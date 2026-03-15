const axios = require('axios');
const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
  // wxhelper API 地址
  wxApiBase: 'http://localhost:19089',
  
  // OpenClaw API 地址（用于调用我）
  openclawApi: 'http://localhost:8080/api/v1/message',
  
  // 自动回复配置
  autoReply: {
    // 新好友欢迎语
    welcomeMessage: `你好！我是李志强的助手小Q🤖

志强正在忙，我先来接待你～

请告诉我：
1. 你怎么认识志强的？
2. 有什么我可以转达的？

我会第一时间通知他！`,
    
    // 关键词回复
    keywords: {
      '价格': '关于价格/合作，请留下你的联系方式，志强会亲自联系你。',
      '合作': '感谢关注！请简单介绍你的项目和需求，我转达给志强。',
      '产品': '我们的产品资料正在整理中，请留下邮箱，我发给你。',
      '在吗': '在的！志强忙的时候我会先回复，重要事情我会立刻转达。',
      '你好': '你好！我是小Q，志强的AI助手。有什么可以帮你的？'
    },
    
    // 默认回复
    defaultReply: '收到！我会转达给志强，他忙完会回复你。'
  },
  
  // 群消息监控关键词
  groupMonitor: {
    keywords: ['志强', '李总', '合作', '紧急'],
    forwardTo: 'filehelper' // 转发到文件传输助手
  }
};

// 日志
function log(msg) {
  const time = new Date().toISOString();
  const logMsg = `[${time}] ${msg}`;
  console.log(logMsg);
  fs.appendFileSync(path.join(__dirname, 'logs', 'bot.log'), logMsg + '\n');
}

// 获取消息列表
async function getMessages() {
  try {
    const res = await axios.get(`${CONFIG.wxApiBase}/getMessages`);
    return res.data.data || [];
  } catch (err) {
    log(`获取消息失败: ${err.message}`);
    return [];
  }
}

// 发送消息
async function sendMessage(to, content) {
  try {
    await axios.post(`${CONFIG.wxApiBase}/sendText`, {
      wxid: to,
      msg: content
    });
    log(`发送消息给 ${to}: ${content.substring(0, 50)}...`);
  } catch (err) {
    log(`发送消息失败: ${err.message}`);
  }
}

// 获取好友申请列表
async function getFriendRequests() {
  try {
    const res = await axios.get(`${CONFIG.wxApiBase}/getFriendRequest`);
    return res.data.data || [];
  } catch (err) {
    log(`获取好友申请失败: ${err.message}`);
    return [];
  }
}

// 通过好友申请
async function acceptFriendRequest(v3, v4) {
  try {
    await axios.post(`${CONFIG.wxApiBase}/acceptFriendRequest`, { v3, v4 });
    log(`通过好友申请: ${v3}`);
    return true;
  } catch (err) {
    log(`通过好友申请失败: ${err.message}`);
    return false;
  }
}

// 处理关键词回复
function getKeywordReply(content) {
  for (const [keyword, reply] of Object.entries(CONFIG.autoReply.keywords)) {
    if (content.includes(keyword)) {
      return reply;
    }
  }
  return null;
}

// 处理新消息
async function handleMessage(msg) {
  const { wxid, content, isGroup } = msg;
  
  // 群消息监控
  if (isGroup) {
    for (const keyword of CONFIG.groupMonitor.keywords) {
      if (content.includes(keyword)) {
        await sendMessage(
          CONFIG.groupMonitor.forwardTo,
          `【群监控】${wxid}: ${content}`
        );
        log(`群关键词触发: ${keyword}`);
      }
    }
    return;
  }
  
  // 私聊自动回复
  const keywordReply = getKeywordReply(content);
  if (keywordReply) {
    await sendMessage(wxid, keywordReply);
  } else {
    // 非关键词，默认回复
    await sendMessage(wxid, CONFIG.autoReply.defaultReply);
  }
  
  // 通知我（小Q）
  notifyMe(`新消息来自 ${wxid}: ${content}`);
}

// 通知我
async function notifyMe(content) {
  try {
    await axios.post(CONFIG.openclawApi, {
      message: content,
      channel: 'feishu'
    });
  } catch (err) {
    log(`通知失败: ${err.message}`);
  }
}

// 处理好友申请
async function handleFriendRequests() {
  const requests = await getFriendRequests();
  
  for (const req of requests) {
    const { v3, v4, wxid } = req;
    
    // 通过申请
    const accepted = await acceptFriendRequest(v3, v4);
    
    if (accepted) {
      // 等待一下确保好友添加成功
      await new Promise(r => setTimeout(r, 2000));
      
      // 发送欢迎语
      await sendMessage(wxid, CONFIG.autoReply.welcomeMessage);
      
      // 通知我
      notifyMe(`🎉 新好友: ${wxid}`);
    }
  }
}

// 发朋友圈
async function postMoment(content, images = []) {
  try {
    // wxhelper 发朋友圈接口
    await axios.post(`${CONFIG.wxApiBase}/postMoment`, {
      content,
      images
    });
    log(`发朋友圈: ${content.substring(0, 50)}...`);
    return true;
  } catch (err) {
    log(`发朋友圈失败: ${err.message}`);
    return false;
  }
}

// 主循环
async function main() {
  log('🤖 小Q微信助手启动...');
  
  // 确保日志目录存在
  if (!fs.existsSync('./logs')) {
    fs.mkdirSync('./logs', { recursive: true });
  }
  
  // 每分钟检查一次
  setInterval(async () => {
    try {
      // 处理好友申请
      await handleFriendRequests();
      
      // 处理新消息
      const messages = await getMessages();
      for (const msg of messages) {
        await handleMessage(msg);
      }
    } catch (err) {
      log(`主循环错误: ${err.message}`);
    }
  }, 60000);
  
  log('✅ 运行中...');
}

// 导出函数供其他模块使用
module.exports = {
  postMoment,
  sendMessage,
  CONFIG
};

// 直接运行
if (require.main === module) {
  main();
}
