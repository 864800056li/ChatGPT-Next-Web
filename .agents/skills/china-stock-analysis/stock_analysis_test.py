#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股基本面分析测试脚本
大大怪将军为爸爸定制
"""

import akshare as ak
import pandas as pd
from datetime import datetime

def get_stock_basic_info(code):
    """获取股票基本信息"""
    try:
        # 获取个股信息
        df = ak.stock_individual_info_em(symbol=code)
        return df
    except Exception as e:
        return f"获取基本信息失败: {e}"

def get_financial_data(code):
    """获取财务数据"""
    try:
        # 获取利润表数据
        df = ak.stock_financial_report_sina(stock=code, symbol='利润表')
        # 获取最近5条数据
        df = df.head(5)
        # 选择关键列
        key_cols = ['报告日', '营业总收入', '净利润', '基本每股收益']
        available_cols = [col for col in key_cols if col in df.columns]
        if available_cols:
            return df[available_cols]
        return df
    except Exception as e:
        return f"获取财务数据失败: {e}"

def get_valuation_data(code):
    """获取估值数据"""
    try:
        # 获取市盈率、市净率等
        df = ak.stock_a_pe(symbol=code)
        return df
    except Exception as e:
        return f"获取估值数据失败: {e}"

def analyze_stock(code):
    """综合分析一只股票"""
    print(f"\n{'='*60}")
    print(f"📊 股票分析报告: {code}")
    print(f"🕒 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # 1. 基本信息
    print("【基本信息】")
    basic = get_stock_basic_info(code)
    if isinstance(basic, pd.DataFrame):
        print(basic.to_string(index=False))
    else:
        print(basic)
    
    print("\n" + "-"*60 + "\n")
    
    # 2. 财务数据
    print("【财务指标 (最近5年)】")
    financial = get_financial_data(code)
    if isinstance(financial, pd.DataFrame):
        # 显示关键列
        key_cols = ['年度', '营业收入', '净利润', 'ROE', '毛利率', '净利率']
        available_cols = [col for col in key_cols if col in financial.columns]
        if available_cols:
            print(financial[available_cols].to_string(index=False))
        else:
            print(financial.to_string(index=False))
    else:
        print(financial)
    
    print("\n" + "-"*60 + "\n")
    
    # 3. 估值数据
    print("【估值数据】")
    valuation = get_valuation_data(code)
    if isinstance(valuation, pd.DataFrame):
        print(valuation.to_string(index=False))
    else:
        print(valuation)
    
    print(f"\n{'='*60}")
    print("💡 提示：以上数据仅供参考，不构成投资建议")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python stock_analysis_test.py <股票代码>")
        print("示例: python stock_analysis_test.py 600519")
        print("      python stock_analysis_test.py 000858")
        sys.exit(1)
    
    code = sys.argv[1]
    analyze_stock(code)
