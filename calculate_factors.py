#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
计算和存储因子值
"""

from app import create_app
from app.extensions import db
from app.services.factor_engine import FactorEngine
from datetime import datetime, timedelta
import pandas as pd
import random

def calculate_and_store_factors():
    """计算并存储因子值"""
    app = create_app()
    with app.app_context():
        try:
            print("🚀 开始计算因子值...")
            
            # 初始化因子引擎
            factor_engine = FactorEngine()

            # 获取股票列表
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT ts_code FROM stock_basic"))
                ts_codes = [row[0] for row in result.fetchall()]

            # 获取要计算的因子列表
            factor_ids = [
                'momentum_1d', 'momentum_5d', 'momentum_20d',
                'volatility_20d', 'volume_ratio_20d', 'price_to_ma20',
                'pe_percentile', 'pb_percentile', 'ps_percentile'
            ]

            print(f"📊 将为 {len(ts_codes)} 只股票计算 {len(factor_ids)} 个因子")
            
            # 计算最近6个月的因子值
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)
            
            # 按月计算，避免一次性计算太多数据
            current_date = start_date
            total_calculated = 0
            
            while current_date <= end_date:
                month_end = min(current_date + timedelta(days=30), end_date)
                
                print(f"📅 计算 {current_date.strftime('%Y-%m-%d')} 到 {month_end.strftime('%Y-%m-%d')} 的因子...")
                
                for factor_id in factor_ids:
                    try:
                        print(f"  🔍 计算因子: {factor_id}")
                        
                        # 计算因子值
                        result = factor_engine.calculate_factor(
                            factor_id=factor_id,
                            ts_codes=ts_codes,
                            start_date=current_date.strftime('%Y-%m-%d'),
                            end_date=month_end.strftime('%Y-%m-%d')
                        )
                        
                        if result and not result.empty:
                            # 存储因子值到数据库
                            with db.engine.connect() as conn:
                                for _, row in result.iterrows():
                                    conn.execute(db.text("""
                                        INSERT OR REPLACE INTO factor_values 
                                        (factor_id, ts_code, trade_date, factor_value, created_at)
                                        VALUES (:factor_id, :ts_code, :trade_date, :factor_value, :created_at)
                                    """), {
                                        'factor_id': row['factor_id'],
                                        'ts_code': row['ts_code'],
                                        'trade_date': row['trade_date'],
                                        'factor_value': float(row['factor_value']) if pd.notna(row['factor_value']) else None,
                                        'created_at': datetime.now()
                                    })
                                
                                conn.commit()
                            
                            calculated_count = len(result)
                            total_calculated += calculated_count
                            print(f"    ✅ {factor_id}: 计算了 {calculated_count} 个值")
                        else:
                            print(f"    ⚠️ {factor_id}: 无数据")
                            
                    except Exception as e:
                        print(f"    ❌ {factor_id}: 计算失败 - {e}")
                
                current_date = month_end + timedelta(days=1)
            
            print(f"✅ 因子计算完成！总共计算了 {total_calculated} 个因子值")
            
            # 验证存储的因子值
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT COUNT(*) FROM factor_values"))
                total_stored = result.fetchone()[0]
                
                result = conn.execute(db.text("SELECT COUNT(DISTINCT factor_id) FROM factor_values"))
                unique_factors = result.fetchone()[0]
                
                result = conn.execute(db.text("SELECT COUNT(DISTINCT ts_code) FROM factor_values"))
                unique_stocks = result.fetchone()[0]
                
                print(f"📊 存储验证:")
                print(f"  - 总因子值数量: {total_stored}")
                print(f"  - 因子种类数量: {unique_factors}")
                print(f"  - 股票数量: {unique_stocks}")
            
            return True
            
        except Exception as e:
            print(f"❌ 因子计算失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def create_factor_values_table():
    """创建因子值表"""
    app = create_app()
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                conn.execute(db.text("""
                    CREATE TABLE IF NOT EXISTS factor_values (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        factor_id VARCHAR(50) NOT NULL,
                        ts_code VARCHAR(20) NOT NULL,
                        trade_date DATE NOT NULL,
                        factor_value DECIMAL(20, 8),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(factor_id, ts_code, trade_date)
                    )
                """))
                
                # 创建索引
                conn.execute(db.text("""
                    CREATE INDEX IF NOT EXISTS idx_factor_values_factor_date 
                    ON factor_values(factor_id, trade_date)
                """))
                
                conn.execute(db.text("""
                    CREATE INDEX IF NOT EXISTS idx_factor_values_stock_date 
                    ON factor_values(ts_code, trade_date)
                """))
                
                conn.commit()
                
            print("✅ 因子值表创建成功")
            return True
            
        except Exception as e:
            print(f"❌ 创建因子值表失败: {e}")
            return False

def generate_sample_predictions():
    """生成示例预测数据以支持模型选股"""
    app = create_app()
    with app.app_context():
        try:
            print("🔮 生成示例预测数据...")
            
            with db.engine.connect() as conn:
                # 创建预测表
                conn.execute(db.text("""
                    CREATE TABLE IF NOT EXISTS ml_predictions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_id VARCHAR(50) NOT NULL,
                        ts_code VARCHAR(20) NOT NULL,
                        trade_date DATE NOT NULL,
                        predicted_return DECIMAL(10, 6),
                        confidence_score DECIMAL(5, 4),
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
                            # 生成随机预测值
                            predicted_return = round(random.uniform(-0.1, 0.1), 6)  # -10%到10%的预测收益
                            confidence_score = round(random.uniform(0.3, 0.9), 4)  # 30%到90%的置信度
                            
                            conn.execute(db.text("""
                                INSERT OR REPLACE INTO ml_predictions 
                                (model_id, ts_code, trade_date, predicted_return, confidence_score)
                                VALUES (:model_id, :ts_code, :trade_date, :predicted_return, :confidence_score)
                            """), {
                                'model_id': 'my_xgb_model',
                                'ts_code': ts_code,
                                'trade_date': trade_date,
                                'predicted_return': predicted_return,
                                'confidence_score': confidence_score
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

def main():
    """主函数"""
    
    print("🚀 开始因子计算和数据准备...")
    
    # 1. 创建因子值表
    if not create_factor_values_table():
        return False
    
    # 2. 计算因子值
    if not calculate_and_store_factors():
        return False
    
    # 3. 生成示例预测数据
    if not generate_sample_predictions():
        return False
    
    print("🎉 所有数据准备完成！")
    print("💡 现在可以测试因子选股和模型选股功能了")
    
    return True

if __name__ == "__main__":
    main()
