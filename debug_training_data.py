#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试训练数据问题
"""

from app import create_app
from app.extensions import db
import pandas as pd

def debug_training_data():
    """调试训练数据"""
    app = create_app()
    with app.app_context():
        try:
            print("🔍 调试训练数据...")
            
            with db.engine.connect() as conn:
                # 1. 检查因子数据的日期范围
                result = conn.execute(db.text("""
                    SELECT MIN(trade_date) as min_date, MAX(trade_date) as max_date, COUNT(*) as count
                    FROM factor_values
                """))
                factor_range = result.fetchone()
                print(f"📊 因子数据范围: {factor_range[0]} 到 {factor_range[1]}, 总数: {factor_range[2]}")
                
                # 2. 检查目标收益率数据的日期范围
                result = conn.execute(db.text("""
                    SELECT MIN(trade_date) as min_date, MAX(trade_date) as max_date, COUNT(*) as count
                    FROM target_returns
                    WHERE return_5d IS NOT NULL
                """))
                target_range = result.fetchone()
                print(f"🎯 目标数据范围: {target_range[0]} 到 {target_range[1]}, 总数: {target_range[2]}")
                
                # 3. 检查特定模型的因子数据
                model_factors = ['momentum_1d', 'momentum_5d', 'volatility_20d']
                result = conn.execute(db.text("""
                    SELECT factor_id, COUNT(*) as count, MIN(trade_date) as min_date, MAX(trade_date) as max_date
                    FROM factor_values
                    WHERE factor_id IN ('momentum_1d', 'momentum_5d', 'volatility_20d')
                    GROUP BY factor_id
                """))
                
                print(f"📈 模型因子数据详情:")
                for row in result.fetchall():
                    print(f"  {row[0]}: {row[1]} 条记录, {row[2]} 到 {row[3]}")
                
                # 4. 检查训练数据集的可用性
                result = conn.execute(db.text("""
                    SELECT COUNT(*) as total_samples
                    FROM factor_values f
                    JOIN target_returns t ON f.ts_code = t.ts_code AND f.trade_date = t.trade_date
                    WHERE f.factor_id IN ('momentum_1d', 'momentum_5d', 'volatility_20d')
                    AND t.return_5d IS NOT NULL
                    AND f.factor_value IS NOT NULL
                """))
                
                training_samples = result.fetchone()[0]
                print(f"🔗 可用训练样本: {training_samples}")
                
                # 5. 检查2023年的数据
                result = conn.execute(db.text("""
                    SELECT COUNT(*) as samples_2023
                    FROM factor_values f
                    JOIN target_returns t ON f.ts_code = t.ts_code AND f.trade_date = t.trade_date
                    WHERE f.factor_id IN ('momentum_1d', 'momentum_5d', 'volatility_20d')
                    AND t.return_5d IS NOT NULL
                    AND f.factor_value IS NOT NULL
                    AND f.trade_date >= '2023-01-01' AND f.trade_date <= '2023-12-31'
                """))
                
                samples_2023 = result.fetchone()[0]
                print(f"📅 2023年训练样本: {samples_2023}")
                
                # 6. 如果2023年没有数据，检查实际可用的日期范围
                if samples_2023 == 0:
                    result = conn.execute(db.text("""
                        SELECT MIN(f.trade_date) as min_date, MAX(f.trade_date) as max_date
                        FROM factor_values f
                        JOIN target_returns t ON f.ts_code = t.ts_code AND f.trade_date = t.trade_date
                        WHERE f.factor_id IN ('momentum_1d', 'momentum_5d', 'volatility_20d')
                        AND t.return_5d IS NOT NULL
                        AND f.factor_value IS NOT NULL
                    """))
                    
                    actual_range = result.fetchone()
                    print(f"📊 实际可用数据范围: {actual_range[0]} 到 {actual_range[1]}")
                    
                    # 使用实际可用的日期范围测试
                    if actual_range[0] and actual_range[1]:
                        result = conn.execute(db.text("""
                            SELECT COUNT(*) as samples_actual
                            FROM factor_values f
                            JOIN target_returns t ON f.ts_code = t.ts_code AND f.trade_date = t.trade_date
                            WHERE f.factor_id IN ('momentum_1d', 'momentum_5d', 'volatility_20d')
                            AND t.return_5d IS NOT NULL
                            AND f.factor_value IS NOT NULL
                            AND f.trade_date >= :start_date AND f.trade_date <= :end_date
                        """), {
                            'start_date': actual_range[0],
                            'end_date': actual_range[1]
                        })
                        
                        samples_actual = result.fetchone()[0]
                        print(f"✅ 实际范围内训练样本: {samples_actual}")
                        
                        # 显示一些样本数据
                        result = conn.execute(db.text("""
                            SELECT f.ts_code, f.trade_date, f.factor_id, f.factor_value, t.return_5d
                            FROM factor_values f
                            JOIN target_returns t ON f.ts_code = t.ts_code AND f.trade_date = t.trade_date
                            WHERE f.factor_id IN ('momentum_1d', 'momentum_5d', 'volatility_20d')
                            AND t.return_5d IS NOT NULL
                            AND f.factor_value IS NOT NULL
                            LIMIT 10
                        """))
                        
                        samples = result.fetchall()
                        print(f"📋 样本数据:")
                        for sample in samples[:5]:
                            print(f"  {sample[0]} {sample[1]} {sample[2]}: {sample[3]:.6f} -> {sample[4]:.6f}")
                
                return True
                
        except Exception as e:
            print(f"❌ 调试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_training_with_actual_dates():
    """使用实际可用的日期测试训练"""
    app = create_app()
    with app.app_context():
        try:
            print("\n🧪 使用实际日期测试训练...")
            
            from app.services.ml_models import MLModelManager
            
            ml_manager = MLModelManager()
            
            # 获取实际可用的日期范围
            with db.engine.connect() as conn:
                result = conn.execute(db.text("""
                    SELECT MIN(f.trade_date) as min_date, MAX(f.trade_date) as max_date
                    FROM factor_values f
                    JOIN target_returns t ON f.ts_code = t.ts_code AND f.trade_date = t.trade_date
                    WHERE f.factor_id IN ('momentum_1d', 'momentum_5d', 'volatility_20d')
                    AND t.return_5d IS NOT NULL
                    AND f.factor_value IS NOT NULL
                """))
                
                date_range = result.fetchone()
                
                if date_range[0] and date_range[1]:
                    start_date = str(date_range[0])
                    end_date = str(date_range[1])
                    
                    print(f"📅 使用日期范围: {start_date} 到 {end_date}")
                    
                    # 准备训练数据
                    X, y = ml_manager.prepare_training_data('my_xgb_model', start_date, end_date)
                    
                    print(f"📊 训练数据形状: X={X.shape if not X.empty else 'Empty'}, y={y.shape if not y.empty else 'Empty'}")
                    
                    if not X.empty and not y.empty:
                        print(f"✅ 训练数据准备成功！")
                        print(f"📈 特征列: {list(X.columns)}")
                        print(f"🎯 目标变量统计: 均值={y.mean():.6f}, 标准差={y.std():.6f}")
                        return True
                    else:
                        print(f"❌ 训练数据为空")
                        return False
                else:
                    print(f"❌ 无法获取有效日期范围")
                    return False
                
        except Exception as e:
            print(f"❌ 测试训练失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """主函数"""
    print("🚀 开始调试训练数据问题...")
    
    # 1. 调试训练数据
    debug_training_data()
    
    # 2. 测试实际日期的训练
    test_training_with_actual_dates()
    
    print("\n🎉 调试完成！")

if __name__ == "__main__":
    main()
