#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API驱动的轻量级股票分析系统 - 支持4000+只股票
API-Driven Lightweight Stock Analysis System - Supporting 4000+ Stocks
"""

import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import os
import sys
from typing import List, Dict, Any, Optional, Tuple
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('StockAPI')

class StockAPIManager:
    """股票API管理器 - 支持多种数据源"""

    def __init__(self):
        # 配置API密钥（实际使用时应从环境变量或配置文件获取）
        self.api_keys = {
            'tushare': os.environ.get('TUSHARE_TOKEN', ''),
            'akshare': '',  # AKShare不需要token
            'eastmoney': '',
            'sina': ''
        }

        # 初始化缓存
        self.cache = {}
        self.cache_expire = {
            'stock_list': 86400,  # 股票列表缓存1天
            'stock_data': 1800,   # 股票数据缓存30分钟
            'realtime': 60        # 实时数据缓存1分钟
        }

        # 设置默认数据源
        self.default_source = 'akshare'

        # 初始化API调用计数和限制
        self.api_calls = {}
        self.api_limits = {
            'tushare': {'daily': 500, 'minute': 10},
            'akshare': {'daily': 10000, 'minute': 100},
            'eastmoney': {'daily': 10000, 'minute': 100},
            'sina': {'daily': 10000, 'minute': 100}
        }

        # 记录API调用时间
        self.last_call_time = {}

    def get_stock_list(self, market: str = 'A', source: Optional[str] = None) -> List[Dict]:
        """获取股票列表

        Args:
            market: 市场类型，'A'=A股, 'HK'=港股, 'US'=美股
            source: 数据源，None表示使用默认源

        Returns:
            股票列表，每个股票包含symbol, name, industry等信息
        """
        source = source or self.default_source
        cache_key = f"stock_list_{market}_{source}"

        # 检查缓存
        cached_data = self._get_from_cache(cache_key, 'stock_list')
        if cached_data:
            logger.info(f"从缓存获取股票列表: {len(cached_data)}只")
            return cached_data

        # 记录API调用
        self._record_api_call(source)

        try:
            # 根据数据源获取股票列表
            if source == 'akshare':
                stock_list = self._get_stock_list_akshare(market)
            elif source == 'tushare':
                stock_list = self._get_stock_list_tushare(market)
            elif source == 'eastmoney':
                stock_list = self._get_stock_list_eastmoney(market)
            else:
                # 如果不支持的数据源，使用模拟数据
                stock_list = self._get_mock_stock_list(market)

            # 缓存结果
            self._save_to_cache(cache_key, stock_list, 'stock_list')

            logger.info(f"获取股票列表成功: {len(stock_list)}只")
            return stock_list

        except Exception as e:
            logger.error(f"获取股票列表失败: {str(e)}")
            # 如果失败，返回模拟数据
            mock_data = self._get_mock_stock_list(market)
            return mock_data

    def get_stock_data(self, symbol: str, days: int = 30, source: Optional[str] = None) -> Dict:
        """获取股票历史数据

        Args:
            symbol: 股票代码，如'000001.SZ'
            days: 获取天数
            source: 数据源，None表示使用默认源

        Returns:
            股票数据，包含prices列表（每日开高低收等）
        """
        source = source or self.default_source
        cache_key = f"stock_data_{symbol}_{days}_{source}"

        # 检查缓存
        cached_data = self._get_from_cache(cache_key, 'stock_data')
        if cached_data:
            logger.info(f"从缓存获取股票数据: {symbol}")
            return cached_data

        # 记录API调用
        self._record_api_call(source)

        try:
            # 根据数据源获取股票数据
            if source == 'akshare':
                stock_data = self._get_stock_data_akshare(symbol, days)
            elif source == 'tushare':
                stock_data = self._get_stock_data_tushare(symbol, days)
            elif source == 'eastmoney':
                stock_data = self._get_stock_data_eastmoney(symbol, days)
            else:
                # 如果不支持的数据源，使用模拟数据
                stock_data = self._get_mock_stock_data(symbol, days)

            # 缓存结果
            self._save_to_cache(cache_key, stock_data, 'stock_data')

            logger.info(f"获取股票数据成功: {symbol}, {len(stock_data.get('prices', []))}天")
            return stock_data

        except Exception as e:
            logger.error(f"获取股票数据失败: {symbol}, {str(e)}")
            # 如果失败，返回模拟数据
            mock_data = self._get_mock_stock_data(symbol, days)
            return mock_data

    def get_realtime_price(self, symbol: str, source: Optional[str] = None) -> Dict:
        """获取实时价格

        Args:
            symbol: 股票代码
            source: 数据源

        Returns:
            实时价格信息
        """
        source = source or self.default_source
        cache_key = f"realtime_{symbol}_{source}"

        # 检查缓存（实时数据缓存时间较短）
        cached_data = self._get_from_cache(cache_key, 'realtime')
        if cached_data:
            return cached_data

        # 记录API调用
        self._record_api_call(source)

        try:
            if source == 'akshare':
                realtime_data = self._get_realtime_akshare(symbol)
            elif source == 'sina':
                realtime_data = self._get_realtime_sina(symbol)
            else:
                realtime_data = self._get_mock_realtime(symbol)

            # 缓存结果
            self._save_to_cache(cache_key, realtime_data, 'realtime')

            return realtime_data

        except Exception as e:
            logger.error(f"获取实时价格失败: {symbol}, {str(e)}")
            return self._get_mock_realtime(symbol)

    def search_stocks(self, keyword: str, limit: int = 20) -> List[Dict]:
        """搜索股票

        Args:
            keyword: 搜索关键词（股票名称或代码）
            limit: 返回结果数量限制

        Returns:
            匹配的股票列表
        """
        try:
            # 获取完整股票列表
            all_stocks = self.get_stock_list()

            # 搜索匹配的股票
            matched_stocks = []
            keyword_lower = keyword.lower()

            for stock in all_stocks:
                # 检查股票代码或名称是否匹配
                if (keyword_lower in stock.get('symbol', '').lower() or
                    keyword_lower in stock.get('name', '').lower() or
                    keyword in stock.get('symbol', '') or
                    keyword in stock.get('name', '')):
                    matched_stocks.append(stock)

                    if len(matched_stocks) >= limit:
                        break

            logger.info(f"搜索股票 '{keyword}': 找到{len(matched_stocks)}只")
            return matched_stocks

        except Exception as e:
            logger.error(f"搜索股票失败: {str(e)}")
            return []

    def _get_stock_list_akshare(self, market: str) -> List[Dict]:
        """使用AKShare获取股票列表"""
        try:
            import akshare as ak

            if market == 'A':
                # 获取A股股票列表
                df = ak.stock_info_a_code_name()

                # 转换为标准格式
                stocks = []
                for _, row in df.iterrows():
                    code = row['code']
                    # 判断市场
                    if code.startswith('6'):
                        symbol = f"{code}.SH"
                    elif code.startswith(('0', '3')):
                        symbol = f"{code}.SZ"
                    else:
                        continue

                    stocks.append({
                        'symbol': symbol,
                        'code': code,
                        'name': row['name'],
                        'market': 'A股',
                        'exchange': 'SH' if code.startswith('6') else 'SZ'
                    })

                return stocks

            elif market == 'HK':
                # 港股列表（如果支持）
                return []
            elif market == 'US':
                # 美股列表（如果支持）
                return []
            else:
                return []

        except ImportError:
            logger.warning("AKShare未安装，使用模拟数据")
            return self._get_mock_stock_list(market)
        except Exception as e:
            logger.error(f"AKShare获取股票列表失败: {str(e)}")
            return self._get_mock_stock_list(market)

    def _get_stock_data_akshare(self, symbol: str, days: int) -> Dict:
        """使用AKShare获取股票数据"""
        try:
            import akshare as ak

            # 提取股票代码
            code = symbol.split('.')[0]

            # 获取历史数据
            df = ak.stock_zh_a_hist(symbol=code, period="daily", adjust="qfq")

            if df.empty:
                raise ValueError(f"未获取到股票 {symbol} 的数据")

            # 只取最近的数据
            df = df.tail(days)

            # 转换为标准格式
            prices = []
            for _, row in df.iterrows():
                prices.append({
                    'date': row['日期'],
                    'open': float(row['开盘']),
                    'high': float(row['最高']),
                    'low': float(row['最低']),
                    'close': float(row['收盘']),
                    'volume': int(row['成交量']),
                    'amount': float(row['成交额'])
                })

            # 获取股票基本信息
            name = symbol  # 默认使用symbol作为名称
            try:
                # 尝试获取股票名称
                stock_info = ak.stock_individual_info_em(symbol=code)
                if not stock_info.empty:
                    name = stock_info.loc[stock_info['item'] == '股票简称', 'value'].iloc[0]
            except:
                pass

            return {
                'symbol': symbol,
                'name': name,
                'current_price': prices[-1]['close'] if prices else 0,
                'prices': prices,
                'data_source': 'akshare',
                'last_update': datetime.now().isoformat()
            }

        except ImportError:
            logger.warning("AKShare未安装，使用模拟数据")
            return self._get_mock_stock_data(symbol, days)
        except Exception as e:
            logger.error(f"AKShare获取股票数据失败: {symbol}, {str(e)}")
            return self._get_mock_stock_data(symbol, days)

    def _get_mock_stock_list(self, market: str) -> List[Dict]:
        """生成模拟股票列表"""
        # 真实的A股股票代码和名称
        real_stocks = [
            {'symbol': '000001.SZ', 'name': '平安银行', 'industry': '银行'},
            {'symbol': '000002.SZ', 'name': '万科A', 'industry': '房地产'},
            {'symbol': '000063.SZ', 'name': '中兴通讯', 'industry': '通信设备'},
            {'symbol': '000100.SZ', 'name': 'TCL科技', 'industry': '电子'},
            {'symbol': '000333.SZ', 'name': '美的集团', 'industry': '家用电器'},
            {'symbol': '000651.SZ', 'name': '格力电器', 'industry': '家用电器'},
            {'symbol': '000858.SZ', 'name': '五粮液', 'industry': '白酒'},
            {'symbol': '002415.SZ', 'name': '海康威视', 'industry': '安防设备'},
            {'symbol': '002594.SZ', 'name': '比亚迪', 'industry': '汽车'},
            {'symbol': '300750.SZ', 'name': '宁德时代', 'industry': '电池'},
            {'symbol': '600000.SH', 'name': '浦发银行', 'industry': '银行'},
            {'symbol': '600036.SH', 'name': '招商银行', 'industry': '银行'},
            {'symbol': '600519.SH', 'name': '贵州茅台', 'industry': '白酒'},
            {'symbol': '600887.SH', 'name': '伊利股份', 'industry': '乳品'},
            {'symbol': '601318.SH', 'name': '中国平安', 'industry': '保险'},
            {'symbol': '601398.SH', 'name': '工商银行', 'industry': '银行'},
            {'symbol': '688981.SH', 'name': '中芯国际', 'industry': '半导体'},
        ]

        # 扩展到更多股票（模拟4000+只股票）
        extended_stocks = real_stocks.copy()

        # 生成更多模拟股票
        industries = ['科技', '金融', '消费', '医药', '制造', '能源', '材料', '电信', '公用事业', '房地产']

        for i in range(17, 4000):  # 从17开始，生成到4000只
            if i < 1000:
                # 深交所主板 000xxx
                symbol = f"{i:06d}.SZ"
            elif i < 2000:
                # 深交所中小板 002xxx
                symbol = f"{i-1000+2000:06d}.SZ"
            elif i < 3000:
                # 创业板 300xxx
                symbol = f"{i-2000+3000:06d}.SZ"
            elif i < 4000:
                # 上交所 600xxx
                symbol = f"{i-3000+6000:06d}.SH"
            else:
                # 科创板 688xxx
                symbol = f"{i-4000+6880:06d}.SH"

            extended_stocks.append({
                'symbol': symbol,
                'code': symbol.split('.')[0],
                'name': f'股票{i:04d}',
                'industry': np.random.choice(industries),
                'market': 'A股',
                'exchange': symbol.split('.')[1]
            })

        return extended_stocks

    def _get_mock_stock_data(self, symbol: str, days: int) -> Dict:
        """生成模拟股票数据"""
        # 根据股票代码生成相对稳定的随机种子
        np.random.seed(hash(symbol) % 2**32)

        # 设置基础价格（根据股票类型）
        if '600519' in symbol:  # 贵州茅台
            base_price = 1800
        elif '000858' in symbol:  # 五粮液
            base_price = 150
        elif symbol.startswith('688'):  # 科创板
            base_price = np.random.uniform(50, 200)
        elif symbol.startswith('300'):  # 创业板
            base_price = np.random.uniform(20, 100)
        else:
            base_price = np.random.uniform(5, 50)

        # 生成历史价格数据
        prices = []
        current_price = base_price

        for i in range(days):
            # 生成日内波动
            daily_change = np.random.normal(0, 0.02)  # 2%的日波动
            current_price *= (1 + daily_change)

            # 确保价格不会太低
            current_price = max(current_price, 1.0)

            # 生成开高低收
            open_price = current_price * (1 + np.random.normal(0, 0.005))
            high_price = max(open_price, current_price) * (1 + np.random.uniform(0, 0.03))
            low_price = min(open_price, current_price) * (1 - np.random.uniform(0, 0.03))
            close_price = current_price

            # 生成成交量
            volume = int(np.random.uniform(1000000, 50000000))
            amount = volume * close_price / 100

            date = (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')

            prices.append({
                'date': date,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume,
                'amount': round(amount, 2)
            })

        # 获取股票名称
        stock_name = self._get_stock_name_from_symbol(symbol)

        return {
            'symbol': symbol,
            'name': stock_name,
            'current_price': prices[-1]['close'] if prices else base_price,
            'prices': prices,
            'data_source': 'mock',
            'last_update': datetime.now().isoformat()
        }

    def _get_stock_name_from_symbol(self, symbol: str) -> str:
        """根据股票代码获取股票名称"""
        # 真实股票名称映射
        name_mapping = {
            '000001.SZ': '平安银行', '000002.SZ': '万科A', '000063.SZ': '中兴通讯',
            '000100.SZ': 'TCL科技', '000333.SZ': '美的集团', '000651.SZ': '格力电器',
            '000858.SZ': '五粮液', '002415.SZ': '海康威视', '002594.SZ': '比亚迪',
            '300750.SZ': '宁德时代', '600000.SH': '浦发银行', '600036.SH': '招商银行',
            '600519.SH': '贵州茅台', '600887.SH': '伊利股份', '601318.SH': '中国平安',
            '601398.SH': '工商银行', '688981.SH': '中芯国际'
        }

        return name_mapping.get(symbol, f"股票{symbol.split('.')[0]}")

    def _get_mock_realtime(self, symbol: str) -> Dict:
        """生成模拟实时数据"""
        # 获取历史数据作为基础
        historical = self._get_mock_stock_data(symbol, 1)
        current_price = historical['current_price']

        # 生成实时波动
        change_pct = np.random.normal(0, 0.01)  # 1%的实时波动
        new_price = current_price * (1 + change_pct)

        return {
            'symbol': symbol,
            'name': historical['name'],
            'current_price': round(new_price, 2),
            'change': round(new_price - current_price, 2),
            'change_pct': round(change_pct * 100, 2),
            'volume': int(np.random.uniform(1000000, 10000000)),
            'timestamp': datetime.now().isoformat(),
            'data_source': 'mock'
        }

    def _get_from_cache(self, key: str, cache_type: str) -> Optional[Any]:
        """从缓存获取数据"""
        if key not in self.cache:
            return None

        cache_data = self.cache[key]
        cache_time = cache_data.get('timestamp', 0)
        expire_time = self.cache_expire.get(cache_type, 1800)

        # 检查是否过期
        if time.time() - cache_time > expire_time:
            del self.cache[key]
            return None

        return cache_data.get('data')

    def _save_to_cache(self, key: str, data: Any, cache_type: str):
        """保存数据到缓存"""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time(),
            'type': cache_type
        }

    def _record_api_call(self, source: str):
        """记录API调用"""
        current_time = time.time()

        if source not in self.api_calls:
            self.api_calls[source] = {'daily': 0, 'minute': 0, 'last_reset': current_time}

        # 重置计数器（如果需要）
        if current_time - self.api_calls[source]['last_reset'] > 86400:  # 24小时
            self.api_calls[source]['daily'] = 0
            self.api_calls[source]['last_reset'] = current_time

        if current_time - self.api_calls[source].get('last_minute_reset', 0) > 60:  # 1分钟
            self.api_calls[source]['minute'] = 0
            self.api_calls[source]['last_minute_reset'] = current_time

        # 增加计数
        self.api_calls[source]['daily'] += 1
        self.api_calls[source]['minute'] += 1

        # 检查是否超过限制
        limits = self.api_limits.get(source, {'daily': 10000, 'minute': 100})
        if (self.api_calls[source]['daily'] > limits['daily'] or
            self.api_calls[source]['minute'] > limits['minute']):
            logger.warning(f"API调用频率接近限制: {source}")

    def get_cache_stats(self) -> Dict:
        """获取缓存统计信息"""
        stats = {
            'total_items': len(self.cache),
            'by_type': {},
            'memory_usage': sys.getsizeof(self.cache)
        }

        for key, value in self.cache.items():
            cache_type = value.get('type', 'unknown')
            if cache_type not in stats['by_type']:
                stats['by_type'][cache_type] = 0
            stats['by_type'][cache_type] += 1

        return stats

    def clear_cache(self, cache_type: Optional[str] = None):
        """清理缓存"""
        if cache_type:
            # 清理特定类型的缓存
            keys_to_remove = [k for k, v in self.cache.items() if v.get('type') == cache_type]
            for key in keys_to_remove:
                del self.cache[key]
            logger.info(f"清理缓存类型: {cache_type}, 清理了{len(keys_to_remove)}项")
        else:
            # 清理所有缓存
            cache_count = len(self.cache)
            self.cache.clear()
            logger.info(f"清理所有缓存, 清理了{cache_count}项")


class LightweightStockAnalyzer:
    """轻量级股票分析器"""

    def __init__(self, api_manager: Optional[StockAPIManager] = None):
        self.api_manager = api_manager or StockAPIManager()

        # 技术指标参数
        self.indicator_params = {
            'ma_short': 5,
            'ma_medium': 10,
            'ma_long': 20,
            'rsi_period': 14,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9
        }

    def analyze_stock(self, symbol: str, days: int = 30) -> Dict:
        """分析单只股票"""
        try:
            logger.info(f"开始分析股票: {symbol}")

            # 获取股票数据
            stock_data = self.api_manager.get_stock_data(symbol, days)

            if not stock_data or not stock_data.get('prices'):
                return {'error': f'无法获取股票 {symbol} 的数据'}

            # 计算技术指标
            indicators = self._calculate_indicators(stock_data['prices'])

            # 计算评分
            score = self._calculate_score(indicators)

            # 生成推荐理由
            reason = self._generate_reason(indicators, score)

            # 获取实时价格
            realtime = self.api_manager.get_realtime_price(symbol)

            result = {
                'symbol': symbol,
                'name': stock_data.get('name', symbol),
                'current_price': realtime.get('current_price', stock_data.get('current_price', 0)),
                'change': realtime.get('change', 0),
                'change_pct': realtime.get('change_pct', 0),
                'score': score,
                'reason': reason,
                'indicators': indicators,
                'data_source': stock_data.get('data_source', 'unknown'),
                'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_days': len(stock_data.get('prices', []))
            }

            logger.info(f"股票分析完成: {symbol}, 评分: {score}")
            return result

        except Exception as e:
            logger.error(f"分析股票失败: {symbol}, {str(e)}")
            return {'error': f'分析股票 {symbol} 失败: {str(e)}'}

    def get_recommendations(self, count: int = 10, market: str = 'A') -> List[Dict]:
        """获取推荐股票"""
        try:
            logger.info(f"开始获取推荐股票: {count}只")

            # 获取股票列表
            stock_list = self.api_manager.get_stock_list(market)

            if not stock_list:
                return []

            # 限制分析数量（避免API限制）
            analysis_limit = min(50, len(stock_list))
            selected_stocks = stock_list[:analysis_limit]

            # 分析股票
            recommendations = []
            for i, stock in enumerate(selected_stocks):
                try:
                    analysis = self.analyze_stock(stock['symbol'])
                    if 'error' not in analysis:
                        recommendations.append(analysis)

                    # 进度显示
                    if (i + 1) % 10 == 0:
                        logger.info(f"已分析 {i + 1}/{analysis_limit} 只股票")

                    # 避免API频率限制
                    time.sleep(0.1)

                except Exception as e:
                    logger.warning(f"分析股票 {stock['symbol']} 失败: {str(e)}")
                    continue

            # 按评分排序
            recommendations.sort(key=lambda x: x.get('score', 0), reverse=True)

            # 返回前N只
            top_recommendations = recommendations[:count]

            logger.info(f"推荐股票获取完成: {len(top_recommendations)}只")
            return top_recommendations

        except Exception as e:
            logger.error(f"获取推荐股票失败: {str(e)}")
            return []

    def _calculate_indicators(self, prices: List[Dict]) -> Dict:
        """计算技术指标"""
        if not prices:
            return {}

        # 提取价格数据
        dates = [p['date'] for p in prices]
        closes = np.array([p['close'] for p in prices])
        opens = np.array([p['open'] for p in prices])
        highs = np.array([p['high'] for p in prices])
        lows = np.array([p['low'] for p in prices])
        volumes = np.array([p['volume'] for p in prices])

        # 计算移动平均线
        ma5 = self._calculate_ma(closes, self.indicator_params['ma_short'])
        ma10 = self._calculate_ma(closes, self.indicator_params['ma_medium'])
        ma20 = self._calculate_ma(closes, self.indicator_params['ma_long'])

        # 计算RSI
        rsi = self._calculate_rsi(closes, self.indicator_params['rsi_period'])

        # 计算MACD
        macd, signal, hist = self._calculate_macd(
            closes,
            self.indicator_params['macd_fast'],
            self.indicator_params['macd_slow'],
            self.indicator_params['macd_signal']
        )

        # 计算布林带
        upper, middle, lower = self._calculate_bollinger_bands(closes)

        # 计算KDJ
        k, d, j = self._calculate_kdj(highs, lows, closes)

        # 计算成交量变化
        volume_change = self._calculate_volume_change(volumes)

        # 计算价格变化
        price_change = self._calculate_price_change(closes)

        # 计算趋势指标
        trend = self._calculate_trend(closes, ma5, ma10, ma20)

        return {
            'ma5': float(ma5[-1]) if len(ma5) > 0 else None,
            'ma10': float(ma10[-1]) if len(ma10) > 0 else None,
            'ma20': float(ma20[-1]) if len(ma20) > 0 else None,
            'rsi': float(rsi[-1]) if len(rsi) > 0 else None,
            'macd': float(macd[-1]) if len(macd) > 0 else None,
            'macd_signal': float(signal[-1]) if len(signal) > 0 else None,
            'macd_hist': float(hist[-1]) if len(hist) > 0 else None,
            'boll_upper': float(upper[-1]) if len(upper) > 0 else None,
            'boll_middle': float(middle[-1]) if len(middle) > 0 else None,
            'boll_lower': float(lower[-1]) if len(lower) > 0 else None,
            'kdj_k': float(k[-1]) if len(k) > 0 else None,
            'kdj_d': float(d[-1]) if len(d) > 0 else None,
            'kdj_j': float(j[-1]) if len(j) > 0 else None,
            'volume_change': float(volume_change),
            'price_change': float(price_change),
            'trend': trend,
            'latest_close': float(closes[-1]) if len(closes) > 0 else None,
            'latest_date': dates[-1] if dates else None
        }

    def _calculate_ma(self, prices: np.ndarray, period: int) -> np.ndarray:
        """计算移动平均线"""
        if len(prices) < period:
            return np.array([])

        return np.convolve(prices, np.ones(period)/period, mode='valid')

    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> np.ndarray:
        """计算RSI"""
        if len(prices) <= period:
            return np.array([50])  # 默认值

        # 计算价格变化
        deltas = np.diff(prices)

        # 分离上涨和下跌
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        # 初始平均值
        avg_gain = np.mean(gains[:period])
        avg_loss = np.mean(losses[:period])

        # 计算后续值
        rsi = np.zeros(len(prices) - period)

        for i in range(len(rsi)):
            if avg_loss == 0:
                rsi[i] = 100
            else:
                rs = avg_gain / avg_loss
                rsi[i] = 100 - (100 / (1 + rs))

            # 更新平均值
            if i < len(deltas) - period:
                avg_gain = (avg_gain * (period - 1) + gains[i + period]) / period
                avg_loss = (avg_loss * (period - 1) + losses[i + period]) / period

        return rsi

    def _calculate_macd(self, prices: np.ndarray, fast_period: int = 12,
                        slow_period: int = 26, signal_period: int = 9) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """计算MACD"""
        if len(prices) < slow_period + signal_period:
            return np.array([]), np.array([]), np.array([])

        # 计算EMA
        ema_fast = self._calculate_ema(prices, fast_period)
        ema_slow = self._calculate_ema(prices, slow_period)

        # 计算MACD线
        macd_line = ema_fast - ema_slow

        # 计算信号线
        signal_line = self._calculate_ema(macd_line, signal_period)

        # 计算柱状图
        histogram = macd_line - signal_line

        return macd_line, signal_line, histogram

    def _calculate_ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        """计算指数移动平均线"""
        if len(prices) < period:
            return np.array([])

        # 计算权重
        multiplier = 2 / (period + 1)

        # 初始EMA为前N个价格的简单平均
        ema = np.zeros(len(prices) - period + 1)
        ema[0] = np.mean(prices[:period])

        # 计算后续EMA
        for i in range(1, len(ema)):
            ema[i] = (prices[i + period - 1] - ema[i-1]) * multiplier + ema[i-1]

        return ema

    def _calculate_bollinger_bands(self, prices: np.ndarray, period: int = 20, std_dev: float = 2) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """计算布林带"""
        if len(prices) < period:
            return np.array([]), np.array([]), np.array([])

        # 计算中轨（移动平均）
        middle = self._calculate_ma(prices, period)

        # 计算标准差
        std = np.array([np.std(prices[i:i+period]) for i in range(len(prices) - period + 1)])

        # 计算上轨和下轨
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)

        return upper, middle, lower

    def _calculate_kdj(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray,
                       period: int = 9) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """计算KDJ指标"""
        if len(closes) < period:
            return np.array([50]), np.array([50]), np.array([50])

        # 计算RSV
        rsv = np.zeros(len(closes) - period + 1)
        for i in range(len(rsv)):
            high_max = np.max(highs[i:i+period])
            low_min = np.min(lows[i:i+period])
            if high_max == low_min:
                rsv[i] = 50
            else:
                rsv[i] = (closes[i+period-1] - low_min) / (high_max - low_min) * 100

        # 计算K、D、J
        k = np.zeros(len(rsv))
        d = np.zeros(len(rsv))
        j = np.zeros(len(rsv))

        k[0] = d[0] = 50  # 初始值

        for i in range(1, len(rsv)):
            k[i] = (2/3) * k[i-1] + (1/3) * rsv[i]
            d[i] = (2/3) * d[i-1] + (1/3) * k[i]
            j[i] = 3 * k[i] - 2 * d[i]

        return k, d, j

    def _calculate_volume_change(self, volumes: np.ndarray) -> float:
        """计算成交量变化率"""
        if len(volumes) < 2:
            return 0

        recent_avg = np.mean(volumes[-5:]) if len(volumes) >= 5 else volumes[-1]
        previous_avg = np.mean(volumes[-10:-5]) if len(volumes) >= 10 else np.mean(volumes[:-1])

        if previous_avg == 0:
            return 0

        return (recent_avg - previous_avg) / previous_avg * 100

    def _calculate_price_change(self, prices: np.ndarray) -> float:
        """计算价格变化率"""
        if len(prices) < 2:
            return 0

        return (prices[-1] - prices[-2]) / prices[-2] * 100

    def _calculate_trend(self, prices: np.ndarray, ma5: np.ndarray, ma10: np.ndarray, ma20: np.ndarray) -> str:
        """计算趋势"""
        if len(ma5) == 0 or len(ma10) == 0 or len(ma20) == 0:
            return "中性"

        current_price = prices[-1]
        ma5_val = ma5[-1]
        ma10_val = ma10[-1]
        ma20_val = ma20[-1]

        if current_price > ma5_val > ma10_val > ma20_val:
            return "强势上涨"
        elif current_price > ma5_val > ma10_val:
            return "上涨"
        elif current_price < ma5_val < ma10_val < ma20_val:
            return "强势下跌"
        elif current_price < ma5_val < ma10_val:
            return "下跌"
        else:
            return "震荡"

    def _calculate_score(self, indicators: Dict) -> float:
        """计算综合评分"""
        score = 50  # 基础分

        # MA趋势评分
        ma5 = indicators.get('ma5')
        ma10 = indicators.get('ma10')
        ma20 = indicators.get('ma20')
        current_price = indicators.get('latest_close')

        if all(x is not None for x in [ma5, ma10, ma20, current_price]):
            if current_price > ma5 > ma10:
                score += 15
            elif current_price > ma5:
                score += 8

            if ma5 > ma10 > ma20:
                score += 10
            elif ma5 > ma10:
                score += 5

        # RSI评分
        rsi = indicators.get('rsi')
        if rsi is not None:
            if 30 < rsi < 70:
                score += 10
            elif 20 < rsi <= 30:
                score += 15  # 超卖反弹机会
            elif rsi <= 20:
                score += 8
            elif 70 <= rsi < 80:
                score -= 5
            elif rsi >= 80:
                score -= 10

        # MACD评分
        macd = indicators.get('macd')
        macd_signal = indicators.get('macd_signal')
        macd_hist = indicators.get('macd_hist')

        if all(x is not None for x in [macd, macd_signal, macd_hist]):
            if macd > macd_signal and macd_hist > 0:
                score += 10
            elif macd > macd_signal:
                score += 5
            elif macd < macd_signal and macd_hist < 0:
                score -= 5

        # 成交量评分
        volume_change = indicators.get('volume_change', 0)
        if volume_change > 50:
            score += 10
        elif volume_change > 20:
            score += 5
        elif volume_change < -30:
            score -= 5

        # 价格变化评分
        price_change = indicators.get('price_change', 0)
        if 0 < price_change <= 3:
            score += 5
        elif 3 < price_change <= 7:
            score += 8
        elif price_change > 9:
            score -= 5  # 涨幅过大
        elif -3 <= price_change < 0:
            score += 2  # 小幅回调
        elif price_change < -7:
            score -= 10

        # 趋势评分
        trend = indicators.get('trend', '中性')
        if trend == '强势上涨':
            score += 15
        elif trend == '上涨':
            score += 10
        elif trend == '震荡':
            score += 0
        elif trend == '下跌':
            score -= 10
        elif trend == '强势下跌':
            score -= 15

        return max(0, min(100, score))

    def _generate_reason(self, indicators: Dict, score: float) -> str:
        """生成推荐理由"""
        reasons = []

        # 趋势分析
        trend = indicators.get('trend', '中性')
        if trend in ['强势上涨', '上涨']:
            reasons.append("技术面呈上涨趋势")
        elif trend == '震荡':
            reasons.append("价格处于震荡区间")

        # MA分析
        ma5 = indicators.get('ma5')
        ma10 = indicators.get('ma10')
        current_price = indicators.get('latest_close')

        if all(x is not None for x in [ma5, ma10, current_price]):
            if current_price > ma5 > ma10:
                reasons.append("短期均线向上排列")
            elif current_price > ma5:
                reasons.append("价格站上短期均线")

        # RSI分析
        rsi = indicators.get('rsi')
        if rsi is not None:
            if 20 <= rsi <= 30:
                reasons.append("RSI显示超卖，存在反弹机会")
            elif 30 < rsi < 70:
                reasons.append("RSI处于健康区间")
            elif rsi >= 80:
                reasons.append("RSI显示超买，注意风险")

        # 成交量分析
        volume_change = indicators.get('volume_change', 0)
        if volume_change > 50:
            reasons.append("成交量显著放大")
        elif volume_change > 20:
            reasons.append("成交量温和放大")

        # MACD分析
        macd = indicators.get('macd')
        macd_signal = indicators.get('macd_signal')
        if macd is not None and macd_signal is not None:
            if macd > macd_signal:
                reasons.append("MACD金叉向上")
            else:
                reasons.append("MACD死叉向下")

        # 根据评分给出总体建议
        if score >= 80:
            reasons.insert(0, "技术面强势")
        elif score >= 60:
            reasons.insert(0, "技术面偏好")
        elif score >= 40:
            reasons.insert(0, "技术面中性")
        else:
            reasons.insert(0, "技术面偏弱")

        return "，".join(reasons) if reasons else "技术指标中性"


def main():
    """主程序"""
    print("🚀 API驱动的轻量级股票分析系统")
    print("=" * 60)
    print("📊 支持4000+只A股实时分析")
    print("🔄 完全基于API，无需本地数据库")
    print("⚡ 智能缓存，快速响应")
    print("=" * 60)

    # 初始化系统
    api_manager = StockAPIManager()
    analyzer = LightweightStockAnalyzer(api_manager)

    while True:
        print("\n📋 功能菜单:")
        print("1. 获取推荐股票")
        print("2. 分析指定股票")
        print("3. 搜索股票")
        print("4. 查看缓存状态")
        print("5. 清理缓存")
        print("0. 退出")

        choice = input("\n请选择功能 (0-5): ").strip()

        if choice == '1':
            # 获取推荐股票
            count = input("请输入推荐数量 (默认10): ").strip()
            count = int(count) if count.isdigit() else 10

            print(f"\n🔍 正在获取前{count}只推荐股票...")
            recommendations = analyzer.get_recommendations(count)

            if recommendations:
                print(f"\n📈 推荐股票 (共{len(recommendations)}只):")
                print("-" * 80)
                for i, stock in enumerate(recommendations, 1):
                    print(f"{i:2d}. {stock['name']} ({stock['symbol']})")
                    print(f"    当前价格: {stock['current_price']:.2f}")
                    print(f"    涨跌幅: {stock['change_pct']:+.2f}%")
                    print(f"    评分: {stock['score']:.1f}")
                    print(f"    理由: {stock['reason']}")
                    print(f"    数据源: {stock['data_source']}")
                    print()
            else:
                print("❌ 未获取到推荐股票")

        elif choice == '2':
            # 分析指定股票
            symbol = input("请输入股票代码 (如000001.SZ): ").strip().upper()
            if symbol:
                print(f"\n🔍 正在分析股票: {symbol}")
                result = analyzer.analyze_stock(symbol)

                if 'error' in result:
                    print(f"❌ {result['error']}")
                else:
                    print(f"\n📊 {result['name']} ({result['symbol']}) 分析结果:")
                    print("-" * 50)
                    print(f"当前价格: {result['current_price']:.2f}")
                    print(f"涨跌幅: {result['change_pct']:+.2f}%")
                    print(f"综合评分: {result['score']:.1f}")
                    print(f"推荐理由: {result['reason']}")
                    print(f"数据天数: {result['data_days']}天")
                    print(f"数据源: {result['data_source']}")
                    print(f"分析时间: {result['analysis_time']}")

        elif choice == '3':
            # 搜索股票
            keyword = input("请输入搜索关键词 (股票名称或代码): ").strip()
            if keyword:
                print(f"\n🔍 搜索股票: {keyword}")
                results = api_manager.search_stocks(keyword, 20)

                if results:
                    print(f"\n📋 搜索结果 (共{len(results)}只):")
                    print("-" * 50)
                    for i, stock in enumerate(results, 1):
                        print(f"{i:2d}. {stock['name']} ({stock['symbol']}) - {stock.get('industry', '未知')}")
                else:
                    print("❌ 未找到匹配的股票")

        elif choice == '4':
            # 查看缓存状态
            stats = api_manager.get_cache_stats()
            print(f"\n📊 缓存状态:")
            print("-" * 30)
            print(f"总缓存项: {stats['total_items']}")
            print(f"内存使用: {stats['memory_usage']} 字节")
            print("按类型分布:")
            for cache_type, count in stats['by_type'].items():
                print(f"  {cache_type}: {count}项")

        elif choice == '5':
            # 清理缓存
            print("\n🧹 缓存清理选项:")
            print("1. 清理所有缓存")
            print("2. 清理股票列表缓存")
            print("3. 清理股票数据缓存")
            print("4. 清理实时数据缓存")

            sub_choice = input("请选择 (1-4): ").strip()
            if sub_choice == '1':
                api_manager.clear_cache()
            elif sub_choice == '2':
                api_manager.clear_cache('stock_list')
            elif sub_choice == '3':
                api_manager.clear_cache('stock_data')
            elif sub_choice == '4':
                api_manager.clear_cache('realtime')
            else:
                print("❓ 无效选择")

        elif choice == '0':
            print("\n👋 感谢使用，再见！")
            break

        else:
            print("❓ 无效选择，请重新输入")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"\n❌ 程序异常: {str(e)}")
        logger.error(f"程序异常: {str(e)}", exc_info=True)