#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成目标变量数据（未来收益率）
"""

from app import create_app
from app.extensions import db
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def generate_target_returns():
    """生成目标收益率数据"""
    app = create_app()
    with app.app_context():
        try:
            print("🎯 开始生成目标收益率数据...")
            
            with db.engine.connect() as conn:
                # 创建目标收益率表
                conn.execute(db.text("""
                    CREATE TABLE IF NOT EXISTS target_returns (
                        ts_code VARCHAR(20) NOT NULL,
                        trade_date DATE NOT NULL,
                        return_1d DECIMAL(10, 6),
                        return_5d DECIMAL(10, 6),
                        return_20d DECIMAL(10, 6),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (ts_code, trade_date)
                    )
                """))
                
                # 获取历史价格数据
                result = conn.execute(db.text("""
                    SELECT ts_code, trade_date, close 
                    FROM stock_daily_history 
                    ORDER BY ts_code, trade_date
                """))
                
                price_data = pd.DataFrame(result.fetchall(), columns=['ts_code', 'trade_date', 'close'])
                
                if price_data.empty:
                    print("❌ 没有历史价格数据")
                    return False
                
                print(f"📊 处理 {len(price_data)} 条价格数据...")
                
                # 按股票分组计算收益率
                target_data = []
                
                for ts_code in price_data['ts_code'].unique():
                    stock_data = price_data[price_data['ts_code'] == ts_code].copy()
                    stock_data = stock_data.sort_values('trade_date')
                    stock_data['close'] = pd.to_numeric(stock_data['close'])
                    
                    # 计算不同期间的收益率
                    stock_data['return_1d'] = stock_data['close'].pct_change(1)
                    stock_data['return_5d'] = stock_data['close'].pct_change(5)
                    stock_data['return_20d'] = stock_data['close'].pct_change(20)
                    
                    # 向前移动，使其成为未来收益率
                    stock_data['future_return_1d'] = stock_data['return_1d'].shift(-1)
                    stock_data['future_return_5d'] = stock_data['return_5d'].shift(-5)
                    stock_data['future_return_20d'] = stock_data['return_20d'].shift(-20)
                    
                    # 添加到结果列表
                    for _, row in stock_data.iterrows():
                        if pd.notna(row['future_return_1d']) or pd.notna(row['future_return_5d']) or pd.notna(row['future_return_20d']):
                            target_data.append({
                                'ts_code': row['ts_code'],
                                'trade_date': row['trade_date'],
                                'return_1d': row['future_return_1d'] if pd.notna(row['future_return_1d']) else None,
                                'return_5d': row['future_return_5d'] if pd.notna(row['future_return_5d']) else None,
                                'return_20d': row['future_return_20d'] if pd.notna(row['future_return_20d']) else None
                            })
                
                print(f"📈 生成了 {len(target_data)} 条目标收益率数据")
                
                # 批量插入数据
                for data in target_data:
                    conn.execute(db.text("""
                        INSERT OR REPLACE INTO target_returns 
                        (ts_code, trade_date, return_1d, return_5d, return_20d)
                        VALUES (:ts_code, :trade_date, :return_1d, :return_5d, :return_20d)
                    """), data)
                
                conn.commit()
                
                # 验证数据
                result = conn.execute(db.text("SELECT COUNT(*) FROM target_returns"))
                total_targets = result.fetchone()[0]
                
                result = conn.execute(db.text("""
                    SELECT COUNT(*) FROM target_returns 
                    WHERE return_5d IS NOT NULL
                """))
                valid_5d = result.fetchone()[0]
                
                print(f"✅ 目标收益率数据生成完成")
                print(f"📊 验证结果:")
                print(f"  - 总记录数: {total_targets}")
                print(f"  - 有效5日收益率: {valid_5d}")
                
                return True
                
        except Exception as e:
            print(f"❌ 生成目标收益率数据失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def create_training_dataset():
    """创建完整的训练数据集"""
    app = create_app()
    with app.app_context():
        try:
            print("🔗 创建完整训练数据集...")
            
            with db.engine.connect() as conn:
                # 创建训练数据集视图
                conn.execute(db.text("""
                    CREATE VIEW IF NOT EXISTS training_dataset AS
                    SELECT 
                        f.ts_code,
                        f.trade_date,
                        f.factor_id,
                        f.factor_value,
                        t.return_1d,
                        t.return_5d,
                        t.return_20d
                    FROM factor_values f
                    LEFT JOIN target_returns t ON f.ts_code = t.ts_code AND f.trade_date = t.trade_date
                    WHERE f.factor_value IS NOT NULL
                """))
                
                # 测试查询
                result = conn.execute(db.text("""
                    SELECT COUNT(*) FROM training_dataset 
                    WHERE return_5d IS NOT NULL
                """))
                
                valid_training_samples = result.fetchone()[0]
                
                print(f"✅ 训练数据集创建完成")
                print(f"📊 可用训练样本: {valid_training_samples}")
                
                # 显示一些示例数据
                result = conn.execute(db.text("""
                    SELECT ts_code, trade_date, factor_id, factor_value, return_5d
                    FROM training_dataset 
                    WHERE return_5d IS NOT NULL 
                    LIMIT 10
                """))
                
                samples = result.fetchall()
                print(f"📋 示例数据:")
                for sample in samples[:5]:
                    print(f"  {sample[0]} {sample[1]} {sample[2]}: {sample[3]:.6f} -> {sample[4]:.6f}")
                
                return True
                
        except Exception as e:
            print(f"❌ 创建训练数据集失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def fix_factor_data_dates():
    """修复因子数据的日期格式"""
    app = create_app()
    with app.app_context():
        try:
            print("📅 修复因子数据日期格式...")
            
            with db.engine.connect() as conn:
                # 检查当前日期格式
                result = conn.execute(db.text("SELECT trade_date FROM factor_values LIMIT 5"))
                sample_dates = [row[0] for row in result.fetchall()]
                
                print(f"当前日期样本: {sample_dates}")
                
                # 确保日期格式一致
                conn.execute(db.text("""
                    UPDATE factor_values 
                    SET trade_date = DATE(trade_date)
                    WHERE trade_date IS NOT NULL
                """))
                
                conn.commit()
                
                print("✅ 因子数据日期格式修复完成")
                return True
                
        except Exception as e:
            print(f"❌ 修复日期格式失败: {e}")
            return False

def main():
    """主函数"""
    print("🚀 开始生成训练所需的目标数据...")
    
    # 1. 修复因子数据日期格式
    if not fix_factor_data_dates():
        return False
    
    # 2. 生成目标收益率数据
    if not generate_target_returns():
        return False
    
    # 3. 创建训练数据集
    if not create_training_dataset():
        return False
    
    print("🎉 训练数据准备完成！")
    print("💡 现在可以测试模型训练功能了")
    
    return True

if __name__ == "__main__":
    main()
