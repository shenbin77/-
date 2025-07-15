#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API驱动股票系统演示
Demo of API-Driven Stock System
"""

import numpy as np
from datetime import datetime, timedelta

# 模拟股票列表
STOCK_LIST = [
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

# 模拟推荐股票
RECOMMENDATIONS = [
    {
        'symbol': '000858.SZ',
        'name': '五粮液',
        'current_price': 152.75,
        'change_pct': 2.35,
        'score': 85.5,
        'reason': '技术面强势，短期均线向上排列，RSI处于健康区间，成交量温和放大'
    },
    {
        'symbol': '600519.SH',
        'name': '贵州茅台',
        'current_price': 1823.50,
        'change_pct': 1.28,
        'score': 82.3,
        'reason': '技术面强势，价格站上短期均线，MACD金叉向上，成交量显著放大'
    },
    {
        'symbol': '300750.SZ',
        'name': '宁德时代',
        'current_price': 187.65,
        'change_pct': 3.42,
        'score': 78.9,
        'reason': '技术面偏好，短期均线向上排列，RSI处于健康区间，成交量温和放大'
    },
    {
        'symbol': '002594.SZ',
        'name': '比亚迪',
        'current_price': 245.30,
        'change_pct': 2.15,
        'score': 76.2,
        'reason': '技术面偏好，价格站上短期均线，RSI处于健康区间'
    },
    {
        'symbol': '000333.SZ',
        'name': '美的集团',
        'current_price': 58.75,
        'change_pct': 1.56,
        'score': 72.8,
        'reason': '技术面偏好，短期均线向上排列，MACD金叉向上'
    },
    {
        'symbol': '002415.SZ',
        'name': '海康威视',
        'current_price': 32.45,
        'change_pct': 0.85,
        'score': 68.5,
        'reason': '技术面偏好，价格站上短期均线，RSI处于健康区间'
    },
    {
        'symbol': '601318.SH',
        'name': '中国平安',
        'current_price': 45.20,
        'change_pct': 1.12,
        'score': 65.3,
        'reason': '技术面偏好，短期均线向上排列，成交量温和放大'
    },
    {
        'symbol': '000063.SZ',
        'name': '中兴通讯',
        'current_price': 28.75,
        'change_pct': 0.95,
        'score': 62.7,
        'reason': '技术面偏好，价格站上短期均线，RSI处于健康区间'
    },
    {
        'symbol': '688981.SH',
        'name': '中芯国际',
        'current_price': 52.30,
        'change_pct': 1.75,
        'score': 61.5,
        'reason': '技术面偏好，短期均线向上排列，成交量温和放大'
    },
    {
        'symbol': '000002.SZ',
        'name': '万科A',
        'current_price': 15.85,
        'change_pct': 0.45,
        'score': 58.2,
        'reason': '技术面中性，价格站上短期均线，RSI处于健康区间'
    },
]

def demo_recommendations():
    """演示推荐股票功能"""
    print("\n📈 推荐股票 (共10只):")
    print("-" * 80)
    
    for i, stock in enumerate(RECOMMENDATIONS, 1):
        print(f"{i:2d}. {stock['name']} ({stock['symbol']})")
        print(f"    当前价格: {stock['current_price']:.2f}")
        print(f"    涨跌幅: {stock['change_pct']:+.2f}%")
        print(f"    评分: {stock['score']:.1f}")
        print(f"    理由: {stock['reason']}")
        print()

def demo_stock_analysis(symbol):
    """演示股票分析功能"""
    # 查找股票
    stock = None
    for s in RECOMMENDATIONS:
        if s['symbol'] == symbol:
            stock = s
            break
    
    if not stock:
        # 如果没找到，使用默认值
        stock = {
            'symbol': symbol,
            'name': next((s['name'] for s in STOCK_LIST if s['symbol'] == symbol), f"股票{symbol}"),
            'current_price': 45.67,
            'change_pct': 1.23,
            'score': 65.4,
            'reason': '技术面偏好，价格站上短期均线，RSI处于健康区间'
        }
    
    # 显示分析结果
    print(f"\n📊 {stock['name']} ({stock['symbol']}) 分析结果:")
    print("-" * 50)
    print(f"当前价格: {stock['current_price']:.2f}")
    print(f"涨跌幅: {stock['change_pct']:+.2f}%")
    print(f"综合评分: {stock['score']:.1f}")
    print(f"推荐理由: {stock['reason']}")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 显示技术指标
    print("\n📈 技术指标:")
    print(f"MA5: {stock['current_price'] * 0.98:.2f}")
    print(f"MA10: {stock['current_price'] * 0.96:.2f}")
    print(f"MA20: {stock['current_price'] * 0.94:.2f}")
    print(f"RSI: {min(70, max(30, 50 + stock['change_pct'] * 2)):.2f}")
    print(f"MACD: {0.15 if stock['change_pct'] > 0 else -0.15:.3f}")
    
    # 显示历史数据
    print("\n📅 最近5日行情:")
    today = datetime.now()
    for i in range(5):
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
        change = np.random.normal(0, 0.01)
        price = stock['current_price'] * (1 - i*0.005 - change)
        print(f"{date}: 收盘价 {price:.2f}, 涨跌幅 {change*100:+.2f}%")

def demo_search_stocks(keyword):
    """演示搜索股票功能"""
    # 搜索匹配的股票
    matched_stocks = []
    keyword_lower = keyword.lower()
    
    for stock in STOCK_LIST:
        # 检查股票代码或名称是否匹配
        if (keyword_lower in stock['symbol'].lower() or 
            keyword_lower in stock['name'].lower()):
            matched_stocks.append(stock)
    
    # 显示结果
    if matched_stocks:
        print(f"\n📋 搜索结果 (共{len(matched_stocks)}只):")
        print("-" * 50)
        for i, stock in enumerate(matched_stocks, 1):
            print(f"{i:2d}. {stock['name']} ({stock['symbol']}) - {stock['industry']}")
    else:
        print(f"\n❌ 未找到匹配 '{keyword}' 的股票")

def main():
    """主函数"""
    print("🚀 API驱动的轻量级股票分析系统 (演示版)")
    print("=" * 60)
    print("📊 支持4000+只A股实时分析")
    print("🔄 完全基于API，无需本地数据库")
    print("=" * 60)
    
    while True:
        print("\n📋 功能菜单:")
        print("1. 获取推荐股票")
        print("2. 分析指定股票")
        print("3. 搜索股票")
        print("0. 退出")
        
        choice = input("\n请选择功能 (0-3): ").strip()
        
        if choice == '1':
            # 获取推荐股票
            demo_recommendations()
        
        elif choice == '2':
            # 分析指定股票
            symbol = input("请输入股票代码 (如000001.SZ): ").strip().upper()
            if symbol:
                demo_stock_analysis(symbol)
        
        elif choice == '3':
            # 搜索股票
            keyword = input("请输入搜索关键词 (股票名称或代码): ").strip()
            if keyword:
                demo_search_stocks(keyword)
        
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
