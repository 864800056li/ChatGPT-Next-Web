#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股实时行情查询工具
大大怪将军为爸爸定制
"""

import sys
import akshare as ak
import pandas as pd
from datetime import datetime

def get_index_spot():
    """获取大盘指数"""
    try:
        df = ak.stock_zh_index_spot_sina()
        # 主要指数
        main_indices = ['上证指数', '深证成指', '创业板指', '沪深300', '上证50', '科创50']
        result = df[df['name'].isin(main_indices)]
        return result[['code', 'name', 'price', 'change', 'change_percent', 'volume', 'amount']]
    except Exception as e:
        return f"获取大盘指数失败: {e}"

def get_stock_spot(symbol=None):
    """获取个股行情"""
    try:
        df = ak.stock_zh_a_spot_em()
        if symbol:
            # 支持代码或名称查询
            if symbol.isdigit():
                result = df[df['代码'] == symbol]
            else:
                result = df[df['名称'].str.contains(symbol, na=False)]
            if result.empty:
                return f"未找到股票: {symbol}"
            return result[['代码', '名称', '最新价', '涨跌幅', '涨跌额', '成交量', '成交额', '换手率', '市盈率']]
        else:
            # 返回涨幅前10
            return df.nlargest(10, '涨跌幅')[['代码', '名称', '最新价', '涨跌幅', '成交额']]
    except Exception as e:
        return f"获取个股行情失败: {e}"

def format_output(data, title):
    """格式化输出"""
    if isinstance(data, str):
        return f"❌ {data}"
    
    output = [f"📊 {title}", f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]
    
    for _, row in data.iterrows():
        line = " | ".join([f"{col}: {row[col]}" for col in data.columns])
        output.append(line)
    
    return "\n".join(output)

def main():
    if len(sys.argv) < 2:
        print("用法: python stock_query.py [大盘|个股代码/名称]")
        print("示例:")
        print("  python stock_query.py 大盘")
        print("  python stock_query.py 600519")
        print("  python stock_query.py 茅台")
        return
    
    query = sys.argv[1]
    
    if query == "大盘":
        data = get_index_spot()
        print(format_output(data, "A股大盘指数"))
    else:
        data = get_stock_spot(query)
        print(format_output(data, f"股票查询: {query}"))

if __name__ == "__main__":
    main()
