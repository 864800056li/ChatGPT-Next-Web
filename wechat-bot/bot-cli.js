const axios = require('axios');
const fs = require('fs');
const path = require('path');

// 配置文件
const CONFIG_PATH = path.join(__dirname, 'config.json');
const LOG_PATH = path.join(__dirname, 'logs', 'bot.log');

// 默认配置
const DEFAULT_CONFIG = {
  autoReply: {
    welcomeMessage: `你好！我是李志强的助手小Q🤖

志强正在忙，我先来接待你～

请告诉我：
1. 你怎么认识志强的？
2. 有什么我可以转达的？

我会第一时间通知他！`,
    keywords: {
      '价格': '关于价格/合作，请留下你的联系方式，志强会亲自联系你。',
      '合作': '感谢关注！请简单介绍你的项目和需求，我转达给志强。',
      '产品': '我们的产品资料正在整理中，请留下邮箱，我发给你。',
      '在吗': '在的！志强忙的时候我会先回复，重要事情我会立刻转达。',
      '你好': '你好！我是小Q，志强的AI助手。有什么可以帮你的？',
      '您好': '您好！我是小Q，志强的AI助手。有什么可以帮你的？',
    },
    defaultReply: '收到！我会转达给志强，他忙完会回复你。'
  },
  groupMonitor: {
    keywords: ['志强', '李总', '合作', '紧急', '小Q'],
    adminWxId: 'filehelper'
  }
};

// 日志
function log(msg) {
  const time = new Date().toLocaleString('zh-CN');
  const logMsg = `[${time}] ${msg}`;
  console.log(logMsg);
  
  const logDir = path.dirname(LOG_PATH);
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }
  fs.appendFileSync(LOG_PATH, logMsg + '\n');
}

// 保存配置
function saveConfig(config) {
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
}

// 加载配置
function loadConfig() {
  if (fs.existsSync(CONFIG_PATH)) {
    return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  }
  saveConfig(DEFAULT_CONFIG);
  return DEFAULT_CONFIG;
}

// 模拟微信机器人（简化版）
// 由于缺少浏览器，先用命令行交互模式
async function interactiveMode() {
  const config = loadConfig();
  
  console.log('\n========================================');
  console.log('🤖 小Q微信助手 - 命令行模式');
  console.log('========================================\n');
  
  console.log('当前配置:');
  console.log('- 自动回复关键词:', Object.keys(config.autoReply.keywords).join(', '));
  console.log('- 群监控关键词:', config.groupMonitor.keywords.join(', '));
  console.log('\n功能:');
  console.log('1. 查看股票简报');
  console.log('2. 生成朋友圈内容');
  console.log('3. 修改欢迎语');
  console.log('4. 修改关键词回复');
  console.log('5. 退出');
  console.log('\n注: 完整微信功能需要安装 Chrome 浏览器');
  console.log('========================================\n');
  
  // 显示今日股票简报
  console.log('📈 今日股票简报:');
  try {
    const report = fs.readFileSync(
      path.join(__dirname, 'logs', `stock-report-${new Date().toISOString().split('T')[0]}.txt`),
      'utf8'
    );
    console.log(report);
  } catch (e) {
    console.log('股票简报尚未生成，运行: node scripts/stock-report.js');
  }
}

// 主函数
async function main() {
  log('小Q助手启动');
  
  // 检查是否有 Chrome
  const hasChrome = fs.existsSync('/Applications/Google Chrome.app') ||
                   fs.existsSync('/Applications/Chromium.app');
  
  if (!hasChrome) {
    log('⚠️ 未检测到 Chrome 浏览器，进入命令行模式');
    await interactiveMode();
    return;
  }
  
  // 有 Chrome，尝试启动完整版
  log('检测到 Chrome，尝试启动完整版...');
  // 这里会调用 bot-wechaty.js
}

main().catch(console.error);
