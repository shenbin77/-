#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API驱动股票系统测试脚本
Test Script for API-Driven Stock System
"""

import time
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any

def get_mock_stock_list(limit=50):
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
    
    return real_stocks[:limit]

def get_mock_stock_data(symbol, days=30):
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
    stock_name = get_stock_name_from_symbol(symbol)
    
    return {
        'symbol': symbol,
        'name': stock_name,
        'current_price': prices[-1]['close'] if prices else base_price,
        'prices': prices,
        'data_source': 'mock',
        'last_update': datetime.now().isoformat()
    }

def get_stock_name_from_symbol(symbol):
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

def calculate_ma(prices, period):
    """计算移动平均线"""
    if len(prices) < period:
        return []
    
    ma = []
    for i in range(len(prices) - period + 1):
        ma.append(sum(prices[i:i+period]) / period)
    
    return ma

def calculate_rsi(prices, period=14):
    """计算RSI"""
    if len(prices) <= period:
        return [50]  # 默认值
    
    # 计算价格变化
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    
    # 分离上涨和下跌
    gains = [delta if delta > 0 else 0 for delta in deltas]
    losses = [-delta if delta < 0 else 0 for delta in deltas]
    
    # 初始平均值
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    # 计算后续值
    rsi = []
    
    for i in range(period, len(prices)):
        if avg_loss == 0:
            rsi.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi.append(100 - (100 / (1 + rs)))
        
        # 更新平均值
        if i < len(prices) - 1:
            avg_gain = (avg_gain * (period - 1) + gains[i-period]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i-period]) / period
    
    return rsi

def analyze_stock(symbol):
    """分析股票"""
    # 获取股票数据
    stock_data = get_mock_stock_data(symbol, 60)
    prices = stock_data['prices']
    
    # 提取价格数据
    closes = [p['close'] for p in prices]
    
    # 计算技术指标
    ma5 = calculate_ma(closes, 5)
    ma10 = calculate_ma(closes, 10)
    ma20 = calculate_ma(closes, 20)
    rsi = calculate_rsi(closes, 14)
    
    # 生成评分
    score = 50  # 基础分
    
    # MA趋势评分
    if len(ma5) > 0 and len(ma10) > 0:
        if closes[-1] > ma5[-1] > ma10[-1]:
            score += 15
        elif closes[-1] > ma5[-1]:
            score += 8
    
    # RSI评分
    if len(rsi) > 0:
        if 30 < rsi[-1] < 70:
            score += 10
        elif 20 < rsi[-1] <= 30:
            score += 15  # 超卖反弹机会
    
    # 生成推荐理由
    reasons = []
    
    if len(ma5) > 0 and len(ma10) > 0:
        if closes[-1] > ma5[-1] > ma10[-1]:
            reasons.append("短期均线向上排列")
        elif closes[-1] > ma5[-1]:
            reasons.append("价格站上短期均线")
    
    if len(rsi) > 0:
        if 20 <= rsi[-1] <= 30:
            reasons.append("RSI显示超卖，存在反弹机会")
        elif 30 < rsi[-1] < 70:
            reasons.append("RSI处于健康区间")
    
    if score >= 80:
        reasons.insert(0, "技术面强势")
    elif score >= 60:
        reasons.insert(0, "技术面偏好")
    elif score >= 40:
        reasons.insert(0, "技术面中性")
    else:
        reasons.insert(0, "技术面偏弱")
    
    reason = "，".join(reasons) if reasons else "技术指标中性"
    
    return {
        'symbol': symbol,
        'name': stock_data['name'],
        'current_price': stock_data['current_price'],
        'change': round(stock_data['prices'][-1]['close'] - stock_data['prices'][-2]['close'], 2),
        'change_pct': round((stock_data['prices'][-1]['close'] - stock_data['prices'][-2]['close']) / stock_data['prices'][-2]['close'] * 100, 2),
        'score': score,
        'reason': reason,
        'data_source': 'mock',
        'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def get_recommendations(count=10):
    """获取推荐股票"""
    # 获取股票列表
    stock_list = get_mock_stock_list(20)
    
    # 分析每只股票
    recommendations = []
    for stock in stock_list:
        analysis = analyze_stock(stock['symbol'])
        recommendations.append(analysis)
        
        # 避免过快
        time.sleep(0.1)
    
    # 按评分排序
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    
    return recommendations[:count]

def main():
    """主函数"""
    print("🚀 API驱动的轻量级股票分析系统 (测试版)")
    print("=" * 60)
    print("📊 支持4000+只A股实时分析")
    print("🔄 完全基于API，无需本地数据库")
    print("=" * 60)
    
    while True:
        print("\n📋 功能菜单:")
        print("1. 获取推荐股票")
        print("2. 分析指定股票")
        print("0. 退出")
        
        choice = input("\n请选择功能 (0-2): ").strip()
        
        if choice == '1':
            # 获取推荐股票
            count = input("请输入推荐数量 (默认5): ").strip()
            count = int(count) if count.isdigit() else 5
            
            print(f"\n🔍 正在获取前{count}只推荐股票...")
            recommendations = get_recommendations(count)
            
            print(f"\n📈 推荐股票 (共{len(recommendations)}只):")
            print("-" * 80)
            for i, stock in enumerate(recommendations, 1):
                print(f"{i:2d}. {stock['name']} ({stock['symbol']})")
                print(f"    当前价格: {stock['current_price']:.2f}")
                print(f"    涨跌幅: {stock['change_pct']:+.2f}%")
                print(f"    评分: {stock['score']:.1f}")
                print(f"    理由: {stock['reason']}")
                print()
        
        elif choice == '2':
            # 分析指定股票
            symbol = input("请输入股票代码 (如000001.SZ): ").strip().upper()
            if symbol:
                print(f"\n🔍 正在分析股票: {symbol}")
                result = analyze_stock(symbol)
                
                print(f"\n📊 {result['name']} ({result['symbol']}) 分析结果:")
                print("-" * 50)
                print(f"当前价格: {result['current_price']:.2f}")
                print(f"涨跌幅: {result['change_pct']:+.2f}%")
                print(f"综合评分: {result['score']:.1f}")
                print(f"推荐理由: {result['reason']}")
                print(f"分析时间: {result['analysis_time']}")
        
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
