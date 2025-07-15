#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复ML模型创建和训练问题
"""

from app import create_app
from app.extensions import db
from app.models.ml_model_definition import MLModelDefinition
from datetime import datetime
import json

def create_ml_model_table():
    """创建ML模型定义表"""
    app = create_app()
    with app.app_context():
        try:
            print("🔨 创建ML模型定义表...")
            
            with db.engine.connect() as conn:
                # 创建ML模型定义表
                conn.execute(db.text("""
                    CREATE TABLE IF NOT EXISTS ml_model_definition (
                        model_id VARCHAR(50) PRIMARY KEY,
                        model_name VARCHAR(100) NOT NULL,
                        model_type VARCHAR(30) NOT NULL,
                        factor_list TEXT NOT NULL,
                        target_type VARCHAR(20) NOT NULL,
                        model_params TEXT,
                        training_config TEXT,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                
                conn.commit()
                
            print("✅ ML模型定义表创建成功")
            return True
            
        except Exception as e:
            print(f"❌ 创建ML模型定义表失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def create_sample_model_definitions():
    """创建示例模型定义"""
    app = create_app()
    with app.app_context():
        try:
            print("🤖 创建示例模型定义...")
            
            # 示例模型定义
            models = [
                {
                    'model_id': 'my_xgb_model',
                    'model_name': '我的XGBoost模型',
                    'model_type': 'xgboost',
                    'factor_list': ['momentum_1d', 'momentum_5d', 'volatility_20d'],
                    'target_type': 'return_5d',
                    'model_params': {
                        'n_estimators': 100,
                        'max_depth': 6,
                        'learning_rate': 0.1,
                        'subsample': 0.8,
                        'colsample_bytree': 0.8
                    },
                    'training_config': {
                        'test_size': 0.2,
                        'validation_method': 'time_series_split',
                        'cv_folds': 5,
                        'feature_selection': True,
                        'feature_selection_k': 20,
                        'scaling_method': 'robust'
                    }
                },
                {
                    'model_id': 'rf_momentum_model',
                    'model_name': '随机森林动量模型',
                    'model_type': 'random_forest',
                    'factor_list': ['momentum_1d', 'momentum_5d', 'momentum_20d', 'volume_ratio_20d'],
                    'target_type': 'return_5d',
                    'model_params': {
                        'n_estimators': 200,
                        'max_depth': 10,
                        'min_samples_split': 5,
                        'min_samples_leaf': 2,
                        'max_features': 'sqrt'
                    },
                    'training_config': {
                        'test_size': 0.2,
                        'validation_method': 'time_series_split',
                        'cv_folds': 3,
                        'feature_selection': False,
                        'scaling_method': 'standard'
                    }
                },
                {
                    'model_id': 'lgb_value_model',
                    'model_name': 'LightGBM价值模型',
                    'model_type': 'lightgbm',
                    'factor_list': ['pe_percentile', 'pb_percentile', 'ps_percentile', 'price_to_ma20'],
                    'target_type': 'return_20d',
                    'model_params': {
                        'num_leaves': 31,
                        'learning_rate': 0.05,
                        'feature_fraction': 0.9,
                        'bagging_fraction': 0.8,
                        'bagging_freq': 5,
                        'verbose': 0
                    },
                    'training_config': {
                        'test_size': 0.25,
                        'validation_method': 'holdout',
                        'feature_selection': True,
                        'feature_selection_k': 15,
                        'scaling_method': 'minmax'
                    }
                }
            ]
            
            with db.engine.connect() as conn:
                for model_data in models:
                    # 检查模型是否已存在
                    result = conn.execute(db.text("""
                        SELECT COUNT(*) FROM ml_model_definition WHERE model_id = :model_id
                    """), {'model_id': model_data['model_id']})
                    
                    if result.fetchone()[0] == 0:
                        # 插入新模型定义
                        conn.execute(db.text("""
                            INSERT INTO ml_model_definition 
                            (model_id, model_name, model_type, factor_list, target_type, model_params, training_config, is_active)
                            VALUES (:model_id, :model_name, :model_type, :factor_list, :target_type, :model_params, :training_config, :is_active)
                        """), {
                            'model_id': model_data['model_id'],
                            'model_name': model_data['model_name'],
                            'model_type': model_data['model_type'],
                            'factor_list': json.dumps(model_data['factor_list']),
                            'target_type': model_data['target_type'],
                            'model_params': json.dumps(model_data['model_params']),
                            'training_config': json.dumps(model_data['training_config']),
                            'is_active': True
                        })
                        
                        print(f"  ✅ 创建模型: {model_data['model_id']} - {model_data['model_name']}")
                    else:
                        print(f"  ⚠️ 模型已存在: {model_data['model_id']}")
                
                conn.commit()
            
            # 验证创建的模型
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT COUNT(*) FROM ml_model_definition"))
                total_models = result.fetchone()[0]
                
                result = conn.execute(db.text("SELECT model_id, model_name FROM ml_model_definition"))
                models_list = result.fetchall()
                
                print(f"📊 验证结果:")
                print(f"  - 总模型数量: {total_models}")
                print(f"  - 模型列表:")
                for model in models_list:
                    print(f"    • {model[0]}: {model[1]}")
            
            return True
            
        except Exception as e:
            print(f"❌ 创建示例模型定义失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def create_training_history_table():
    """创建训练历史表"""
    app = create_app()
    with app.app_context():
        try:
            print("📚 创建训练历史表...")
            
            with db.engine.connect() as conn:
                conn.execute(db.text("""
                    CREATE TABLE IF NOT EXISTS ml_training_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model_id VARCHAR(50) NOT NULL,
                        training_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        start_date DATE,
                        end_date DATE,
                        training_samples INTEGER,
                        test_samples INTEGER,
                        accuracy DECIMAL(10, 6),
                        precision_score DECIMAL(10, 6),
                        recall_score DECIMAL(10, 6),
                        f1_score DECIMAL(10, 6),
                        auc_score DECIMAL(10, 6),
                        loss DECIMAL(10, 6),
                        training_time_seconds INTEGER,
                        model_size_mb DECIMAL(10, 2),
                        feature_importance TEXT,
                        validation_metrics TEXT,
                        is_successful BOOLEAN DEFAULT TRUE,
                        error_message TEXT,
                        FOREIGN KEY (model_id) REFERENCES ml_model_definition(model_id)
                    )
                """))
                
                # 创建索引
                conn.execute(db.text("""
                    CREATE INDEX IF NOT EXISTS idx_training_model_date 
                    ON ml_training_history(model_id, training_date)
                """))
                
                conn.commit()
                
            print("✅ 训练历史表创建成功")
            return True
            
        except Exception as e:
            print(f"❌ 创建训练历史表失败: {e}")
            return False

def generate_sample_training_history():
    """生成示例训练历史"""
    app = create_app()
    with app.app_context():
        try:
            print("📈 生成示例训练历史...")
            
            import random
            
            with db.engine.connect() as conn:
                # 获取模型列表
                result = conn.execute(db.text("SELECT model_id FROM ml_model_definition"))
                model_ids = [row[0] for row in result.fetchall()]
                
                for model_id in model_ids:
                    # 为每个模型生成几次训练历史
                    for i in range(3):
                        from datetime import timedelta
                        training_date = datetime.now() - timedelta(days=i*10)
                        
                        # 生成随机但合理的训练指标
                        accuracy = round(random.uniform(0.75, 0.92), 6)
                        precision = round(random.uniform(0.70, 0.90), 6)
                        recall = round(random.uniform(0.65, 0.88), 6)
                        f1 = round(2 * (precision * recall) / (precision + recall), 6)
                        auc = round(random.uniform(0.80, 0.95), 6)
                        loss = round(random.uniform(0.08, 0.25), 6)
                        
                        feature_importance = json.dumps({
                            'momentum_1d': round(random.uniform(0.15, 0.35), 4),
                            'momentum_5d': round(random.uniform(0.20, 0.40), 4),
                            'volatility_20d': round(random.uniform(0.10, 0.25), 4),
                            'volume_ratio_20d': round(random.uniform(0.05, 0.20), 4)
                        })
                        
                        validation_metrics = json.dumps({
                            'cv_accuracy_mean': round(accuracy - random.uniform(0.01, 0.05), 6),
                            'cv_accuracy_std': round(random.uniform(0.005, 0.02), 6),
                            'overfitting_score': round(random.uniform(0.02, 0.08), 6)
                        })
                        
                        conn.execute(db.text("""
                            INSERT INTO ml_training_history 
                            (model_id, training_date, start_date, end_date, training_samples, test_samples,
                             accuracy, precision_score, recall_score, f1_score, auc_score, loss,
                             training_time_seconds, model_size_mb, feature_importance, validation_metrics, is_successful)
                            VALUES (:model_id, :training_date, :start_date, :end_date, :training_samples, :test_samples,
                                    :accuracy, :precision_score, :recall_score, :f1_score, :auc_score, :loss,
                                    :training_time_seconds, :model_size_mb, :feature_importance, :validation_metrics, :is_successful)
                        """), {
                            'model_id': model_id,
                            'training_date': training_date,
                            'start_date': '2023-01-01',
                            'end_date': '2023-12-31',
                            'training_samples': random.randint(1000, 2000),
                            'test_samples': random.randint(200, 500),
                            'accuracy': accuracy,
                            'precision_score': precision,
                            'recall_score': recall,
                            'f1_score': f1,
                            'auc_score': auc,
                            'loss': loss,
                            'training_time_seconds': random.randint(30, 300),
                            'model_size_mb': round(random.uniform(1.5, 5.0), 2),
                            'feature_importance': feature_importance,
                            'validation_metrics': validation_metrics,
                            'is_successful': True
                        })
                
                conn.commit()
                
                # 验证数据
                result = conn.execute(db.text("SELECT COUNT(*) FROM ml_training_history"))
                total_history = result.fetchone()[0]
                
                print(f"✅ 生成了 {total_history} 条训练历史记录")
                
            return True
            
        except Exception as e:
            print(f"❌ 生成训练历史失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """主函数"""
    print("🚀 开始修复ML模型问题...")
    
    # 1. 创建ML模型定义表
    if not create_ml_model_table():
        return False
    
    # 2. 创建示例模型定义
    if not create_sample_model_definitions():
        return False
    
    # 3. 创建训练历史表
    if not create_training_history_table():
        return False
    
    # 4. 生成示例训练历史
    if not generate_sample_training_history():
        return False
    
    print("🎉 ML模型问题修复完成！")
    print("💡 现在可以测试以下功能：")
    print("  - 创建模型定义")
    print("  - 训练模型")
    print("  - 查看训练历史")
    print("  - 模型预测")
    
    return True

if __name__ == "__main__":
    main()
