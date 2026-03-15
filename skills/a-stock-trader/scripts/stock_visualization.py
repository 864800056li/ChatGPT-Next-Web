#!/usr/bin/env python3
"""
股票数据可视化工具
生成K线图、趋势图、成交量图
"""

import sys
import akshare as ak
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def get_stock_data(symbol, days=60):
    """获取股票历史数据"""
    try:
        # 转换股票代码格式
        if symbol.startswith('6'):
            symbol += '.SH'
        else:
            symbol += '.SZ'
        
        # 获取历史数据
        df = ak.stock_zh_a_hist(symbol=symbol.replace('.SH', '').replace('.SZ', ''), 
                                period="daily",
                                start_date=(datetime.now() - timedelta(days=days)).strftime('%Y%m%d'),
                                end_date=datetime.now().strftime('%Y%m%d'),
                                adjust="qfq")
        return df
    except Exception as e:
        print(f"获取数据失败: {e}")
        return None

def plot_stock_chart(symbol, output_path=None):
    """绘制股票K线图和指标"""
    df = get_stock_data(symbol)
    if df is None or df.empty:
        print("无法获取股票数据")
        return False
    
    # 转换日期
    df['日期'] = pd.to_datetime(df['日期'])
    
    # 创建图表
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), 
                             gridspec_kw={'height_ratios': [3, 1, 1]})
    
    # 1. K线图和均线
    ax1 = axes[0]
    ax1.plot(df['日期'], df['收盘'], label='收盘价', linewidth=2, color='black')
    ax1.plot(df['日期'], df['5日均线'], label='MA5', alpha=0.7, color='blue')
    ax1.plot(df['日期'], df['10日均线'], label='MA10', alpha=0.7, color='orange')
    ax1.plot(df['日期'], df['20日均线'], label='MA20', alpha=0.7, color='green')
    ax1.plot(df['日期'], df['60日均线'], label='MA60', alpha=0.7, color='red')
    
    ax1.set_title(f'{symbol} 股票走势', fontsize=14, fontweight='bold')
    ax1.set_ylabel('价格 (元)')
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # 2. 成交量
    ax2 = axes[1]
    colors = ['red' if df.iloc[i]['收盘'] >= df.iloc[i]['开盘'] else 'green' 
              for i in range(len(df))]
    ax2.bar(df['日期'], df['成交量'], color=colors, alpha=0.6)
    ax2.set_ylabel('成交量')
    ax2.grid(True, alpha=0.3)
    
    # 3. MACD
    ax3 = axes[2]
    exp1 = df['收盘'].ewm(span=12, adjust=False).mean()
    exp2 = df['收盘'].ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    histogram = macd - signal
    
    ax3.plot(df['日期'], macd, label='MACD', color='blue')
    ax3.plot(df['日期'], signal, label='Signal', color='red')
    ax3.bar(df['日期'], histogram, label='Histogram', 
            color=['red' if h >= 0 else 'green' for h in histogram], alpha=0.6)
    ax3.set_ylabel('MACD')
    ax3.set_xlabel('日期')
    ax3.legend(loc='upper left')
    ax3.grid(True, alpha=0.3)
    ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    
    # 格式化日期
    for ax in axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
    
    plt.tight_layout()
    
    # 保存或显示
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"图表已保存: {output_path}")
    else:
        plt.show()
    
    plt.close()
    return True

def calculate_ma(df):
    """计算移动平均线"""
    df['5日均线'] = df['收盘'].rolling(window=5).mean()
    df['10日均线'] = df['收盘'].rolling(window=10).mean()
    df['20日均线'] = df['收盘'].rolling(window=20).mean()
    df['60日均线'] = df['收盘'].rolling(window=60).mean()
    return df

def analyze_trend(symbol):
    """分析股票趋势"""
    df = get_stock_data(symbol, days=60)
    if df is None or df.empty:
        return None
    
    df = calculate_ma(df)
    latest = df.iloc[-1]
    
    # 趋势判断
    trend = {
        'symbol': symbol,
        'name': latest.get('名称', symbol),
        'current_price': latest['收盘'],
        'change_pct': (latest['收盘'] - df.iloc[-2]['收盘']) / df.iloc[-2]['收盘'] * 100,
        'ma5': latest['5日均线'],
        'ma10': latest['10日均线'],
        'ma20': latest['20日均线'],
        'ma60': latest['60日均线'],
        'volume': latest['成交量'],
        'trend_signal': 'unknown'
    }
    
    # 均线多头排列判断
    if latest['5日均线'] > latest['10日均线'] > latest['20日均线'] > latest['60日均线']:
        trend['trend_signal'] = '多头排列（强势）'
    elif latest['5日均线'] < latest['10日均线'] < latest['20日均线'] < latest['60日均线']:
        trend['trend_signal'] = '空头排列（弱势）'
    elif latest['收盘'] > latest['5日均线'] > latest['10日均线']:
        trend['trend_signal'] = '短期强势'
    elif latest['收盘'] < latest['5日均线'] < latest['10日均线']:
        trend['trend_signal'] = '短期弱势'
    else:
        trend['trend_signal'] = '震荡整理'
    
    return trend

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python stock_visualization.py <股票代码> [输出路径]")
        print("示例: python stock_visualization.py 000001 ~/Desktop/000001_chart.png")
        sys.exit(1)
    
    symbol = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"正在生成 {symbol} 的股票图表...")
    
    # 生成图表
    if plot_stock_chart(symbol, output_path):
        # 分析趋势
        trend = analyze_trend(symbol)
        if trend:
            print(f"\n=== {trend['name']} ({symbol}) 趋势分析 ===")
            print(f"当前价格: ¥{trend['current_price']:.2f}")
            print(f"涨跌幅: {trend['change_pct']:+.2f}%")
            print(f"趋势信号: {trend['trend_signal']}")
            print(f"成交量: {trend['volume']:,.0f}")
    else:
        print("生成图表失败")
