#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合交易分析入口 - 整合所有分析模块
"""
import sys
import json
import argparse
from pathlib import Path

# 添加技能路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from adapters import AkshareAdapter
from analyzers.trading_analyzer import SignalGenerator, SignalType
from analyzers.paper_trading import PaperTrading
from analyzers.alert_manager import AlertManager

class TradingAnalyzer:
    """交易分析主类"""
    
    def __init__(self):
        self.adapter = AkshareAdapter()
        self.signal_gen = SignalGenerator()
        self.paper = PaperTrading("default")
        self.alerts = AlertManager()
    
    def analyze_stock(self, code: str, name: str = "") -> dict:
        """完整分析一只股票"""
        # 获取K线数据
        try:
            result = self.adapter.stock_kline(code, period="daily", top_n=120)
            if not result.get("ok"):
                return {"ok": False, "error": result.get("error", "获取数据失败")}
            
            import pandas as pd
            items = result.get("data", {}).get("items", [])
            if len(items) < 60:
                return {"ok": False, "error": "数据不足"}
            
            df = pd.DataFrame(items)
            df.columns = [c.lower() for c in df.columns]
            # 确保列名正确
            if '收盘' in df.columns:
                df = df.rename(columns={
                    '开盘': 'open',
                    '收盘': 'close',
                    '最高': 'high',
                    '最低': 'low',
                    '成交量': 'volume'
                })
        except Exception as e:
            return {"ok": False, "error": f"获取数据失败: {e}"}
        
        # 生成交易信号
        signal = self.signal_gen.generate_signal(df)
        
        # 获取最新价格
        current_price = df['close'].iloc[-1]
        prev_close = df['close'].iloc[-2] if len(df) > 1 else current_price
        change_pct = ((current_price - prev_close) / prev_close) * 100
        
        # 检查预警
        triggered_alerts = self.alerts.check_alerts(code, current_price, change_pct)
        
        return {
            "ok": True,
            "code": code,
            "name": name or code,
            "current_price": current_price,
            "change_pct": change_pct,
            "signal": signal.signal.value,
            "confidence": signal.confidence,
            "reasons": signal.reasons,
            "entry_price": signal.entry_price,
            "stop_loss": signal.stop_loss,
            "take_profit": signal.take_profit,
            "alerts": [a.message for a in triggered_alerts]
        }
    
    def paper_trade(self, action: str, code: str, name: str, price: float, shares: int, reason: str = ""):
        """模拟盘交易"""
        if action.upper() == "BUY":
            return self.paper.buy(code, name, price, shares, reason)
        elif action.upper() == "SELL":
            return self.paper.sell(code, price, shares, reason)
        else:
            return False, "未知操作"
    
    def get_portfolio(self):
        """获取模拟盘组合"""
        return self.paper.get_report()
    
    def add_alert(self, code: str, name: str, alert_type: str, threshold: float, message: str = ""):
        """添加价格预警"""
        alert_id = self.alerts.add_alert(code, name, alert_type, threshold, message)
        return f"✅ 预警已设置 [{alert_id}]：{name}({code}) {alert_type} {threshold}"
    
    def list_alerts(self):
        """列出所有预警"""
        return self.alerts.list_alerts()

def main():
    parser = argparse.ArgumentParser(description="交易分析工具")
    parser.add_argument("--action", choices=["analyze", "buy", "sell", "portfolio", "alert", "list-alerts"], required=True)
    parser.add_argument("--code", help="股票代码")
    parser.add_argument("--name", help="股票名称")
    parser.add_argument("--price", type=float, help="价格")
    parser.add_argument("--shares", type=int, help="股数")
    parser.add_argument("--type", help="预警类型")
    parser.add_argument("--threshold", type=float, help="预警阈值")
    parser.add_argument("--reason", help="交易理由")
    
    args = parser.parse_args()
    
    analyzer = TradingAnalyzer()
    
    if args.action == "analyze":
        if not args.code:
            print("错误：需要 --code 参数")
            return
        result = analyzer.analyze_stock(args.code, args.name or "")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.action == "buy":
        if not all([args.code, args.name, args.price, args.shares]):
            print("错误：需要 --code, --name, --price, --shares 参数")
            return
        success, msg = analyzer.paper_trade("BUY", args.code, args.name, args.price, args.shares, args.reason or "")
        print(msg)
    
    elif args.action == "sell":
        if not all([args.code, args.price]):
            print("错误：需要 --code, --price 参数")
            return
        success, msg = analyzer.paper_trade("SELL", args.code, args.name or "", args.price, args.shares or 0, args.reason or "")
        print(msg)
    
    elif args.action == "portfolio":
        print(analyzer.get_portfolio())
    
    elif args.action == "alert":
        if not all([args.code, args.name, args.type, args.threshold]):
            print("错误：需要 --code, --name, --type, --threshold 参数")
            return
        print(analyzer.add_alert(args.code, args.name, args.type, args.threshold, args.reason or ""))
    
    elif args.action == "list-alerts":
        print(analyzer.list_alerts())

if __name__ == "__main__":
    main()
