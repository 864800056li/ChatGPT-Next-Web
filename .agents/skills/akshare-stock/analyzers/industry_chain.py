#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
产业链分析系统 - 分析股票上下游产业链关系
"""
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class IndustryChain:
    """产业链信息"""
    stock_code: str
    stock_name: str
    industry: str
    upstream: List[Dict]  # 上游供应商
    downstream: List[Dict]  # 下游客户
    peers: List[Dict]  # 同行业竞争对手
    substitutes: List[Dict]  # 替代品
    key_indicators: Dict  # 关键指标

class IndustryChainAnalyzer:
    """产业链分析器"""
    
    # 产业链数据库（简化版，实际需要维护完整数据库）
    CHAIN_DATABASE = {
        '宁德时代': {
            'industry': '动力电池',
            'upstream': [
                {'name': '锂矿', 'stocks': ['赣锋锂业', '天齐锂业'], 'impact': 'high'},
                {'name': '钴矿', 'stocks': ['华友钴业', '洛阳钼业'], 'impact': 'medium'},
                {'name': '正极材料', 'stocks': ['当升科技', '容百科技'], 'impact': 'high'},
                {'name': '负极材料', 'stocks': ['贝特瑞', '璞泰来'], 'impact': 'high'},
                {'name': '电解液', 'stocks': ['天赐材料', '新宙邦'], 'impact': 'medium'},
                {'name': '隔膜', 'stocks': ['恩捷股份', '星源材质'], 'impact': 'medium'},
            ],
            'downstream': [
                {'name': '新能源汽车', 'stocks': ['比亚迪', '特斯拉'], 'impact': 'high'},
                {'name': '储能', 'stocks': ['阳光电源', '派能科技'], 'impact': 'medium'},
            ],
            'peers': [
                {'name': '比亚迪', 'code': '002594'},
                {'name': '中创新航', 'code': 'H股'},
                {'name': '国轩高科', 'code': '002074'},
                {'name': '亿纬锂能', 'code': '300014'},
            ],
            'key_indicators': ['碳酸锂价格', '电池装机量', '新能源车销量']
        },
        '贵州茅台': {
            'industry': '白酒',
            'upstream': [
                {'name': '粮食', 'stocks': [], 'impact': 'low'},
                {'name': '包装', 'stocks': ['裕同科技'], 'impact': 'low'},
            ],
            'downstream': [
                {'name': '经销商', 'stocks': [], 'impact': 'high'},
                {'name': '消费者', 'stocks': [], 'impact': 'high'},
            ],
            'peers': [
                {'name': '五粮液', 'code': '000858'},
                {'name': '泸州老窖', 'code': '000568'},
                {'name': '洋河股份', 'code': '002304'},
            ],
            'key_indicators': ['批价', '库存', '动销', '茅台1935销量']
        },
        '比亚迪': {
            'industry': '新能源汽车',
            'upstream': [
                {'name': '电池', 'stocks': ['宁德时代'], 'impact': 'high'},
                {'name': '芯片', 'stocks': ['斯达半导', '士兰微'], 'impact': 'high'},
                {'name': '电机', 'stocks': ['汇川技术'], 'impact': 'medium'},
                {'name': '车身', 'stocks': ['华域汽车'], 'impact': 'medium'},
            ],
            'downstream': [
                {'name': '个人消费者', 'stocks': [], 'impact': 'high'},
                {'name': '网约车', 'stocks': [], 'impact': 'medium'},
                {'name': '公交', 'stocks': [], 'impact': 'low'},
            ],
            'peers': [
                {'name': '特斯拉', 'code': '美股'},
                {'name': '蔚来', 'code': '美股'},
                {'name': '小鹏', 'code': '美股'},
                {'name': '理想', 'code': '美股'},
            ],
            'key_indicators': ['销量', '市占率', '毛利率', '电池成本']
        }
    }
    
    def analyze(self, stock_name: str) -> Optional[IndustryChain]:
        """分析指定股票的产业链"""
        data = self.CHAIN_DATABASE.get(stock_name)
        
        if not data:
            return None
        
        # 获取股票代码（简化）
        code_map = {
            '宁德时代': '300750',
            '贵州茅台': '600519',
            '比亚迪': '002594'
        }
        
        return IndustryChain(
            stock_code=code_map.get(stock_name, ''),
            stock_name=stock_name,
            industry=data['industry'],
            upstream=data['upstream'],
            downstream=data['downstream'],
            peers=data['peers'],
            substitutes=[],  # 可扩展
            key_indicators=data['key_indicators']
        )
    
    def get_upstream_risk(self, stock_name: str) -> Dict:
        """分析上游风险"""
        chain = self.analyze(stock_name)
        if not chain:
            return {'error': '无产业链数据'}
        
        high_impact = [u for u in chain.upstream if u['impact'] == 'high']
        
        return {
            'stock': stock_name,
            'high_risk_suppliers': high_impact,
            'risk_level': 'high' if len(high_impact) > 2 else 'medium',
            'suggestion': f"关注{', '.join([u['name'] for u in high_impact])}的价格波动"
        }
    
    def get_downstream_demand(self, stock_name: str) -> Dict:
        """分析下游需求"""
        chain = self.analyze(stock_name)
        if not chain:
            return {'error': '无产业链数据'}
        
        high_impact = [d for d in chain.downstream if d['impact'] == 'high']
        
        return {
            'stock': stock_name,
            'key_customers': high_impact,
            'demand_stability': 'stable' if len(high_impact) > 1 else 'volatile',
            'suggestion': f"跟踪{', '.join([d['name'] for d in high_impact])}的需求变化"
        }
    
    def get_competitive_position(self, stock_name: str) -> Dict:
        """分析竞争地位"""
        chain = self.analyze(stock_name)
        if not chain:
            return {'error': '无产业链数据'}
        
        peers = chain.peers
        
        return {
            'stock': stock_name,
            'industry': chain.industry,
            'main_competitors': peers,
            'competition_intensity': 'high' if len(peers) > 3 else 'medium',
            'suggestion': '建议对比毛利率、市占率、ROE等指标'
        }
    
    def generate_report(self, stock_name: str) -> str:
        """生成产业链分析报告"""
        chain = self.analyze(stock_name)
        if not chain:
            return f"暂无{stock_name}的产业链数据"
        
        lines = [
            f"📊 {stock_name}（{chain.stock_code}）产业链分析",
            f"行业：{chain.industry}",
            "",
            "🔺 上游供应商："
        ]
        
        for up in chain.upstream:
            impact_emoji = "🔴" if up['impact'] == 'high' else "🟡"
            stocks = ', '.join(up['stocks']) if up['stocks'] else '外部采购'
            lines.append(f"  {impact_emoji} {up['name']}：{stocks}")
        
        lines.append("")
        lines.append("🔻 下游客户：")
        
        for down in chain.downstream:
            impact_emoji = "🔴" if down['impact'] == 'high' else "🟡"
            stocks = ', '.join(down['stocks']) if down['stocks'] else '终端市场'
            lines.append(f"  {impact_emoji} {down['name']}：{stocks}")
        
        lines.append("")
        lines.append("⚔️ 主要竞争对手：")
        for peer in chain.peers:
            lines.append(f"  • {peer['name']}（{peer['code']}）")
        
        lines.append("")
        lines.append("📈 关键跟踪指标：")
        for indicator in chain.key_indicators:
            lines.append(f"  • {indicator}")
        
        return '\n'.join(lines)

if __name__ == "__main__":
    analyzer = IndustryChainAnalyzer()
    
    # 测试
    report = analyzer.generate_report('宁德时代')
    print(report)
