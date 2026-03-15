#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻情绪分析系统 - 监控股票相关新闻和市场情绪
"""
import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

@dataclass
class NewsItem:
    """新闻条目"""
    title: str
    content: str
    source: str
    publish_time: str
    url: str = ""
    sentiment: float = 0.0  # -1到1，负面到正面
    keywords: List[str] = None
    related_stocks: List[str] = None

@dataclass
class SentimentAlert:
    """情绪预警"""
    stock_code: str
    stock_name: str
    alert_type: str  # positive/negative/neutral
    sentiment_score: float
    news_count: int
    summary: str
    created_at: str

class NewsSentimentAnalyzer:
    """新闻情绪分析器"""
    
    # 正面关键词词典
    POSITIVE_WORDS = [
        '利好', '上涨', '涨停', '大涨', '飙升', '突破', '创新高', '强劲',
        '增长', '盈利', '超预期', '并购', '收购', '合作', '订单', '中标',
        '政策扶持', '补贴', '减税', '降准', '降息', '放水', '刺激',
        '看好', '推荐', '买入', '增持', '目标价上调', '评级上调'
    ]
    
    # 负面关键词词典
    NEGATIVE_WORDS = [
        '利空', '下跌', '跌停', '大跌', '暴跌', '跳水', '破位', '创新低',
        '亏损', '预亏', '暴雷', '退市', '调查', '处罚', '违规', '造假',
        '减持', '清仓', '抛售', '裁员', '停产', '破产', '债务违约',
        '看空', '卖出', '减持', '目标价下调', '评级下调'
    ]
    
    # 行业关键词映射
    SECTOR_KEYWORDS = {
        '新能源': ['宁德时代', '比亚迪', '隆基', '光伏', '锂电', '储能', '新能源汽车'],
        '白酒': ['茅台', '五粮液', '泸州老窖', '洋河', '汾酒', '白酒', '酿酒'],
        '医药': ['恒瑞', '药明', '迈瑞', '医疗器械', '创新药', '集采', '医保'],
        '科技': ['华为', '芯片', '半导体', 'AI', '人工智能', '5G', '算力'],
        '金融': ['银行', '保险', '券商', '证券', '金融科技', '降息', '降准'],
        '房地产': ['万科', '保利', '地产', '房地产', '房价', '楼市调控']
    }
    
    def __init__(self):
        self.news_cache: List[NewsItem] = []
        self.alerts: List[SentimentAlert] = []
        self.data_dir = Path.home() / ".openclaw" / "workspace" / "news_sentiment"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_text(self, text: str) -> float:
        """
        分析文本情绪
        返回-1到1之间的分数，越接近1越正面
        """
        if not text:
            return 0.0
        
        text = text.lower()
        
        # 统计正负关键词
        pos_count = sum(1 for word in self.POSITIVE_WORDS if word in text)
        neg_count = sum(1 for word in self.NEGATIVE_WORDS if word in text)
        
        total = pos_count + neg_count
        if total == 0:
            return 0.0
        
        # 计算情绪分数
        sentiment = (pos_count - neg_count) / total
        
        # 归一化到-1到1
        return max(-1, min(1, sentiment))
    
    def extract_related_stocks(self, text: str) -> List[str]:
        """从文本中提取相关股票"""
        stocks = []
        
        # 匹配股票代码（6位数字）
        codes = re.findall(r'\b(\d{6})\b', text)
        stocks.extend(codes)
        
        # 匹配股票名称（需要维护一个股票名称词典）
        # 这里简化处理
        
        return list(set(stocks))
    
    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        keywords = []
        
        # 提取所有正负关键词
        for word in self.POSITIVE_WORDS + self.NEGATIVE_WORDS:
            if word in text:
                keywords.append(word)
        
        return keywords
    
    def analyze_news(self, title: str, content: str = "", 
                     source: str = "", publish_time: str = "") -> NewsItem:
        """分析单条新闻"""
        full_text = title + " " + content
        
        sentiment = self.analyze_text(full_text)
        keywords = self.extract_keywords(full_text)
        related_stocks = self.extract_related_stocks(full_text)
        
        news = NewsItem(
            title=title,
            content=content,
            source=source,
            publish_time=publish_time or datetime.now().isoformat(),
            sentiment=sentiment,
            keywords=keywords,
            related_stocks=related_stocks
        )
        
        self.news_cache.append(news)
        return news
    
    def get_sector_sentiment(self, sector: str, days: int = 7) -> Dict:
        """获取某个板块的情绪指数"""
        keywords = self.SECTOR_KEYWORDS.get(sector, [sector])
        
        # 过滤相关新闻
        related_news = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for news in self.news_cache:
            news_date = datetime.fromisoformat(news.publish_time.replace('Z', '+00:00'))
            if news_date < cutoff_date:
                continue
            
            text = news.title + " " + news.content
            if any(kw in text for kw in keywords):
                related_news.append(news)
        
        if not related_news:
            return {
                'sector': sector,
                'sentiment': 0,
                'news_count': 0,
                'trend': 'neutral'
            }
        
        # 计算平均情绪
        avg_sentiment = sum(n.sentiment for n in related_news) / len(related_news)
        
        # 判断趋势
        if avg_sentiment > 0.3:
            trend = 'very_positive'
        elif avg_sentiment > 0.1:
            trend = 'positive'
        elif avg_sentiment < -0.3:
            trend = 'very_negative'
        elif avg_sentiment < -0.1:
            trend = 'negative'
        else:
            trend = 'neutral'
        
        return {
            'sector': sector,
            'sentiment': round(avg_sentiment, 2),
            'news_count': len(related_news),
            'trend': trend,
            'keywords': self._get_top_keywords(related_news)
        }
    
    def _get_top_keywords(self, news_list: List[NewsItem], top_n: int = 5) -> List[str]:
        """获取热门关键词"""
        keyword_count = {}
        for news in news_list:
            for kw in news.keywords or []:
                keyword_count[kw] = keyword_count.get(kw, 0) + 1
        
        sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
        return [kw for kw, count in sorted_keywords[:top_n]]
    
    def check_stock_sentiment(self, stock_code: str, stock_name: str) -> SentimentAlert:
        """检查特定股票的情绪"""
        # 过滤相关新闻（最近3天）
        related_news = []
        cutoff_date = datetime.now() - timedelta(days=3)
        
        for news in self.news_cache:
            news_date = datetime.fromisoformat(news.publish_time.replace('Z', '+00:00'))
            if news_date < cutoff_date:
                continue
            
            if stock_code in (news.related_stocks or []) or stock_name in news.title:
                related_news.append(news)
        
        if not related_news:
            return None
        
        # 计算情绪
        avg_sentiment = sum(n.sentiment for n in related_news) / len(related_news)
        
        # 判断预警类型
        if avg_sentiment > 0.5:
            alert_type = 'very_positive'
            summary = f"近3天有{len(related_news)}条新闻，情绪非常正面"
        elif avg_sentiment > 0.2:
            alert_type = 'positive'
            summary = f"近3天有{len(related_news)}条新闻，情绪偏正面"
        elif avg_sentiment < -0.5:
            alert_type = 'very_negative'
            summary = f"近3天有{len(related_news)}条新闻，情绪非常负面，请注意风险"
        elif avg_sentiment < -0.2:
            alert_type = 'negative'
            summary = f"近3天有{len(related_news)}条新闻，情绪偏负面"
        else:
            alert_type = 'neutral'
            summary = f"近3天有{len(related_news)}条新闻，情绪中性"
        
        alert = SentimentAlert(
            stock_code=stock_code,
            stock_name=stock_name,
            alert_type=alert_type,
            sentiment_score=round(avg_sentiment, 2),
            news_count=len(related_news),
            summary=summary,
            created_at=datetime.now().isoformat()
        )
        
        self.alerts.append(alert)
        return alert
    
    def get_market_overview(self) -> Dict:
        """获取市场情绪总览"""
        sectors = ['新能源', '白酒', '医药', '科技', '金融', '房地产']
        
        overview = {}
        for sector in sectors:
            overview[sector] = self.get_sector_sentiment(sector)
        
        # 计算整体情绪
        sentiments = [s['sentiment'] for s in overview.values() if s['news_count'] > 0]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        return {
            'overall_sentiment': round(avg_sentiment, 2),
            'sectors': overview,
            'hot_sectors': sorted(overview.items(), 
                                 key=lambda x: x[1]['news_count'], 
                                 reverse=True)[:3]
        }

if __name__ == "__main__":
    # 测试
    analyzer = NewsSentimentAnalyzer()
    
    # 测试分析
    news1 = analyzer.analyze_news(
        title="茅台发布超预期财报，净利润增长20%",
        content="贵州茅台今日发布年报，净利润同比增长20%，超出市场预期...",
        source="财经网",
        publish_time=datetime.now().isoformat()
    )
    
    print(f"新闻情绪: {news1.sentiment}")
    print(f"关键词: {news1.keywords}")
    print(f"相关股票: {news1.related_stocks}")
