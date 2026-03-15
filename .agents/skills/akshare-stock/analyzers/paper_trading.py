#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟盘管理器 - 跟踪虚拟交易和收益
"""
import json
import os
from datetime import datetime, date
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class Trade:
    """交易记录"""
    date: str
    code: str
    name: str
    action: str  # BUY/SELL
    price: float
    shares: int
    amount: float
    reason: str = ""

@dataclass
class Position:
    """持仓"""
    code: str
    name: str
    shares: int
    avg_cost: float
    current_price: float = 0.0
    
    @property
    def market_value(self) -> float:
        return self.shares * self.current_price
    
    @property
    def cost_basis(self) -> float:
        return self.shares * self.avg_cost
    
    @property
    def pnl(self) -> float:
        return self.market_value - self.cost_basis
    
    @property
    def pnl_pct(self) -> float:
        if self.cost_basis == 0:
            return 0
        return (self.pnl / self.cost_basis) * 100

class PaperTrading:
    """模拟盘管理"""
    
    def __init__(self, name: str = "default", initial_capital: float = 1000000.0):
        self.name = name
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.history: List[Dict] = []
        
        # 数据存储路径
        self.data_dir = Path.home() / ".openclaw" / "workspace" / "paper_trading"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.load()
    
    def load(self):
        """加载数据"""
        file_path = self.data_dir / f"{self.name}.json"
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.cash = data.get('cash', self.initial_capital)
                self.initial_capital = data.get('initial_capital', self.initial_capital)
                self.trades = [Trade(**t) for t in data.get('trades', [])]
                self.positions = {p['code']: Position(**p) for p in data.get('positions', [])}
                self.history = data.get('history', [])
    
    def save(self):
        """保存数据"""
        file_path = self.data_dir / f"{self.name}.json"
        data = {
            'name': self.name,
            'initial_capital': self.initial_capital,
            'cash': self.cash,
            'positions': [
                {
                    'code': p.code,
                    'name': p.name,
                    'shares': p.shares,
                    'avg_cost': p.avg_cost,
                    'current_price': p.current_price
                }
                for p in self.positions.values()
            ],
            'trades': [asdict(t) for t in self.trades],
            'history': self.history
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def buy(self, code: str, name: str, price: float, shares: int, reason: str = ""):
        """买入"""
        amount = price * shares
        if amount > self.cash:
            return False, f"资金不足，需要{amount:.2f}，可用{self.cash:.2f}"
        
        self.cash -= amount
        
        if code in self.positions:
            # 加仓，更新成本
            pos = self.positions[code]
            total_cost = pos.cost_basis + amount
            total_shares = pos.shares + shares
            pos.avg_cost = total_cost / total_shares
            pos.shares = total_shares
            pos.name = name
        else:
            # 新建仓位
            self.positions[code] = Position(
                code=code,
                name=name,
                shares=shares,
                avg_cost=price
            )
        
        trade = Trade(
            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            code=code,
            name=name,
            action="BUY",
            price=price,
            shares=shares,
            amount=amount,
            reason=reason
        )
        self.trades.append(trade)
        self.save()
        
        return True, f"买入成功：{name}({code}) {shares}股 @ {price:.2f}"
    
    def sell(self, code: str, price: float, shares: int = None, reason: str = ""):
        """卖出"""
        if code not in self.positions:
            return False, f"没有持仓：{code}"
        
        pos = self.positions[code]
        
        if shares is None or shares >= pos.shares:
            # 清仓
            shares = pos.shares
            sell_amount = price * shares
            pnl = sell_amount - pos.cost_basis
            del self.positions[code]
        else:
            # 部分卖出
            sell_amount = price * shares
            cost = pos.avg_cost * shares
            pnl = sell_amount - cost
            pos.shares -= shares
        
        self.cash += sell_amount
        
        trade = Trade(
            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            code=code,
            name=pos.name,
            action="SELL",
            price=price,
            shares=shares,
            amount=sell_amount,
            reason=reason
        )
        self.trades.append(trade)
        self.save()
        
        return True, f"卖出成功：{pos.name}({code}) {shares}股 @ {price:.2f}，盈亏{pnl:+.2f}"
    
    def update_prices(self, prices: Dict[str, float]):
        """更新持仓价格"""
        for code, price in prices.items():
            if code in self.positions:
                self.positions[code].current_price = price
    
    def get_portfolio_value(self) -> Dict:
        """获取组合价值"""
        positions_value = sum(p.market_value for p in self.positions.values())
        total_value = self.cash + positions_value
        total_return = total_value - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100
        
        return {
            'cash': self.cash,
            'positions_value': positions_value,
            'total_value': total_value,
            'total_return': total_return,
            'total_return_pct': total_return_pct,
            'positions_count': len(self.positions)
        }
    
    def get_report(self) -> str:
        """生成报告"""
        portfolio = self.get_portfolio_value()
        
        lines = [
            f"📊 模拟盘报告 - {self.name}",
            f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            f"💰 初始资金：{self.initial_capital:,.2f}",
            f"💵 可用现金：{portfolio['cash']:,.2f}",
            f"📈 持仓市值：{portfolio['positions_value']:,.2f}",
            f"💎 总资产：{portfolio['total_value']:,.2f}",
            f"📊 总收益：{portfolio['total_return']:+.2f} ({portfolio['total_return_pct']:+.2f}%)",
            "",
            f"📋 持仓明细 ({portfolio['positions_count']}只)："
        ]
        
        for pos in self.positions.values():
            lines.append(
                f"  {pos.name}({pos.code}) {pos.shares}股 "
                f"成本{pos.avg_cost:.2f} 现价{pos.current_price:.2f} "
                f"盈亏{pos.pnl:+.2f}({pos.pnl_pct:+.2f}%)"
            )
        
        if not self.positions:
            lines.append("  (空仓)")
        
        lines.append("")
        lines.append(f"📝 最近交易：")
        for trade in self.trades[-5:]:
            emoji = "🟢" if trade.action == "BUY" else "🔴"
            lines.append(
                f"  {emoji} {trade.date} {trade.name} {trade.action} "
                f"{trade.shares}股 @ {trade.price:.2f}"
            )
        
        return "\n".join(lines)

if __name__ == "__main__":
    # 测试
    pt = PaperTrading("test", 100000)
    print("模拟盘管理器已加载")
    print(pt.get_report())
