#!/bin/bash
# 设置定时任务

echo "🕐 设置定时任务..."

# 股票简报 - 每天 9:00
crontab -l 2>/dev/null | grep -v "stock-report" | crontab -
(crontab -l 2>/dev/null; echo "0 9 * * * cd /Users/dadaguaijiangjun/.openclaw/workspace/wechat-bot && /usr/local/bin/node scripts/stock-report.js >> logs/stock.log 2>&1") | crontab -

# 朋友圈 - 每天 12:00
crontab -l 2>/dev/null | grep -v "post-moment" | crontab -
(crontab -l 2>/dev/null; echo "0 12 * * * cd /Users/dadaguaijiangjun/.openclaw/workspace/wechat-bot && /usr/local/bin/node scripts/post-moment.js >> logs/moment.log 2>&1") | crontab -

echo "✅ 定时任务已设置:"
crontab -l | grep -E "(stock-report|post-moment)"
