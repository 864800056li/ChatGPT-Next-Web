const { WechatyBuilder } = require('wechaty');
const PuppetWechat = require('wechaty-puppet-wechat');
const fs = require('fs');
const path = require('path');

// 配置
const CONFIG = {
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
      '你好': '你好！我是小Q，志强的AI助手。有什么可以帮你的？',
      '您好': '您好！我是小Q，志强的AI助手。有什么可以帮你的？',
      'hi': 'Hi there! 我是小Q，志强的AI助手。',
      'hello': 'Hello! 我是小Q，志强的AI助手。'
    },

    // 默认回复
    defaultReply: '收到！我会转达给志强，他忙完会回复你。'
  },

  // 群消息监控关键词
  groupMonitor: {
    keywords: ['志强', '李总', '合作', '紧急', '小Q'],
    adminWxId: 'filehelper' // 转发到文件传输助手
  }
};

// 日志
function log(msg) {
  const time = new Date().toLocaleString('zh-CN');
  const logMsg = `[${time}] ${msg}`;
  console.log(logMsg);

  const logDir = path.join(__dirname, 'logs');
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }
  fs.appendFileSync(path.join(logDir, 'bot.log'), logMsg + '\n');
}

// 处理关键词回复
function getKeywordReply(content) {
  if (!content) return null;

  for (const [keyword, reply] of Object.entries(CONFIG.autoReply.keywords)) {
    if (content.toLowerCase().includes(keyword.toLowerCase())) {
      return reply;
    }
  }
  return null;
}

// 主函数
async function main() {
  log('🤖 小Q微信助手启动中...');

  // 创建机器人 - 使用系统 Chrome
  const bot = WechatyBuilder.build({
    name: 'xiaoq-wechat-bot',
    puppet: 'wechaty-puppet-wechat',
    puppetOptions: {
      executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    }
  });

  // 扫码登录
  bot.on('scan', (qrcode, status) => {
    const qrUrl = `https://wechaty.js.org/qrcode/${encodeURIComponent(qrcode)}`;
    log(`📱 请扫码登录: ${qrUrl}`);
    console.log('\n========================================');
    console.log('请访问上面的链接，用微信扫码登录');
    console.log('或者复制链接到浏览器打开二维码');
    console.log('========================================\n');
  });

  // 登录成功
  bot.on('login', (user) => {
    log(`✅ 登录成功: ${user.name()}`);
    log('🚀 机器人开始运行...');
  });

  // 登出
  bot.on('logout', (user) => {
    log(`👋 已登出: ${user.name()}`);
  });

  // 收到消息
  bot.on('message', async (msg) => {
    const contact = msg.talker();
    const content = msg.text();
    const room = msg.room();

    // 跳过自己发的消息
    if (msg.self()) return;

    // 群消息处理
    if (room) {
      try {
        const topic = await room.topic();
        log(`[群:${topic}] ${contact.name()}: ${content}`);

        // 监控关键词
        for (const keyword of CONFIG.groupMonitor.keywords) {
          if (content.includes(keyword)) {
            const alert = `【群监控】群"${topic}" 中 ${contact.name()} 提到"${keyword}": ${content}`;
            log(`🔔 ${alert}`);

            // 转发到文件传输助手
            const fileHelper = await bot.Contact.find({ name: '文件传输助手' });
            if (fileHelper) {
              await fileHelper.say(alert);
            }
          }
        }
      } catch (err) {
        log(`群消息处理错误: ${err.message}`);
      }
      return;
    }

    // 私聊消息
    log(`[私聊] ${contact.name()}: ${content}`);

    // 关键词回复
    const reply = getKeywordReply(content);
    if (reply) {
      await msg.say(reply);
      log(`🤖 回复: ${reply.substring(0, 30)}...`);
    } else {
      // 默认回复
      await msg.say(CONFIG.autoReply.defaultReply);
      log(`🤖 默认回复`);
    }
  });

  // 好友申请
  bot.on('friendship', async (friendship) => {
    const contact = friendship.contact();
    log(`📝 收到好友申请: ${contact.name()}`);

    try {
      // 自动通过好友申请
      await friendship.accept();
      log(`✅ 已通过 ${contact.name()} 的好友申请`);

      // 等待一下再发欢迎语
      await new Promise(r => setTimeout(r, 3000));

      // 发送欢迎语
      await contact.say(CONFIG.autoReply.welcomeMessage);
      log(`💬 已发送欢迎语给 ${contact.name()}`);

      // 通知我
      const fileHelper = await bot.Contact.find({ name: '文件传输助手' });
      if (fileHelper) {
        await fileHelper.say(`🎉 新好友: ${contact.name()}`);
      }
    } catch (err) {
      log(`❌ 处理好友申请失败: ${err.message}`);
    }
  });

  // 启动
  await bot.start();
}

// 发朋友圈功能（导出供其他脚本调用）
async function postMoment(bot, content) {
  try {
    // WeChaty 网页版不支持直接发朋友圈
    // 需要通过文件传输助手提醒自己手动发
    const fileHelper = await bot.Contact.find({ name: '文件传输助手' });
    if (fileHelper) {
      await fileHelper.say(`【朋友圈提醒】\n请手动发送以下内容到朋友圈：\n\n${content}`);
      log(`📱 朋友圈提醒已发送`);
      return true;
    }
  } catch (err) {
    log(`❌ 发朋友圈提醒失败: ${err.message}`);
    return false;
  }
}

// 导出
module.exports = { postMoment };

// 直接运行
main().catch(err => {
  log(`❌ 错误: ${err.message}`);
  console.error(err);
  process.exit(1);
});
