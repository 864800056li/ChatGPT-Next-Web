#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股实时行情获取
大大怪将军为爸爸定制
"""

import sys
import akshare as ak
import pandas as pd
from datetime import datetime

def get_realtime_quote(code):
    """获取个股实时行情"""
    try:
        # 获取实时行情
        df = ak.stock_zh_a_spot_em()
        
        # 查找指定股票
        stock = df[df['代码'] == code]
        
        if stock.empty:
            print(f"❌ 未找到股票: {code}")
            return
        
        # 提取关键信息
        name = stock['名称'].values[0]
        price = stock['最新价'].values[0]
        change_pct = stock['涨跌幅'].values[0]
        change = stock['涨跌额'].values[0]
        volume = stock['成交量'].values[0]
        amount = stock['成交额'].values[0]
        
        # 格式化输出
        print(f"\n{'='*60}")
        print(f"📊 {name} ({code})")
        print(f"🕒 {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")
        print(f"💰 最新价: {price}")
        print(f"📈 涨跌幅: {change_pct}%")
        print(f"📊 涨跌额: {change}")
        print(f"📦 成交量: {volume/10000:.2f}万手")
        print(f"💵 成交额: {amount/10000:.2f}万元")
        print(f"{'='*60}\n")
        
        # 判断涨跌
        if change_pct > 0:
            print("🔴 上涨")
        elif change_pct < 0:
            print("🟢 下跌")
        else:
            print("⚪ 平盘")
            
    except Exception as e:
        print(f"❌ 获取行情失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python get_realtime_quote.py <股票代码>")
        print("示例: python get_realtime_quote.py 600519")
        sys.exit(1)
    
    code = sys.argv[1]
    get_realtime_quote(code)
