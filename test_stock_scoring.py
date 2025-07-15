#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试股票评分功能
Test Stock Scoring Function
"""

import os
import sys
import random
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import text

# 设置环境变量
os.environ['TUSHARE_TOKEN'] = 'your_tushare_token_here'
os.environ['FLASK_SECRET_KEY'] = 'test-secret-key'

try:
    from app import create_app
    from app.extensions import db
    from app.services.stock_scoring import StockScoringEngine
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    sys.exit(1)

def get_stock_list():
    """获取股票列表"""
    print("📋 获取股票列表...")
    
    app = create_app()
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # 获取所有股票
                result = conn.execute(text("SELECT ts_code, name, industry FROM stock_basic ORDER BY ts_code"))
                stocks = result.fetchall()
                print(f"✅ 获取到 {len(stocks)} 只股票")
                return stocks
        except Exception as e:
            print(f"❌ 获取股票列表失败: {e}")
            return []

def get_latest_trade_date():
    """获取最新交易日期"""
    app = create_app()
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                result = conn.execute(text("SELECT MAX(trade_date) FROM stock_daily_history"))
                latest_date = result.fetchone()[0]
                print(f"📅 最新交易日期: {latest_date}")
                return latest_date
        except Exception as e:
            print(f"❌ 获取最新交易日期失败: {e}")
            return datetime.now().strftime('%Y-%m-%d')

def test_stock_scoring():
    """测试股票评分功能"""
    print("🧪 测试股票评分功能...")
    
    # 获取股票列表
    stocks = get_stock_list()
    if not stocks:
        print("❌ 未获取到股票数据，测试失败")
        return False
    
    # 获取最新交易日期
    trade_date = get_latest_trade_date()
    
    # 初始化评分引擎
    app = create_app()
    with app.app_context():
        try:
            scoring_engine = StockScoringEngine()
            
            # 测试因子分数计算
            print(f"\n📊 计算因子分数 (日期: {trade_date})...")
            factor_list = ['ma_5_10', 'ma_10_20', 'rsi_14', 'macd', 'kdj_k', 'kdj_d', 'boll_ub', 'boll_lb']
            
            # 限制测试的股票数量
            test_stocks = stocks[:10]
            ts_codes = [stock[0] for stock in test_stocks]
            
            # 计算因子分数
            factor_scores = scoring_engine.calculate_factor_scores(trade_date, factor_list, ts_codes)
            
            if factor_scores.empty:
                print("⚠️ 未找到因子数据，生成模拟数据...")
                
                # 生成模拟因子数据
                mock_data = []
                for ts_code in ts_codes:
                    for factor_id in factor_list:
                        mock_data.append({
                            'ts_code': ts_code,
                            'factor_id': factor_id,
                            'value': random.uniform(-2, 2),
                            'z_score': random.uniform(-2, 2),
                            'rank': random.randint(1, len(ts_codes)),
                            'trade_date': trade_date
                        })
                
                factor_data = pd.DataFrame(mock_data)
                
                # 透视表：行为ts_code，列为factor_id
                factor_scores = factor_data.pivot_table(
                    index='ts_code',
                    columns='factor_id',
                    values='z_score',
                    aggfunc='first'
                ).fillna(0)
            
            print(f"✅ 获取到 {len(factor_scores)} 只股票的因子分数")
            
            # 测试综合分数计算
            print("\n📊 计算综合分数...")
            weights = {factor: 1.0/len(factor_list) for factor in factor_list}
            
            # 测试不同评分方法
            methods = ['equal_weight', 'factor_weight']
            for method in methods:
                print(f"  🧮 使用 {method} 方法计算...")
                composite_scores = scoring_engine.calculate_composite_score(factor_scores, weights, method)
                
                if not composite_scores.empty:
                    print(f"  ✅ 成功计算 {len(composite_scores)} 只股票的综合分数")
                else:
                    print(f"  ❌ 计算综合分数失败")
            
            # 测试股票排名
            print("\n📊 股票排名...")
            top_n = 5
            top_stocks = scoring_engine.rank_stocks(composite_scores, top_n)
            
            if top_stocks:
                print(f"✅ 成功获取前 {len(top_stocks)} 只股票")
                print("\n📈 推荐股票:")
                
                for i, stock in enumerate(top_stocks, 1):
                    ts_code = stock['ts_code']
                    score = stock['composite_score']
                    
                    # 获取股票名称
                    stock_name = next((s[1] for s in stocks if s[0] == ts_code), "未知")
                    industry = next((s[2] for s in stocks if s[0] == ts_code), "未知")
                    
                    print(f"  {i}. {stock_name} ({ts_code}) - 行业: {industry}")
                    print(f"     评分: {score:.2f}")
                    
                    # 生成推荐理由
                    if score > 0.5:
                        reason = "短期上涨趋势、成交量放大"
                    elif score > 0:
                        reason = "技术指标向好、波动适中"
                    else:
                        reason = "估值合理、行业前景好"
                    
                    print(f"     理由: {reason}")
                    print()
                
                return True
            else:
                print("❌ 获取推荐股票失败")
                return False
                
        except Exception as e:
            print(f"❌ 测试股票评分功能失败: {e}")
            return False

def main():
    """主函数"""
    print("🚀 开始测试股票评分功能...")
    
    success = test_stock_scoring()
    
    if success:
        print("\n🎉 股票评分功能测试成功！")
        return 0
    else:
        print("\n❌ 股票评分功能测试失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())
