#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轻量级股票分析系统
Lightweight Stock Analysis System
"""

import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any
import time

class LightweightStockAnalyzer:
    """轻量级股票分析器 - 无需本地数据存储"""
    
    def __init__(self):
        self.cache = {}  # 简单内存缓存
        self.cache_expire = 300  # 5分钟缓存过期
        
        # 支持的数据源
        self.data_sources = {
            'akshare': self._get_akshare_data,
            'mock': self._get_mock_data  # 模拟数据，用于演示
        }
        
        # 当前使用的数据源
        self.current_source = 'mock'  # 默认使用模拟数据
    
    def get_stock_list(self, market='A股', limit=50):
        """获取股票列表 - 不存储，实时获取"""
        cache_key = f"stock_list_{market}_{limit}"
        
        # 检查缓存
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        # 模拟股票列表（实际可接入真实API）
        stock_list = self._generate_stock_list(limit)
        
        # 缓存结果
        self._set_cache(cache_key, stock_list)
        
        return stock_list
    
    def get_stock_data(self, symbol: str, days: int = 30):
        """获取股票数据 - 实时获取，不本地存储"""
        cache_key = f"stock_data_{symbol}_{days}"
        
        # 检查缓存
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        
        # 获取数据
        data_func = self.data_sources.get(self.current_source)
        if not data_func:
            raise ValueError(f"不支持的数据源: {self.current_source}")
        
        stock_data = data_func(symbol, days)
        
        # 缓存结果
        self._set_cache(cache_key, stock_data)
        
        return stock_data
    
    def analyze_stock(self, symbol: str):
        """分析股票 - 轻量级分析"""
        try:
            # 获取数据
            data = self.get_stock_data(symbol, 30)
            if not data:
                return {'error': f'无法获取股票 {symbol} 的数据'}
            
            # 计算技术指标
            indicators = self._calculate_indicators(data)
            
            # 生成评分
            score = self._calculate_score(indicators)
            
            # 生成推荐理由
            reason = self._generate_reason(indicators, score)
            
            return {
                'symbol': symbol,
                'name': data.get('name', symbol),
                'current_price': data.get('current_price', 0),
                'score': score,
                'reason': reason,
                'indicators': indicators,
                'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {'error': f'分析股票 {symbol} 失败: {str(e)}'}
    
    def get_recommendations(self, count: int = 10):
        """获取推荐股票 - 轻量级推荐"""
        try:
            # 获取股票列表
            stock_list = self.get_stock_list(limit=50)
            
            # 分析每只股票
            recommendations = []
            for stock in stock_list[:20]:  # 只分析前20只，避免API限制
                analysis = self.analyze_stock(stock['symbol'])
                if 'error' not in analysis:
                    recommendations.append(analysis)
                
                # 避免API频率限制
                time.sleep(0.1)
            
            # 按评分排序
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            
            return recommendations[:count]
            
        except Exception as e:
            return {'error': f'获取推荐失败: {str(e)}'}
    
    def _generate_stock_list(self, limit: int):
        """生成股票列表（模拟数据）"""
        # 实际应用中，这里应该调用真实的股票列表API
        stocks = [
            {'symbol': '000001.SZ', 'name': '平安银行', 'industry': '银行'},
            {'symbol': '000002.SZ', 'name': '万科A', 'industry': '房地产'},
            {'symbol': '600519.SH', 'name': '贵州茅台', 'industry': '白酒'},
            {'symbol': '000858.SZ', 'name': '五粮液', 'industry': '白酒'},
            {'symbol': '300750.SZ', 'name': '宁德时代', 'industry': '电池'},
            {'symbol': '002415.SZ', 'name': '海康威视', 'industry': '安防'},
            {'symbol': '600036.SH', 'name': '招商银行', 'industry': '银行'},
            {'symbol': '000063.SZ', 'name': '中兴通讯', 'industry': '通信'},
            {'symbol': '002594.SZ', 'name': '比亚迪', 'industry': '汽车'},
            {'symbol': '600276.SH', 'name': '恒瑞医药', 'industry': '医药'},
        ]
        
        # 扩展到更多股票（模拟）
        extended_stocks = []
        for i in range(limit):
            if i < len(stocks):
                extended_stocks.append(stocks[i])
            else:
                # 生成模拟股票
                extended_stocks.append({
                    'symbol': f'{600000 + i:06d}.SH',
                    'name': f'股票{i:03d}',
                    'industry': np.random.choice(['科技', '金融', '消费', '医药', '制造'])
                })
        
        return extended_stocks
    
    def _get_mock_data(self, symbol: str, days: int):
        """获取模拟数据"""
        # 生成模拟的股票数据
        base_price = np.random.uniform(10, 100)
        prices = []
        
        for i in range(days):
            change = np.random.normal(0, 0.02)  # 2%的日波动
            base_price *= (1 + change)
            prices.append({
                'date': (datetime.now() - timedelta(days=days-i)).strftime('%Y-%m-%d'),
                'open': round(base_price * 0.99, 2),
                'high': round(base_price * 1.02, 2),
                'low': round(base_price * 0.98, 2),
                'close': round(base_price, 2),
                'volume': int(np.random.uniform(1000000, 10000000))
            })
        
        return {
            'symbol': symbol,
            'name': symbol.split('.')[0],
            'current_price': prices[-1]['close'],
            'prices': prices
        }
    
    def _get_akshare_data(self, symbol: str, days: int):
        """获取AKShare数据（需要安装akshare）"""
        try:
            import akshare as ak
            
            # 转换股票代码格式
            code = symbol.split('.')[0]
            
            # 获取历史数据
            df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")
            
            # 只取最近的数据
            df = df.tail(days)
            
            # 转换格式
            prices = []
            for _, row in df.iterrows():
                prices.append({
                    'date': row['日期'],
                    'open': float(row['开盘']),
                    'high': float(row['最高']),
                    'low': float(row['最低']),
                    'close': float(row['收盘']),
                    'volume': int(row['成交量'])
                })
            
            return {
                'symbol': symbol,
                'name': symbol,
                'current_price': prices[-1]['close'] if prices else 0,
                'prices': prices
            }
            
        except ImportError:
            print("❌ 未安装akshare，使用模拟数据")
            return self._get_mock_data(symbol, days)
        except Exception as e:
            print(f"❌ 获取AKShare数据失败: {e}，使用模拟数据")
            return self._get_mock_data(symbol, days)
    
    def _calculate_indicators(self, data: Dict):
        """计算技术指标"""
        prices = data.get('prices', [])
        if len(prices) < 5:
            return {}
        
        closes = [p['close'] for p in prices]
        volumes = [p['volume'] for p in prices]
        
        # 简单移动平均
        ma5 = np.mean(closes[-5:]) if len(closes) >= 5 else closes[-1]
        ma10 = np.mean(closes[-10:]) if len(closes) >= 10 else closes[-1]
        ma20 = np.mean(closes[-20:]) if len(closes) >= 20 else closes[-1]
        
        # RSI
        rsi = self._calculate_rsi(closes)
        
        # 成交量比率
        vol_ratio = volumes[-1] / np.mean(volumes) if len(volumes) > 1 else 1
        
        return {
            'ma5': round(ma5, 2),
            'ma10': round(ma10, 2),
            'ma20': round(ma20, 2),
            'rsi': round(rsi, 2),
            'volume_ratio': round(vol_ratio, 2),
            'price_change': round((closes[-1] - closes[-2]) / closes[-2] * 100, 2) if len(closes) > 1 else 0
        }
    
    def _calculate_rsi(self, prices: List[float], period: int = 14):
        """计算RSI"""
        if len(prices) < period + 1:
            return 50  # 默认值
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_score(self, indicators: Dict):
        """计算综合评分"""
        score = 50  # 基础分
        
        # MA趋势评分
        if indicators.get('ma5', 0) > indicators.get('ma10', 0):
            score += 10
        if indicators.get('ma10', 0) > indicators.get('ma20', 0):
            score += 10
        
        # RSI评分
        rsi = indicators.get('rsi', 50)
        if 30 < rsi < 70:
            score += 10
        elif rsi < 30:
            score += 5  # 超卖
        
        # 成交量评分
        vol_ratio = indicators.get('volume_ratio', 1)
        if vol_ratio > 1.5:
            score += 10
        elif vol_ratio > 1.2:
            score += 5
        
        # 价格变化评分
        price_change = indicators.get('price_change', 0)
        if 0 < price_change < 5:
            score += 5
        elif price_change > 5:
            score += 3
        
        return min(100, max(0, score))
    
    def _generate_reason(self, indicators: Dict, score: float):
        """生成推荐理由"""
        reasons = []
        
        if indicators.get('ma5', 0) > indicators.get('ma10', 0):
            reasons.append("短期趋势向上")
        
        if indicators.get('volume_ratio', 1) > 1.5:
            reasons.append("成交量放大")
        
        rsi = indicators.get('rsi', 50)
        if 30 < rsi < 70:
            reasons.append("RSI处于合理区间")
        elif rsi < 30:
            reasons.append("RSI显示超卖")
        
        if score > 70:
            reasons.append("技术面强势")
        elif score > 50:
            reasons.append("技术面偏好")
        
        return "，".join(reasons) if reasons else "技术指标中性"
    
    def _is_cache_valid(self, key: str):
        """检查缓存是否有效"""
        if key not in self.cache:
            return False
        
        cache_time = self.cache[key]['time']
        return (time.time() - cache_time) < self.cache_expire
    
    def _set_cache(self, key: str, data: Any):
        """设置缓存"""
        self.cache[key] = {
            'data': data,
            'time': time.time()
        }

# 使用示例
def main():
    """主函数"""
    print("🚀 轻量级股票分析系统启动...")
    
    analyzer = LightweightStockAnalyzer()
    
    # 获取推荐股票
    print("\n📊 获取推荐股票...")
    recommendations = analyzer.get_recommendations(5)
    
    if isinstance(recommendations, list):
        print(f"✅ 获取到 {len(recommendations)} 只推荐股票:")
        
        for i, stock in enumerate(recommendations, 1):
            print(f"\n{i}. {stock['name']} ({stock['symbol']})")
            print(f"   当前价格: {stock['current_price']}")
            print(f"   评分: {stock['score']}")
            print(f"   理由: {stock['reason']}")
    else:
        print(f"❌ 获取推荐失败: {recommendations.get('error', '未知错误')}")

if __name__ == "__main__":
    main()
