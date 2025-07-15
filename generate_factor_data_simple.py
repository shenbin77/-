#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单直接的因子数据和预测数据生成脚本
"""

from app import create_app
from app.extensions import db
from datetime import datetime, timedelta
import random
import pandas as pd
import numpy as np

def generate_factor_values():
    """直接生成因子值数据"""
    app = create_app()
    with app.app_context():
        try:
            print("🚀 开始生成因子值数据...")
            
            with db.engine.connect() as conn:
                # 获取股票列表
                result = conn.execute(db.text("SELECT ts_code FROM stock_basic"))
                stocks = [row[0] for row in result.fetchall()]
                
                # 因子列表
                factors = [
                    'momentum_1d', 'momentum_5d', 'momentum_20d',
                    'volatility_20d', 'volume_ratio_20d', 'price_to_ma20',
                    'pe_percentile', 'pb_percentile', 'ps_percentile'
                ]
                
                print(f"📊 为 {len(stocks)} 只股票生成 {len(factors)} 个因子的数据...")
                
                # 生成最近3个月的因子数据
                end_date = datetime.now()
                start_date = end_date - timedelta(days=90)
                
                total_generated = 0
                current_date = start_date
                
                while current_date <= end_date:
                    if current_date.weekday() < 5:  # 工作日
                        trade_date = current_date.strftime('%Y-%m-%d')
                        
                        for ts_code in stocks:
                            for factor_id in factors:
                                # 根据因子类型生成不同范围的值
                                if 'momentum' in factor_id:
                                    factor_value = round(random.uniform(-0.1, 0.1), 6)  # -10%到10%
                                elif 'volatility' in factor_id:
                                    factor_value = round(random.uniform(0.01, 0.5), 6)  # 1%到50%
                                elif 'volume_ratio' in factor_id:
                                    factor_value = round(random.uniform(0.5, 3.0), 6)  # 0.5到3倍
                                elif 'price_to_ma' in factor_id:
                                    factor_value = round(random.uniform(0.8, 1.2), 6)  # 80%到120%
                                elif 'percentile' in factor_id:
                                    factor_value = round(random.uniform(0, 100), 6)  # 0到100百分位
                                else:
                                    factor_value = round(random.uniform(-2, 2), 6)  # 标准化值
                                
                                # 插入因子值
                                conn.execute(db.text("""
                                    INSERT OR REPLACE INTO factor_values 
                                    (factor_id, ts_code, trade_date, factor_value, created_at)
                                    VALUES (:factor_id, :ts_code, :trade_date, :factor_value, :created_at)
                                """), {
                                    'factor_id': factor_id,
                                    'ts_code': ts_code,
                                    'trade_date': trade_date,
                                    'factor_value': factor_value,
                                    'created_at': datetime.now()
                                })
                                
                                total_generated += 1
                    
                    current_date += timedelta(days=1)
                
                conn.commit()
                
                print(f"✅ 生成了 {total_generated} 个因子值")
                
                # 验证数据
                result = conn.execute(db.text("SELECT COUNT(*) FROM factor_values"))
                total_stored = result.fetchone()[0]
                
                result = conn.execute(db.text("SELECT COUNT(DISTINCT factor_id) FROM factor_values"))
                unique_factors = result.fetchone()[0]
                
                print(f"📊 验证结果:")
                print(f"  - 总因子值: {total_stored}")
                print(f"  - 因子种类: {unique_factors}")
                
                return True
                
        except Exception as e:
            print(f"❌ 生成因子值失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def generate_ml_predictions():
    """生成ML模型预测数据"""
    app = create_app()
    with app.app_context():
        try:
            print("🔮 开始生成ML预测数据...")
            
            with db.engine.connect() as conn:
                # 重新创建预测表（修复字段问题）
                conn.execute(db.text("DROP TABLE IF EXISTS ml_predictions"))
                conn.execute(db.text("""
                    CREATE TABLE ml_predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_id VARCHAR(50) NOT NULL,
                        ts_code VARCHAR(20) NOT NULL,
                        trade_date DATE NOT NULL,
                        predicted_return DECIMAL(10, 6),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(model_id, ts_code, trade_date)
                    )
                """))
                
                # 获取股票列表
                result = conn.execute(db.text("SELECT ts_code FROM stock_basic"))
                stocks = [row[0] for row in result.fetchall()]
                
                # 生成最近30天的预测数据
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                
                current_date = start_date
                total_predictions = 0
                
                while current_date <= end_date:
                    if current_date.weekday() < 5:  # 工作日
                        trade_date = current_date.strftime('%Y-%m-%d')
                        
                        for ts_code in stocks:
                            # 生成预测收益率（基于正态分布，更真实）
                            predicted_return = round(np.random.normal(0, 0.03), 6)  # 均值0，标准差3%
                            predicted_return = max(-0.1, min(0.1, predicted_return))  # 限制在-10%到10%
                            
                            conn.execute(db.text("""
                                INSERT OR REPLACE INTO ml_predictions 
                                (model_id, ts_code, trade_date, predicted_return)
                                VALUES (:model_id, :ts_code, :trade_date, :predicted_return)
                            """), {
                                'model_id': 'my_xgb_model',
                                'ts_code': ts_code,
                                'trade_date': trade_date,
                                'predicted_return': predicted_return
                            })
                            
                            total_predictions += 1
                    
                    current_date += timedelta(days=1)
                
                conn.commit()
                
                print(f"✅ 生成了 {total_predictions} 个预测值")
                return True
                
        except Exception as e:
            print(f"❌ 生成预测数据失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def create_model_definitions():
    """创建模型定义数据"""
    app = create_app()
    with app.app_context():
        try:
            print("🤖 创建模型定义...")
            
            with db.engine.connect() as conn:
                # 创建模型定义表
                conn.execute(db.text("""
                    CREATE TABLE IF NOT EXISTS ml_model_definitions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_id VARCHAR(50) UNIQUE NOT NULL,
                        model_name VARCHAR(100) NOT NULL,
                        model_type VARCHAR(50) NOT NULL,
                        factor_list TEXT,
                        target_type VARCHAR(50),
                        is_trained BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                # 插入示例模型定义
                conn.execute(db.text("""
                    INSERT OR REPLACE INTO ml_model_definitions 
                    (model_id, model_name, model_type, factor_list, target_type, is_trained)
                    VALUES (:model_id, :model_name, :model_type, :factor_list, :target_type, :is_trained)
                """), {
                    'model_id': 'my_xgb_model',
                    'model_name': '我的XGBoost模型',
                    'model_type': 'xgboost',
                    'factor_list': 'momentum_1d,momentum_5d,volatility_20d',
                    'target_type': 'return_5d',
                    'is_trained': True
                })
                
                conn.commit()
                
                print("✅ 模型定义创建完成")
                return True
                
        except Exception as e:
            print(f"❌ 创建模型定义失败: {e}")
            return False

def main():
    """主函数"""
    print("🚀 开始生成多因子系统数据...")
    
    # 1. 生成因子值数据
    if not generate_factor_values():
        return False
    
    # 2. 生成ML预测数据
    if not generate_ml_predictions():
        return False
    
    # 3. 创建模型定义
    if not create_model_definitions():
        return False
    
    print("🎉 多因子系统数据生成完成！")
    print("💡 现在可以测试以下功能：")
    print("  - 计算因子值")
    print("  - 基于因子选股")
    print("  - 基于ML模型选股")
    print("  - 模型训练（有了基础数据支持）")
    
    return True

if __name__ == "__main__":
    main()
