#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
量化策略回测系统 - 验证交易策略的历史表现
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

@dataclass
class BacktestResult:
    """回测结果"""
    strategy_name: str
    start_date: str
    end_date: str
    initial_capital: float
    final_value: float
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_profit_per_trade: float
    equity_curve: List[Dict]
    trades: List[Dict]

class StrategyBacktester:
    """策略回测器"""
    
    def __init__(self, initial_capital: float = 1000000.0):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Dict] = {}
        self.trades: List[Dict] = []
        self.equity_curve: List[Dict] = []
        
    def run_backtest(self, 
                     df: pd.DataFrame, 
                     strategy_func,
                     start_date: str = None,
                     end_date: str = None) -> BacktestResult:
        """
        运行回测
        
        Args:
            df: 股票数据，包含open, high, low, close, volume
            strategy_func: 策略函数，返回信号
            start_date: 回测开始日期
            end_date: 回测结束日期
        """
        # 过滤日期范围
        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]
        
        if len(df) < 60:
            raise ValueError("数据不足，至少需要60个交易日")
        
        # 遍历每个交易日
        for i in range(60, len(df)):
            current_date = df.index[i]
            current_data = df.iloc[:i+1]
            
            # 获取策略信号
            signal = strategy_func(current_data)
            
            # 执行交易
            self._execute_signal(signal, current_date, df.iloc[i])
            
            # 记录权益曲线
            self._record_equity(current_date, df.iloc[i])
        
        # 计算回测指标
        return self._calculate_metrics(df.index[0], df.index[-1])
    
    def _execute_signal(self, signal: Dict, date: datetime, bar: pd.Series):
        """执行交易信号"""
        if not signal or signal.get('action') == 'hold':
            return
        
        symbol = signal.get('symbol', 'unknown')
        action = signal.get('action')
        shares = signal.get('shares', 0)
        price = bar['close']
        
        if action == 'buy' and shares > 0:
            cost = price * shares * 1.00025  # 含佣金
            if cost <= self.cash:
                self.cash -= cost
                if symbol in self.positions:
                    # 加仓
                    pos = self.positions[symbol]
                    total_cost = pos['cost'] + cost
                    total_shares = pos['shares'] + shares
                    pos['cost'] = total_cost
                    pos['shares'] = total_shares
                    pos['avg_price'] = total_cost / total_shares
                else:
                    # 新建仓位
                    self.positions[symbol] = {
                        'shares': shares,
                        'avg_price': price,
                        'cost': cost
                    }
                
                self.trades.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'action': 'buy',
                    'symbol': symbol,
                    'shares': shares,
                    'price': price,
                    'cost': cost
                })
        
        elif action == 'sell' and symbol in self.positions:
            pos = self.positions[symbol]
            if shares >= pos['shares']:
                shares = pos['shares']
            
            proceeds = price * shares * 0.99875  # 含佣金和印花税
            self.cash += proceeds
            
            # 计算盈亏
            cost_basis = pos['avg_price'] * shares
            pnl = proceeds - cost_basis
            
            pos['shares'] -= shares
            if pos['shares'] <= 0:
                del self.positions[symbol]
            
            self.trades.append({
                'date': date.strftime('%Y-%m-%d'),
                'action': 'sell',
                'symbol': symbol,
                'shares': shares,
                'price': price,
                'proceeds': proceeds,
                'pnl': pnl
            })
    
    def _record_equity(self, date: datetime, bar: pd.Series):
        """记录权益曲线"""
        positions_value = sum(
            pos['shares'] * bar['close'] 
            for pos in self.positions.values()
        )
        total_value = self.cash + positions_value
        
        self.equity_curve.append({
            'date': date.strftime('%Y-%m-%d'),
            'cash': self.cash,
            'positions_value': positions_value,
            'total_value': total_value,
            'return': (total_value - self.initial_capital) / self.initial_capital
        })
    
    def _calculate_metrics(self, start_date: datetime, end_date: datetime) -> BacktestResult:
        """计算回测指标"""
        if not self.equity_curve:
            raise ValueError("没有交易记录")
        
        final_value = self.equity_curve[-1]['total_value']
        total_return = (final_value - self.initial_capital) / self.initial_capital
        
        # 计算年化收益
        days = (end_date - start_date).days
        years = days / 365
        annual_return = (1 + total_return) ** (1/years) - 1 if years > 0 else 0
        
        # 计算最大回撤
        max_drawdown = self._calculate_max_drawdown()
        
        # 计算夏普比率
        sharpe_ratio = self._calculate_sharpe_ratio()
        
        # 统计交易
        winning_trades = [t for t in self.trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in self.trades if t.get('pnl', 0) < 0]
        
        total_pnl = sum(t.get('pnl', 0) for t in self.trades if 'pnl' in t)
        avg_profit = total_pnl / len(self.trades) if self.trades else 0
        
        # 盈亏比
        total_profit = sum(t['pnl'] for t in winning_trades)
        total_loss = abs(sum(t['pnl'] for t in losing_trades))
        profit_factor = total_profit / total_loss if total_loss > 0 else float('inf')
        
        return BacktestResult(
            strategy_name='Technical Strategy',
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            initial_capital=self.initial_capital,
            final_value=final_value,
            total_return=total_return,
            annual_return=annual_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            win_rate=len(winning_trades) / len(self.trades) if self.trades else 0,
            profit_factor=profit_factor,
            total_trades=len(self.trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            avg_profit_per_trade=avg_profit,
            equity_curve=self.equity_curve,
            trades=self.trades
        )
    
    def _calculate_max_drawdown(self) -> float:
        """计算最大回撤"""
        if not self.equity_curve:
            return 0
        
        values = [e['total_value'] for e in self.equity_curve]
        peak = values[0]
        max_dd = 0
        
        for value in values:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            max_dd = max(max_dd, dd)
        
        return max_dd
    
    def _calculate_sharpe_ratio(self) -> float:
        """计算夏普比率"""
        if len(self.equity_curve) < 2:
            return 0
        
        returns = []
        for i in range(1, len(self.equity_curve)):
            r = (self.equity_curve[i]['total_value'] - self.equity_curve[i-1]['total_value']) / self.equity_curve[i-1]['total_value']
            returns.append(r)
        
        if not returns:
            return 0
        
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        
        # 假设无风险利率为3%
        risk_free_rate = 0.03 / 252  # 日度
        
        if std_return == 0:
            return 0
        
        sharpe = (avg_return - risk_free_rate) / std_return * np.sqrt(252)
        return sharpe

# 示例策略函数
def example_ma_strategy(df: pd.DataFrame) -> Dict:
    """
    示例：双均线策略
    金叉买入，死叉卖出
    """
    if len(df) < 20:
        return {'action': 'hold'}
    
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    ma20 = df['close'].rolling(20).mean().iloc[-1]
    
    # 获取当前持仓（简化处理）
    # 实际应该跟踪持仓状态
    
    if ma5 > ma20:
        return {
            'action': 'buy',
            'symbol': 'stock',
            'shares': 100
        }
    elif ma5 < ma20:
        return {
            'action': 'sell',
            'symbol': 'stock',
            'shares': 100
        }
    
    return {'action': 'hold'}

if __name__ == "__main__":
    print("量化策略回测系统已加载")
