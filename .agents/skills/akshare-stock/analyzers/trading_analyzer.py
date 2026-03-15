#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交易信号分析器 - 基于技术分析生成买卖信号
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

class SignalType(Enum):
    BUY = "买入"
    SELL = "卖出"
    HOLD = "持有"
    WATCH = "观望"

@dataclass
class TradeSignal:
    signal: SignalType
    confidence: float  # 0-100
    reasons: List[str]
    entry_price: float = None
    stop_loss: float = None
    take_profit: float = None
    timeframe: str = "日线"

class TechnicalAnalyzer:
    """技术分析器"""
    
    @staticmethod
    def calculate_ma(prices: pd.Series, periods: List[int] = [5, 10, 20, 60]) -> Dict[str, pd.Series]:
        """计算移动平均线"""
        mas = {}
        for period in periods:
            mas[f"MA{period}"] = prices.rolling(window=period).mean()
        return mas
    
    @staticmethod
    def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """计算MACD指标"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal).mean()
        macd_hist = macd - macd_signal
        return {
            "macd": macd,
            "signal": macd_signal,
            "hist": macd_hist
        }
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """计算RSI指标"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_bollinger(prices: pd.Series, period: int = 20, std_dev: int = 2) -> Dict[str, pd.Series]:
        """计算布林带"""
        ma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = ma + (std * std_dev)
        lower = ma - (std * std_dev)
        return {
            "middle": ma,
            "upper": upper,
            "lower": lower
        }
    
    @staticmethod
    def calculate_kdj(high: pd.Series, low: pd.Series, close: pd.Series, 
                     n: int = 9, m1: int = 3, m2: int = 3) -> Dict[str, pd.Series]:
        """计算KDJ指标"""
        rsv = (close - low.rolling(window=n).min()) / (high.rolling(window=n).max() - low.rolling(window=n).min()) * 100
        k = rsv.ewm(com=m1-1).mean()
        d = k.ewm(com=m2-1).mean()
        j = 3 * k - 2 * d
        return {"k": k, "d": d, "j": j}

class SignalGenerator:
    """交易信号生成器"""
    
    def __init__(self):
        self.analyzer = TechnicalAnalyzer()
    
    def generate_signal(self, df: pd.DataFrame) -> TradeSignal:
        """
        基于技术分析生成交易信号
        df需要包含: open, high, low, close, volume
        """
        close = df['close']
        high = df['high']
        low = df['low']
        volume = df['volume']
        
        # 计算指标
        ma_dict = self.analyzer.calculate_ma(close)
        macd_dict = self.analyzer.calculate_macd(close)
        rsi = self.analyzer.calculate_rsi(close)
        boll_dict = self.analyzer.calculate_bollinger(close)
        kdj_dict = self.analyzer.calculate_kdj(high, low, close)
        
        # 获取最新值
        current_price = close.iloc[-1]
        current_ma5 = ma_dict['MA5'].iloc[-1]
        current_ma10 = ma_dict['MA10'].iloc[-1]
        current_ma20 = ma_dict['MA20'].iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_macd = macd_dict['macd'].iloc[-1]
        current_macd_signal = macd_dict['signal'].iloc[-1]
        current_macd_hist = macd_dict['hist'].iloc[-1]
        prev_macd_hist = macd_dict['hist'].iloc[-2] if len(macd_dict['hist']) > 1 else 0
        current_k = kdj_dict['k'].iloc[-1]
        current_d = kdj_dict['d'].iloc[-1]
        current_j = kdj_dict['j'].iloc[-1]
        
        # 信号判断
        signals = []
        confidence = 50
        
        # 1. 均线趋势
        if current_price > current_ma5 > current_ma10 > current_ma20:
            signals.append("多头排列，趋势向上")
            confidence += 15
        elif current_price < current_ma5 < current_ma10 < current_ma20:
            signals.append("空头排列，趋势向下")
            confidence -= 15
        else:
            signals.append("均线纠缠，趋势不明")
        
        # 2. MACD信号
        if current_macd_hist > 0 and prev_macd_hist <= 0:
            signals.append("MACD金叉，买入信号")
            confidence += 10
        elif current_macd_hist < 0 and prev_macd_hist >= 0:
            signals.append("MACD死叉，卖出信号")
            confidence -= 10
        elif current_macd > 0:
            signals.append("MACD在零轴上方，偏多")
            confidence += 5
        else:
            signals.append("MACD在零轴下方，偏空")
            confidence -= 5
        
        # 3. RSI信号
        if current_rsi > 70:
            signals.append(f"RSI超买({current_rsi:.1f})")
            confidence -= 10
        elif current_rsi < 30:
            signals.append(f"RSI超卖({current_rsi:.1f})")
            confidence += 10
        elif 40 <= current_rsi <= 60:
            signals.append(f"RSI中性({current_rsi:.1f})")
        
        # 4. KDJ信号
        if current_k > current_d and current_j < 20:
            signals.append("KDJ低位金叉")
            confidence += 10
        elif current_k < current_d and current_j > 80:
            signals.append("KDJ高位死叉")
            confidence -= 10
        
        # 5. 价格与布林带关系
        if current_price > boll_dict['upper'].iloc[-1]:
            signals.append("价格突破布林带上轨，可能超买")
            confidence -= 5
        elif current_price < boll_dict['lower'].iloc[-1]:
            signals.append("价格跌破布林带下轨，可能超卖")
            confidence += 5
        
        # 确定最终信号
        if confidence >= 70:
            signal_type = SignalType.BUY
        elif confidence <= 30:
            signal_type = SignalType.SELL
        elif 45 <= confidence <= 55:
            signal_type = SignalType.WATCH
        else:
            signal_type = SignalType.HOLD
        
        # 计算止损止盈位
        atr = self._calculate_atr(high, low, close)
        current_atr = atr.iloc[-1]
        
        stop_loss = current_price - 2 * current_atr if signal_type == SignalType.BUY else current_price + 2 * current_atr
        take_profit = current_price + 3 * current_atr if signal_type == SignalType.BUY else current_price - 3 * current_atr
        
        return TradeSignal(
            signal=signal_type,
            confidence=min(max(confidence, 0), 100),
            reasons=signals,
            entry_price=current_price,
            stop_loss=round(stop_loss, 2),
            take_profit=round(take_profit, 2),
            timeframe="日线"
        )
    
    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """计算ATR（平均真实波幅）"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr

if __name__ == "__main__":
    # 测试代码
    print("交易信号分析器已加载")
