const axios = require('axios');

// 使用新浪财经 API (国内可用)
async function getStockPriceSina(code) {
  try {
    // 转换代码格式
    let sinaCode = code;
    if (code.endsWith('.SS')) {
      sinaCode = 'sh' + code.replace('.SS', '');
    } else if (code.endsWith('.SZ')) {
      sinaCode = 'sz' + code.replace('.SZ', '');
    } else if (code.endsWith('.HK')) {
      sinaCode = 'hk' + code.replace('.HK', '');
    } else {
      sinaCode = 'gb_' + code.toLowerCase();
    }
    
    const url = `https://hq.sinajs.cn/list=${sinaCode}`;
    const res = await axios.get(url, {
      headers: {
        'Referer': 'https://finance.sina.com.cn',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
      },
      timeout: 10000,
      responseType: 'text'
    });
    
    // 解析返回数据
    const match = res.data.match(/"([^"]+)"/);
    if (!match) return null;
    
    const parts = match[1].split(',');
    if (parts.length < 5) return null;
    
    // 根据不同市场解析
    let name, price, prevClose, change, changePercent;
    
    if (code.endsWith('.HK')) {
      // 港股格式
      name = parts[1];
      price = parseFloat(parts[6]);
      prevClose = parseFloat(parts[3]);
    } else if (code.startsWith('0') || code.startsWith('6')) {
      // A股格式
      name = parts[0];
      price = parseFloat(parts[3]);
      prevClose = parseFloat(parts[2]);
    } else {
      // 美股格式
      name = parts[0];
      price = parseFloat(parts[1]);
      prevClose = parseFloat(parts[26]);
    }
    
    change = price - prevClose;
    changePercent = (change / prevClose) * 100;
    
    return {
      name,
      price: price.toFixed(2),
      change: change.toFixed(2),
      changePercent: changePercent.toFixed(2)
    };
  } catch (err) {
    console.error(`获取 ${code} 失败:`, err.message);
    return null;
  }
}

// 股票列表
const STOCKS = [
  { code: 'AAPL', name: '苹果' },
  { code: 'TSLA', name: '特斯拉' },
  { code: 'NVDA', name: '英伟达' },
  { code: 'MSFT', name: '微软' },
  { code: 'BABA', name: '阿里巴巴' },
  { code: '00700.HK', name: '腾讯控股' },
  { code: '600519.SS', name: '贵州茅台' },
  { code: '000001.SZ', name: '平安银行' }
];

// 生成简报
async function generateReport() {
  const now = new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
  let report = `📈 股票简报 (${now})\n\n`;
  
  report += `【美股】\n`;
  for (const stock of STOCKS.slice(0, 5)) {
    const data = await getStockPriceSina(stock.code);
    if (data) {
      const emoji = parseFloat(data.change) >= 0 ? '🟢' : '🔴';
      report += `${emoji} ${stock.name}: $${data.price} (${data.change > 0 ? '+' : ''}${data.change}, ${data.changePercent}%)\n`;
    } else {
      report += `⚪ ${stock.name}: 获取失败\n`;
    }
    await new Promise(r => setTimeout(r, 300));
  }
  
  report += `\n【港股/A股】\n`;
  for (const stock of STOCKS.slice(5)) {
    const data = await getStockPriceSina(stock.code);
    if (data) {
      const emoji = parseFloat(data.change) >= 0 ? '🟢' : '🔴';
      const currency = stock.code.endsWith('.HK') ? 'HK$' : '¥';
      report += `${emoji} ${data.name}: ${currency}${data.price} (${data.change > 0 ? '+' : ''}${data.change}, ${data.changePercent}%)\n`;
    } else {
      report += `⚪ ${stock.name}: 获取失败\n`;
    }
    await new Promise(r => setTimeout(r, 300));
  }
  
  return report;
}

// 主函数
async function main() {
  console.log('正在获取股票数据...\n');
  const report = await generateReport();
  console.log(report);
  
  // 保存到文件
  const fs = require('fs');
  const path = require('path');
  const logDir = path.join(__dirname, '..', 'logs');
  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }
  
  const date = new Date().toISOString().split('T')[0];
  fs.writeFileSync(path.join(logDir, `stock-report-${date}.txt`), report);
  
  console.log('✅ 简报已保存到 logs/ 目录');
}

// 直接运行
main().catch(console.error);
