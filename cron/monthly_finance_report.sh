#!/bin/bash
# 月度财报分析定时任务
# 每月第一个交易日执行

cd /Users/dadaguaijiangjun/.openclaw/workspace

# 获取当前月份
MONTH=$(date +%m)
YEAR=$(date +%Y)

echo "开始执行 ${YEAR}年${MONTH}月 财报分析..."

# 分析重点股票财报
python3 skills/akshare-stock/main.py --query "三房巷 财务指标 最新季报" --platform qq > /tmp/sanfangxiang_report.txt

# 发送给爸爸
# 通过QQ发送结果
echo "财报分析完成，结果已保存"
