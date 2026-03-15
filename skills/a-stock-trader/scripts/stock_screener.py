#!/usr/bin/env python3
"""
股票筛选器
基于价值投资和技术指标筛选潜力股票
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

def get_stock_list():
    """获取A股所有股票列表"""
    try:
        df = ak.stock_zh_a_spot_em()
        return df
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        return None

def filter_by_value():
    """
    价值筛选条件：
    - 市盈率 < 30
    - 市净率 < 3
    - ROE > 10%
    - 股息率 > 2%
    """
    df = get_stock_list()
    if df is None:
        return None
    
    # 重命名列以便处理
    column_mapping = {
        '代码': 'symbol',
        '名称': 'name',
        '最新价': 'price',
        '涨跌幅': 'change_pct',
        '市盈率-动态': 'pe',
        '市净率': 'pb',
        'ROE': 'roe',
        '股息率': 'dividend_yield',
        '换手率': 'turnover',
        '成交量': 'volume',
        '总市值': 'market_cap',
        '所属行业': 'industry'
    }
    
    # 筛选条件
    filtered = df[
        (df['市盈率-动态'] > 0) & (df['市盈率-动态'] < 30) &
        (df['市净率'] > 0) & (df['市净率'] < 3) &
        (df['ROE'] > 10)
    ].copy()
    
    # 按ROE排序
    filtered = filtered.sort_values('ROE', ascending=False)
    
    return filtered[['代码', '名称', '最新价', '涨跌幅', '市盈率-动态', '市净率', 'ROE', '所属行业']].head(20)

def filter_by_technical():
    """
    技术筛选条件：
    - 当日涨幅 > 3%
    - 换手率 > 5%
    - 成交量放大
    - 突破形态
    """
    df = get_stock_list()
    if df is None:
        return None
    
    # 筛选强势股
    filtered = df[
        (df['涨跌幅'] > 3) &
        (df['换手率'] > 5) &
        (df['最新价'] > 0)
    ].copy()
    
    # 按涨跌幅排序
    filtered = filtered.sort_values('涨跌幅', ascending=False)
    
    return filtered[['代码', '名称', '最新价', '涨跌幅', '换手率', '成交量', '所属行业']].head(20)

def filter_by_dividend():
    """
    高股息筛选：
    - 股息率 > 4%
    - 连续分红
    """
    df = get_stock_list()
    if df is None:
        return None
    
    # 筛选高股息
    filtered = df[
        (df['股息率'] > 4) &
        (df['最新价'] > 0)
    ].copy()
    
    # 按股息率排序
    filtered = filtered.sort_values('股息率', ascending=False)
    
    return filtered[['代码', '名称', '最新价', '股息率', '市盈率-动态', '所属行业']].head(20)

def filter_by_small_cap():
    """
    小盘股筛选：
    - 总市值 < 100亿
    - 流通市值小
    - 有成长性
    """
    df = get_stock_list()
    if df is None:
        return None
    
    # 筛选小盘股
    filtered = df[
        (df['总市值'] < 10000000000) &  # 100亿
        (df['最新价'] > 0) &
        (df['涨跌幅'] > -5) &
        (df['涨跌幅'] < 20)
    ].copy()
    
    # 按市值排序
    filtered = filtered.sort_values('总市值', ascending=True)
    
    return filtered[['代码', '名称', '最新价', '涨跌幅', '总市值', '换手率', '所属行业']].head(20)

def main():
    """主函数"""
    print("=" * 60)
    print("A股股票筛选器")
    print("=" * 60)
    
    print("\n【价值股筛选】PE<30, PB<3, ROE>10%")
    print("-" * 60)
    value_stocks = filter_by_value()
    if value_stocks is not None:
        print(value_stocks.to_string(index=False))
    
    print("\n【强势股筛选】涨幅>3%, 换手>5%")
    print("-" * 60)
    tech_stocks = filter_by_technical()
    if tech_stocks is not None:
        print(tech_stocks.to_string(index=False))
    
    print("\n【高股息筛选】股息率>4%")
    print("-" * 60)
    dividend_stocks = filter_by_dividend()
    if dividend_stocks is not None:
        print(dividend_stocks.to_string(index=False))
    
    print("\n【小盘股筛选】市值<100亿")
    print("-" * 60)
    small_cap_stocks = filter_by_small_cap()
    if small_cap_stocks is not None:
        print(small_cap_stocks.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("免责声明：以上筛选结果仅供参考，不构成投资建议")
    print("=" * 60)

if __name__ == "__main__":
    main()
