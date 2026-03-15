#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多因子选股模型 - 综合多个维度对股票进行打分排名
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class FactorType(Enum):
    """因子类型"""
    VALUE = "估值因子"  # PE, PB, PS
    GROWTH = "成长因子"  # 营收增长, 利润增长
    QUALITY = "质量因子"  # ROE, 毛利率, 现金流
    MOMENTUM = "动量因子"  # 涨跌幅, 换手率
    VOLATILITY = "波动因子"  # 波动率, 贝塔

@dataclass
class StockScore:
    """股票评分"""
    code: str
    name: str
    total_score: float
    rank: int
    factor_scores: Dict[str, float]
    raw_data: Dict[str, float]

class MultiFactorModel:
    """多因子选股模型"""
    
    def __init__(self):
        # 因子权重配置
        self.factor_weights = {
            'value': 0.25,      # 估值因子权重
            'growth': 0.25,     # 成长因子权重
            'quality': 0.25,    # 质量因子权重
            'momentum': 0.15,   # 动量因子权重
            'volatility': 0.10  # 波动因子权重
        }
        
        # 估值因子：越低越好
        self.value_factors = {
            'pe': {'weight': 0.4, 'direction': 'lower_better'},
            'pb': {'weight': 0.3, 'direction': 'lower_better'},
            'ps': {'weight': 0.2, 'direction': 'lower_better'},
            'dividend_yield': {'weight': 0.1, 'direction': 'higher_better'}
        }
        
        # 成长因子：越高越好
        self.growth_factors = {
            'revenue_growth': {'weight': 0.4, 'direction': 'higher_better'},
            'profit_growth': {'weight': 0.4, 'direction': 'higher_better'},
            'eps_growth': {'weight': 0.2, 'direction': 'higher_better'}
        }
        
        # 质量因子：越高越好
        self.quality_factors = {
            'roe': {'weight': 0.35, 'direction': 'higher_better'},
            'gross_margin': {'weight': 0.25, 'direction': 'higher_better'},
            'net_margin': {'weight': 0.25, 'direction': 'higher_better'},
            'debt_ratio': {'weight': 0.15, 'direction': 'lower_better'}  # 负债率越低越好
        }
        
        # 动量因子
        self.momentum_factors = {
            'return_1m': {'weight': 0.3, 'direction': 'higher_better'},
            'return_3m': {'weight': 0.4, 'direction': 'higher_better'},
            'return_6m': {'weight': 0.3, 'direction': 'higher_better'}
        }
        
        # 波动因子：越低越好
        self.volatility_factors = {
            'volatility_20d': {'weight': 0.5, 'direction': 'lower_better'},
            'beta': {'weight': 0.5, 'direction': 'lower_better'}
        }
    
    def calculate_factor_score(self, value: float, factor_config: Dict, 
                               all_values: List[float]) -> float:
        """计算单个因子得分（0-100分）"""
        if not all_values or value is None or np.isnan(value):
            return 50  # 缺失值给中等分数
        
        # 计算分位数
        percentile = sum(1 for v in all_values if v <= value) / len(all_values) * 100
        
        if factor_config['direction'] == 'lower_better':
            # 越低越好，分位数越低分数越高
            score = 100 - percentile
        else:
            # 越高越好，分位数越高分数越高
            score = percentile
        
        return score
    
    def score_stock(self, stock_data: Dict, all_stocks_data: List[Dict]) -> StockScore:
        """对单只股票进行多因子打分"""
        code = stock_data.get('code', '')
        name = stock_data.get('name', '')
        
        factor_scores = {}
        
        # 1. 估值因子得分
        value_score = 0
        for factor, config in self.value_factors.items():
            values = [s.get(factor, 0) for s in all_stocks_data if s.get(factor) is not None]
            score = self.calculate_factor_score(stock_data.get(factor), config, values)
            value_score += score * config['weight']
        factor_scores['value'] = value_score
        
        # 2. 成长因子得分
        growth_score = 0
        for factor, config in self.growth_factors.items():
            values = [s.get(factor, 0) for s in all_stocks_data if s.get(factor) is not None]
            score = self.calculate_factor_score(stock_data.get(factor), config, values)
            growth_score += score * config['weight']
        factor_scores['growth'] = growth_score
        
        # 3. 质量因子得分
        quality_score = 0
        for factor, config in self.quality_factors.items():
            values = [s.get(factor, 0) for s in all_stocks_data if s.get(factor) is not None]
            score = self.calculate_factor_score(stock_data.get(factor), config, values)
            quality_score += score * config['weight']
        factor_scores['quality'] = quality_score
        
        # 4. 动量因子得分
        momentum_score = 0
        for factor, config in self.momentum_factors.items():
            values = [s.get(factor, 0) for s in all_stocks_data if s.get(factor) is not None]
            score = self.calculate_factor_score(stock_data.get(factor), config, values)
            momentum_score += score * config['weight']
        factor_scores['momentum'] = momentum_score
        
        # 5. 波动因子得分
        volatility_score = 0
        for factor, config in self.volatility_factors.items():
            values = [s.get(factor, 0) for s in all_stocks_data if s.get(factor) is not None]
            score = self.calculate_factor_score(stock_data.get(factor), config, values)
            volatility_score += score * config['weight']
        factor_scores['volatility'] = volatility_score
        
        # 计算总分
        total_score = (
            factor_scores['value'] * self.factor_weights['value'] +
            factor_scores['growth'] * self.factor_weights['growth'] +
            factor_scores['quality'] * self.factor_weights['quality'] +
            factor_scores['momentum'] * self.factor_weights['momentum'] +
            factor_scores['volatility'] * self.factor_weights['volatility']
        )
        
        return StockScore(
            code=code,
            name=name,
            total_score=round(total_score, 2),
            rank=0,  # 稍后计算
            factor_scores={k: round(v, 2) for k, v in factor_scores.items()},
            raw_data=stock_data
        )
    
    def rank_stocks(self, stocks_data: List[Dict]) -> List[StockScore]:
        """对多只股票进行排名"""
        scores = []
        
        for stock in stocks_data:
            score = self.score_stock(stock, stocks_data)
            scores.append(score)
        
        # 按总分排序
        scores.sort(key=lambda x: x.total_score, reverse=True)
        
        # 添加排名
        for i, score in enumerate(scores):
            score.rank = i + 1
        
        return scores
    
    def get_top_picks(self, stocks_data: List[Dict], top_n: int = 10) -> List[StockScore]:
        """获取Top N股票"""
        ranked = self.rank_stocks(stocks_data)
        return ranked[:top_n]
    
    def generate_report(self, stocks_data: List[Dict], top_n: int = 20) -> str:
        """生成选股报告"""
        ranked = self.rank_stocks(stocks_data)
        top_stocks = ranked[:top_n]
        
        lines = [
            "📊 多因子选股模型报告",
            f"🕒 生成时间：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}",
            f"📈 分析股票数：{len(stocks_data)}",
            "",
            f"🏆 Top {top_n} 推荐股票：",
            ""
        ]
        
        for stock in top_stocks:
            lines.append(f"{stock.rank}. {stock.name}（{stock.code}）")
            lines.append(f"   综合评分：{stock.total_score}")
            lines.append(f"   估值：{stock.factor_scores['value']} | "
                        f"成长：{stock.factor_scores['growth']} | "
                        f"质量：{stock.factor_scores['quality']}")
            lines.append("")
        
        # 添加因子说明
        lines.append("📋 评分说明：")
        lines.append("  • 估值因子：PE、PB越低越好，股息率越高越好")
        lines.append("  • 成长因子：营收、利润增长率越高越好")
        lines.append("  • 质量因子：ROE、毛利率越高越好，负债率越低越好")
        lines.append("  • 动量因子：近期涨幅越高越好")
        lines.append("  • 波动因子：波动率越低越好")
        
        return '\n'.join(lines)
    
    def filter_stocks(self, stocks_data: List[Dict], 
                      min_score: float = 60,
                      min_factor_scores: Dict[str, float] = None) -> List[StockScore]:
        """根据条件筛选股票"""
        ranked = self.rank_stocks(stocks_data)
        
        filtered = []
        for stock in ranked:
            if stock.total_score < min_score:
                continue
            
            if min_factor_scores:
                skip = False
                for factor, min_val in min_factor_scores.items():
                    if stock.factor_scores.get(factor, 0) < min_val:
                        skip = True
                        break
                if skip:
                    continue
            
            filtered.append(stock)
        
        return filtered

if __name__ == "__main__":
    # 测试
    model = MultiFactorModel()
    
    # 模拟数据
    test_data = [
        {'code': '600519', 'name': '贵州茅台', 'pe': 25, 'pb': 8, 'roe': 30, 'revenue_growth': 15},
        {'code': '000858', 'name': '五粮液', 'pe': 18, 'pb': 5, 'roe': 22, 'revenue_growth': 12},
        {'code': '002594', 'name': '比亚迪', 'pe': 35, 'pb': 6, 'roe': 18, 'revenue_growth': 25},
    ]
    
    scores = model.rank_stocks(test_data)
    for s in scores:
        print(f"{s.name}: {s.total_score}")
