#!/usr/bin/env python3
"""
投资组合跟踪器
记录持仓、计算盈亏、生成报告
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# 投资组合数据文件
PORTFOLIO_FILE = os.path.expanduser("~/.openclaw/workspace/skills/a-stock-trader/data/portfolio.json")
TRANSACTION_FILE = os.path.expanduser("~/.openclaw/workspace/skills/a-stock-trader/data/transactions.json")

def ensure_data_dir():
    """确保数据目录存在"""
    data_dir = os.path.dirname(PORTFOLIO_FILE)
    os.makedirs(data_dir, exist_ok=True)

def load_portfolio():
    """加载投资组合"""
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "cash": 10000.0,  # 初始资金
        "positions": {},  # 持仓
        "total_value": 10000.0,
        "last_update": datetime.now().isoformat()
    }

def save_portfolio(portfolio):
    """保存投资组合"""
    ensure_data_dir()
    portfolio["last_update"] = datetime.now().isoformat()
    with open(PORTFOLIO_FILE, 'w', encoding='utf-8') as f:
        json.dump(portfolio, f, ensure_ascii=False, indent=2)

def load_transactions():
    """加载交易记录"""
    if os.path.exists(TRANSACTION_FILE):
        with open(TRANSACTION_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_transaction(transaction):
    """保存交易记录"""
    ensure_data_dir()
    transactions = load_transactions()
    transaction["timestamp"] = datetime.now().isoformat()
    transactions.append(transaction)
    with open(TRANSACTION_FILE, 'w', encoding='utf-8') as f:
        json.dump(transactions, f, ensure_ascii=False, indent=2)

def buy_stock(symbol, name, price, shares):
    """买入股票"""
    portfolio = load_portfolio()
    
    # 计算成本
    cost = price * shares
    commission = max(cost * 0.0003, 5)  # 佣金，最低5元
    total_cost = cost + commission
    
    # 检查资金
    if total_cost > portfolio["cash"]:
        return False, f"资金不足，需要¥{total_cost:.2f}，可用¥{portfolio['cash']:.2f}"
    
    # 更新持仓
    if symbol not in portfolio["positions"]:
        portfolio["positions"][symbol] = {
            "name": name,
            "shares": 0,
            "avg_cost": 0,
            "total_cost": 0
        }
    
    position = portfolio["positions"][symbol]
    old_shares = position["shares"]
    old_cost = position["total_cost"]
    
    position["shares"] += shares
    position["total_cost"] += total_cost
    position["avg_cost"] = position["total_cost"] / position["shares"]
    
    # 更新现金
    portfolio["cash"] -= total_cost
    
    # 保存
    save_portfolio(portfolio)
    save_transaction({
        "type": "buy",
        "symbol": symbol,
        "name": name,
        "price": price,
        "shares": shares,
        "commission": commission,
        "total": total_cost
    })
    
    return True, f"买入成功！{name}({symbol}) {shares}股 @ ¥{price:.2f}，佣金¥{commission:.2f}"

def sell_stock(symbol, price, shares):
    """卖出股票"""
    portfolio = load_portfolio()
    
    if symbol not in portfolio["positions"]:
        return False, f"未持有股票 {symbol}"
    
    position = portfolio["positions"][symbol]
    if shares > position["shares"]:
        return False, f"持仓不足，持有{position['shares']}股，尝试卖出{shares}股"
    
    # 计算收入
    revenue = price * shares
    commission = max(revenue * 0.0003, 5)  # 佣金
    stamp_tax = revenue * 0.001  # 印花税
    total_revenue = revenue - commission - stamp_tax
    
    # 计算盈亏
    cost_basis = position["avg_cost"] * shares
    profit = total_revenue - cost_basis
    profit_pct = (profit / cost_basis) * 100
    
    # 更新持仓
    position["shares"] -= shares
    position["total_cost"] = position["avg_cost"] * position["shares"]
    
    if position["shares"] == 0:
        del portfolio["positions"][symbol]
    
    # 更新现金
    portfolio["cash"] += total_revenue
    
    # 保存
    save_portfolio(portfolio)
    save_transaction({
        "type": "sell",
        "symbol": symbol,
        "name": position.get("name", symbol),
        "price": price,
        "shares": shares,
        "commission": commission,
        "stamp_tax": stamp_tax,
        "total": total_revenue,
        "profit": profit,
        "profit_pct": profit_pct
    })
    
    profit_str = f"盈利¥{profit:.2f}(+{profit_pct:.2f}%)" if profit > 0 else f"亏损¥{abs(profit):.2f}({profit_pct:.2f}%)"
    return True, f"卖出成功！{position.get('name', symbol)}({symbol}) {shares}股 @ ¥{price:.2f}，{profit_str}"

def get_portfolio_summary():
    """获取投资组合摘要"""
    portfolio = load_portfolio()
    
    summary = {
        "cash": portfolio["cash"],
        "positions_count": len(portfolio["positions"]),
        "positions": []
    }
    
    total_market_value = portfolio["cash"]
    total_cost = portfolio["cash"]
    
    for symbol, position in portfolio["positions"].items():
        # 这里应该获取实时价格，简化处理
        market_value = position["total_cost"]  # 用成本代替，实际需要实时价格
        summary["positions"].append({
            "symbol": symbol,
            "name": position["name"],
            "shares": position["shares"],
            "avg_cost": position["avg_cost"],
            "market_value": market_value
        })
        total_market_value += market_value
        total_cost += position["total_cost"]
    
    summary["total_value"] = total_market_value
    summary["total_return"] = total_market_value - 10000.0
    summary["total_return_pct"] = ((total_market_value - 10000.0) / 10000.0) * 100
    
    return summary

def print_portfolio():
    """打印投资组合"""
    portfolio = load_portfolio()
    summary = get_portfolio_summary()
    
    print("=" * 70)
    print("投资组合报告")
    print("=" * 70)
    print(f"\n💰 现金: ¥{portfolio['cash']:.2f}")
    print(f"📊 持仓数量: {len(portfolio['positions'])} 只股票")
    print(f"💵 总资产: ¥{summary['total_value']:.2f}")
    
    return_pct = summary['total_return_pct']
    return_emoji = "📈" if return_pct >= 0 else "📉"
    print(f"{return_emoji} 总收益: ¥{summary['total_return']:.2f} ({return_pct:+.2f}%)")
    
    if portfolio["positions"]:
        print("\n" + "-" * 70)
        print("持仓明细:")
        print("-" * 70)
        print(f"{'代码':<10} {'名称':<12} {'持仓':<8} {'成本价':<10} {'市值':<12}")
        print("-" * 70)
        for pos in summary["positions"]:
            print(f"{pos['symbol']:<10} {pos['name']:<12} {pos['shares']:<8} ¥{pos['avg_cost']:<9.2f} ¥{pos['market_value']:<11.2f}")
    
    print("\n" + "=" * 70)

def print_transactions(limit=10):
    """打印最近交易记录"""
    transactions = load_transactions()
    
    print("=" * 70)
    print(f"最近 {min(limit, len(transactions))} 笔交易记录")
    print("=" * 70)
    
    if not transactions:
        print("暂无交易记录")
        return
    
    for t in reversed(transactions[-limit:]):
        time_str = t['timestamp'][:19].replace('T', ' ')
        action = "买入" if t['type'] == 'buy' else "卖出"
        emoji = "🟢" if t['type'] == 'buy' else "🔴"
        print(f"{emoji} [{time_str}] {action} {t['name']}({t['symbol']}) {t['shares']}股 @ ¥{t['price']:.2f}")
        if 'profit' in t:
            profit_str = f"盈利¥{t['profit']:.2f}" if t['profit'] > 0 else f"亏损¥{abs(t['profit']):.2f}"
            print(f"   盈亏: {profit_str}")
    
    print("=" * 70)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  python portfolio_tracker.py show          # 显示投资组合")
        print("  python portfolio_tracker.py transactions  # 显示交易记录")
        print("  python portfolio_tracker.py buy <代码> <名称> <价格> <数量>")
        print("  python portfolio_tracker.py sell <代码> <价格> <数量>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "show":
        print_portfolio()
    elif cmd == "transactions":
        print_transactions()
    elif cmd == "buy" and len(sys.argv) >= 6:
        success, msg = buy_stock(sys.argv[2], sys.argv[3], float(sys.argv[4]), int(sys.argv[5]))
        print(msg)
    elif cmd == "sell" and len(sys.argv) >= 5:
        success, msg = sell_stock(sys.argv[2], float(sys.argv[3]), int(sys.argv[4]))
        print(msg)
    else:
        print("命令格式错误")
