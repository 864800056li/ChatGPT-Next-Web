#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财报自动解读系统 - 自动提取和分析财报PDF的关键信息
"""
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FinancialReport:
    """财报数据"""
    stock_code: str
    stock_name: str
    report_type: str  # 年报/季报/半年报
    report_date: str
    revenue: float  # 营收
    revenue_yoy: float  # 营收同比
    net_profit: float  # 净利润
    net_profit_yoy: float  # 净利润同比
    eps: float  # 每股收益
    roe: float  # 净资产收益率
    gross_margin: float  # 毛利率
    net_margin: float  # 净利率
    debt_ratio: float  # 资产负债率
    operating_cash_flow: float  # 经营现金流
    key_highlights: List[str]  # 关键亮点
    risk_warnings: List[str]  # 风险提示

class FinancialReportAnalyzer:
    """财报分析器"""
    
    def parse_report_text(self, text: str, stock_code: str, stock_name: str) -> FinancialReport:
        """
        从财报文本中提取关键信息
        实际应用中应该解析PDF，这里简化处理
        """
        # 提取关键数据（使用正则表达式）
        revenue = self._extract_number(text, r'营业收入[\s:：]*(\d+\.?\d*)')
        revenue_yoy = self._extract_number(text, r'营收同比[\s:：]*([+-]?\d+\.?\d*)%?')
        net_profit = self._extract_number(text, r'净利润[\s:：]*(\d+\.?\d*)')
        net_profit_yoy = self._extract_number(text, r'净利润同比[\s:：]*([+-]?\d+\.?\d*)%?')
        eps = self._extract_number(text, r'每股收益[\s:：]*(\d+\.?\d*)')
        roe = self._extract_number(text, r'ROE[\s:：]*(\d+\.?\d*)%?')
        gross_margin = self._extract_number(text, r'毛利率[\s:：]*(\d+\.?\d*)%?')
        net_margin = self._extract_number(text, r'净利率[\s:：]*(\d+\.?\d*)%?')
        debt_ratio = self._extract_number(text, r'资产负债率[\s:：]*(\d+\.?\d*)%?')
        
        # 分析关键亮点和风险
        highlights = self._extract_highlights(text)
        risks = self._extract_risks(text)
        
        return FinancialReport(
            stock_code=stock_code,
            stock_name=stock_name,
            report_type=self._detect_report_type(text),
            report_date=self._extract_date(text),
            revenue=revenue,
            revenue_yoy=revenue_yoy,
            net_profit=net_profit,
            net_profit_yoy=net_profit_yoy,
            eps=eps,
            roe=roe,
            gross_margin=gross_margin,
            net_margin=net_margin,
            debt_ratio=debt_ratio,
            operating_cash_flow=0,  # 需要更复杂的提取
            key_highlights=highlights,
            risk_warnings=risks
        )
    
    def _extract_number(self, text: str, pattern: str) -> float:
        """提取数字"""
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except:
                return 0.0
        return 0.0
    
    def _extract_date(self, text: str) -> str:
        """提取日期"""
        patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
            r'(\d{4})-(\d{2})-(\d{2})',
            r'(\d{4})/(\d{2})/(\d{2})'
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)}-{match.group(2).zfill(2)}-{match.group(3).zfill(2)}"
        return datetime.now().strftime('%Y-%m-%d')
    
    def _detect_report_type(self, text: str) -> str:
        """检测财报类型"""
        if '年报' in text or '年度报告' in text:
            return '年报'
        elif '半年报' in text or '中期报告' in text:
            return '半年报'
        elif '三季报' in text or '第三季度' in text:
            return '三季报'
        elif '一季报' in text or '第一季度' in text:
            return '一季报'
        return '财报'
    
    def _extract_highlights(self, text: str) -> List[str]:
        """提取业绩亮点"""
        highlights = []
        
        # 增长相关
        if re.search(r'增长[\s:：]*([\d.]+)%', text):
            match = re.search(r'增长[\s:：]*([\d.]+)%', text)
            if match and float(match.group(1)) > 20:
                highlights.append(f"营收/利润增长{match.group(1)}%，增速较快")
        
        # 超预期
        if '超预期' in text or '超预期' in text:
            highlights.append("业绩超市场预期")
        
        # 毛利率提升
        if '毛利率提升' in text or '毛利率改善' in text:
            highlights.append("盈利能力改善，毛利率提升")
        
        # 现金流
        if '现金流' in text and ('充裕' in text or '良好' in text):
            highlights.append("现金流状况良好")
        
        # 市场份额
        if '市场份额' in text and ('提升' in text or '增长' in text):
            highlights.append("市场份额提升")
        
        return highlights
    
    def _extract_risks(self, text: str) -> List[str]:
        """提取风险提示"""
        risks = []
        
        # 下滑相关
        if re.search(r'(下滑|下降|减少)[\s:：]*([\d.]+)%', text):
            match = re.search(r'(下滑|下降|减少)[\s:：]*([\d.]+)%', text)
            if match and float(match.group(2)) > 10:
                risks.append(f"部分指标下滑{match.group(2)}%，需关注")
        
        # 亏损
        if '亏损' in text:
            risks.append("出现亏损，业绩承压")
        
        # 应收账款
        if '应收账款' in text and ('增加' in text or '上升' in text):
            risks.append("应收账款增加，回款压力增大")
        
        # 存货
        if '存货' in text and ('增加' in text or '积压' in text):
            risks.append("存货增加，存在减值风险")
        
        # 负债
        if '负债率' in text and ('上升' in text or '较高' in text):
            risks.append("负债率较高，财务风险需关注")
        
        return risks
    
    def generate_report_summary(self, report: FinancialReport) -> str:
        """生成财报解读摘要"""
        lines = [
            f"📊 {report.stock_name}（{report.stock_code}）{report.report_type}解读",
            f"📅 报告期：{report.report_date}",
            "",
            "💰 核心财务数据：",
            f"  • 营业收入：{report.revenue:.2f}亿元（同比{report.revenue_yoy:+.2f}%）",
            f"  • 净利润：{report.net_profit:.2f}亿元（同比{report.net_profit_yoy:+.2f}%）",
            f"  • 每股收益：{report.eps:.2f}元",
            f"  • ROE：{report.roe:.2f}%",
            f"  • 毛利率：{report.gross_margin:.2f}%",
            f"  • 净利率：{report.net_margin:.2f}%",
            f"  • 资产负债率：{report.debt_ratio:.2f}%",
            ""
        ]
        
        if report.key_highlights:
            lines.append("✨ 业绩亮点：")
            for highlight in report.key_highlights:
                lines.append(f"  • {highlight}")
            lines.append("")
        
        if report.risk_warnings:
            lines.append("⚠️ 风险提示：")
            for risk in report.risk_warnings:
                lines.append(f"  • {risk}")
            lines.append("")
        
        # 综合评价
        lines.append("📈 综合评价：")
        score = self._calculate_score(report)
        if score >= 80:
            lines.append("  业绩优秀，基本面强劲，建议关注")
        elif score >= 60:
            lines.append("  业绩良好，符合预期，可持有")
        elif score >= 40:
            lines.append("  业绩一般，需观察后续改善")
        else:
            lines.append("  业绩承压，注意风险")
        
        return '\n'.join(lines)
    
    def _calculate_score(self, report: FinancialReport) -> int:
        """计算财报评分"""
        score = 50  # 基础分
        
        # 营收增长
        if report.revenue_yoy > 30:
            score += 15
        elif report.revenue_yoy > 10:
            score += 10
        elif report.revenue_yoy < -10:
            score -= 10
        
        # 利润增长
        if report.net_profit_yoy > 30:
            score += 15
        elif report.net_profit_yoy > 10:
            score += 10
        elif report.net_profit_yoy < -10:
            score -= 15
        
        # ROE
        if report.roe > 20:
            score += 10
        elif report.roe > 15:
            score += 5
        elif report.roe < 8:
            score -= 5
        
        # 毛利率
        if report.gross_margin > 40:
            score += 5
        elif report.gross_margin < 20:
            score -= 5
        
        # 负债率
        if report.debt_ratio < 50:
            score += 5
        elif report.debt_ratio > 70:
            score -= 5
        
        return max(0, min(100, score))
    
    def compare_reports(self, current: FinancialReport, previous: FinancialReport) -> Dict:
        """对比两期财报"""
        return {
            'revenue_change': current.revenue_yoy - previous.revenue_yoy,
            'profit_change': current.net_profit_yoy - previous.net_profit_yoy,
            'roe_change': current.roe - previous.roe,
            'margin_change': current.gross_margin - previous.gross_margin,
            'trend': 'improving' if current.net_profit_yoy > previous.net_profit_yoy else 'declining'
        }

if __name__ == "__main__":
    print("财报自动解读系统已加载")
