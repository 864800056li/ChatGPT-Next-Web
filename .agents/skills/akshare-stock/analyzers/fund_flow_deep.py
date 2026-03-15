#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
资金流向深度分析 - 龙虎榜、机构持仓、北向资金等
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class FundFlowData:
    """资金流向数据"""
    stock_code: str
    stock_name: str
    main_force_net: float  # 主力净流入
    retail_net: float  # 散户净流入
    institution_net: float  # 机构净流入
    north_bound_net: float  # 北向资金净流入
    large_order_net: float  # 大单净流入
    medium_order_net: float  # 中单净流入
    small_order_net: float  # 小单净流入
    update_time: str

@dataclass
class DragonTigerData:
    """龙虎榜数据"""
    stock_code: str
    stock_name: str
    date: str
    reason: str  # 上榜原因
    buy_amount: float  # 买入金额
    sell_amount: float  # 卖出金额
    net_amount: float  # 净额
    top5_buy: List[Dict]  # 买入前5席位
    top5_sell: List[Dict]  # 卖出前5席位
    institution_buy: float  # 机构买入
    institution_sell: float  # 机构卖出

class FundFlowAnalyzer:
    """资金流向分析器"""
    
    def analyze_fund_flow(self, stock_code: str, stock_name: str, 
                          flow_data: Dict) -> FundFlowData:
        """分析资金流向"""
        return FundFlowData(
            stock_code=stock_code,
            stock_name=stock_name,
            main_force_net=flow_data.get('main_force', 0),
            retail_net=flow_data.get('retail', 0),
            institution_net=flow_data.get('institution', 0),
            north_bound_net=flow_data.get('north_bound', 0),
            large_order_net=flow_data.get('large_order', 0),
            medium_order_net=flow_data.get('medium_order', 0),
            small_order_net=flow_data.get('small_order', 0),
            update_time=datetime.now().isoformat()
        )
    
    def get_flow_signal(self, data: FundFlowData) -> Dict:
        """根据资金流向生成信号"""
        signals = []
        score = 50  # 基础分
        
        # 主力资金
        if data.main_force_net > 100000000:  # 1亿
            signals.append("主力大幅净流入，资金看好")
            score += 20
        elif data.main_force_net > 50000000:  # 5000万
            signals.append("主力净流入，资金流入")
            score += 10
        elif data.main_force_net < -100000000:
            signals.append("主力大幅净流出，资金撤离")
            score -= 20
        elif data.main_force_net < -50000000:
            signals.append("主力净流出，资金流出")
            score -= 10
        
        # 北向资金
        if data.north_bound_net > 50000000:
            signals.append("北向资金大幅买入，外资看好")
            score += 15
        elif data.north_bound_net < -50000000:
            signals.append("北向资金大幅卖出，外资撤离")
            score -= 15
        
        # 大单动向
        if data.large_order_net > 0 and data.small_order_net < 0:
            signals.append("大单买入小单卖出，主力吸筹")
            score += 10
        elif data.large_order_net < 0 and data.small_order_net > 0:
            signals.append("大单卖出小单买入，主力出货")
            score -= 10
        
        # 机构资金
        if data.institution_net > 30000000:
            signals.append("机构资金净流入，机构看好")
            score += 15
        elif data.institution_net < -30000000:
            signals.append("机构资金净流出，机构看空")
            score -= 15
        
        # 综合判断
        if score >= 80:
            trend = '强烈看多'
        elif score >= 60:
            trend = '看多'
        elif score <= 20:
            trend = '强烈看空'
        elif score <= 40:
            trend = '看空'
        else:
            trend = '中性'
        
        return {
            'stock_code': data.stock_code,
            'stock_name': data.stock_name,
            'score': score,
            'trend': trend,
            'signals': signals,
            'main_force': data.main_force_net,
            'north_bound': data.north_bound_net,
            'institution': data.institution_net
        }
    
    def analyze_dragon_tiger(self, data: Dict) -> DragonTigerData:
        """分析龙虎榜数据"""
        return DragonTigerData(
            stock_code=data.get('code', ''),
            stock_name=data.get('name', ''),
            date=data.get('date', ''),
            reason=data.get('reason', ''),
            buy_amount=data.get('buy_amount', 0),
            sell_amount=data.get('sell_amount', 0),
            net_amount=data.get('buy_amount', 0) - data.get('sell_amount', 0),
            top5_buy=data.get('top5_buy', []),
            top5_sell=data.get('top5_sell', []),
            institution_buy=data.get('institution_buy', 0),
            institution_sell=data.get('institution_sell', 0)
        )
    
    def get_dragon_tiger_signal(self, data: DragonTigerData) -> Dict:
        """根据龙虎榜生成信号"""
        signals = []
        
        # 机构参与度
        institution_ratio = (data.institution_buy + data.institution_sell) / (data.buy_amount + data.sell_amount + 1)
        
        if institution_ratio > 0.3:
            signals.append(f"机构参与度{institution_ratio*100:.1f}%，机构活跃")
        
        # 机构净买入
        institution_net = data.institution_buy - data.institution_sell
        if institution_net > 100000000:
            signals.append(f"机构净买入{institution_net/100000000:.2f}亿，机构强烈看好")
        elif institution_net > 50000000:
            signals.append(f"机构净买入{institution_net/100000000:.2f}亿，机构看好")
        elif institution_net < -100000000:
            signals.append(f"机构净卖出{abs(institution_net)/100000000:.2f}亿，机构看空")
        
        # 游资特征
        top5_buy_sum = sum(b.get('amount', 0) for b in data.top5_buy)
        if top5_buy_sum > 200000000:
            signals.append("游资大举买入，短线活跃")
        
        # 上榜原因分析
        if '涨停' in data.reason:
            signals.append("涨停上榜，关注持续性")
        if '连续' in data.reason:
            signals.append("连续上榜，热度较高")
        
        return {
            'stock_code': data.stock_code,
            'stock_name': data.stock_name,
            'date': data.date,
            'reason': data.reason,
            'net_amount': data.net_amount,
            'institution_net': institution_net,
            'signals': signals
        }
    
    def detect_main_force_accumulation(self, flow_history: List[FundFlowData]) -> Dict:
        """检测主力吸筹迹象"""
        if len(flow_history) < 5:
            return {'error': '数据不足'}
        
        # 最近5日资金流向
        recent = flow_history[-5:]
        main_force_sum = sum(d.main_force_net for d in recent)
        
        # 连续流入天数
        consecutive_inflow = 0
        for d in reversed(recent):
            if d.main_force_net > 0:
                consecutive_inflow += 1
            else:
                break
        
        # 判断吸筹
        if consecutive_inflow >= 3 and main_force_sum > 100000000:
            return {
                'detected': True,
                'confidence': 'high',
                'consecutive_days': consecutive_inflow,
                'total_inflow': main_force_sum,
                'suggestion': '主力连续吸筹，关注突破机会'
            }
        elif consecutive_inflow >= 2 and main_force_sum > 50000000:
            return {
                'detected': True,
                'confidence': 'medium',
                'consecutive_days': consecutive_inflow,
                'total_inflow': main_force_sum,
                'suggestion': '主力有吸筹迹象，保持关注'
            }
        
        return {
            'detected': False,
            'consecutive_days': consecutive_inflow,
            'total_inflow': main_force_sum
        }
    
    def detect_main_force_distribution(self, flow_history: List[FundFlowData]) -> Dict:
        """检测主力出货迹象"""
        if len(flow_history) < 5:
            return {'error': '数据不足'}
        
        recent = flow_history[-5:]
        main_force_sum = sum(d.main_force_net for d in recent)
        
        consecutive_outflow = 0
        for d in reversed(recent):
            if d.main_force_net < 0:
                consecutive_outflow += 1
            else:
                break
        
        if consecutive_outflow >= 3 and main_force_sum < -100000000:
            return {
                'detected': True,
                'confidence': 'high',
                'consecutive_days': consecutive_outflow,
                'total_outflow': abs(main_force_sum),
                'suggestion': '主力连续出货，注意风险'
            }
        elif consecutive_outflow >= 2 and main_force_sum < -50000000:
            return {
                'detected': True,
                'confidence': 'medium',
                'consecutive_days': consecutive_outflow,
                'total_outflow': abs(main_force_sum),
                'suggestion': '主力有出货迹象，谨慎对待'
            }
        
        return {
            'detected': False,
            'consecutive_days': consecutive_outflow,
            'total_outflow': abs(main_force_sum)
        }

if __name__ == "__main__":
    print("资金流向深度分析系统已加载")
