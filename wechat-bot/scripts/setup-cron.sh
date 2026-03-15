#!/bin/bash
# 定时发朋友圈脚本

# 设置时间（每天 8:00, 12:00, 18:00 随机选一个时间点）
HOURS=(8 12 18)
RANDOM_HOUR=${HOURS[$RANDOM % ${#HOURS[@]}]}
RANDOM_MINUTE=$((RANDOM % 60))

# 写入 crontab
CRON_JOB="$RANDOM_MINUTE $RANDOM_HOUR * * * cd /Users/dadaguaijiangjun/.openclaw/workspace/wechat-bot && /usr/local/bin/node scripts/post-moment.js >> logs/moment.log 2>&1"

# 先删除旧的定时任务
(crontab -l 2>/dev/null | grep -v "post-moment.js") | crontab -

# 添加新的
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

echo "✅ 定时任务已设置: 每天 $RANDOM_HOUR:$RANDOM_MINUTE 发朋友圈"
echo "当前 crontab:"
crontab -l | grep post-moment
