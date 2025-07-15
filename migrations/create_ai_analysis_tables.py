#!/usr/bin/env python3
"""
创建AI分析相关数据表的迁移脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.extensions import db
from app.models.ai_analysis_result import AIAnalysisResult, AIModelConfig

def create_ai_analysis_tables():
    """创建AI分析相关的数据表"""
    
    app = create_app('development')
    
    with app.app_context():
        try:
            print("开始创建AI分析相关数据表...")
            
            # 创建表
            db.create_all()
            
            print("✅ AI分析数据表创建成功!")
            
            # 创建一些默认的AI模型配置
            create_default_ai_configs()
            
            print("✅ 默认AI模型配置创建成功!")
            
        except Exception as e:
            print(f"❌ 创建AI分析数据表失败: {e}")
            return False
    
    return True

def create_default_ai_configs():
    """创建默认的AI模型配置"""
    
    default_configs = [
        {
            'model_name': '快速分析模型',
            'llm_provider': 'dashscope',
            'model_type': 'qwen-turbo',
            'analysts_config': '["market", "fundamentals"]',
            'analysis_depth': 'quick',
            'max_debate_rounds': 1,
            'online_tools': True,
            'description': '适合日常快速分析，2-4分钟完成'
        },
        {
            'model_name': '标准分析模型',
            'llm_provider': 'dashscope', 
            'model_type': 'qwen-plus',
            'analysts_config': '["market", "fundamentals", "news"]',
            'analysis_depth': 'standard',
            'max_debate_rounds': 2,
            'online_tools': True,
            'description': '平衡分析质量和速度，4-8分钟完成'
        },
        {
            'model_name': '深度分析模型',
            'llm_provider': 'dashscope',
            'model_type': 'qwen-max',
            'analysts_config': '["market", "fundamentals", "news", "social"]',
            'analysis_depth': 'deep',
            'max_debate_rounds': 3,
            'online_tools': True,
            'description': '最全面的分析，8-15分钟完成'
        },
        {
            'model_name': 'OpenAI标准模型',
            'llm_provider': 'openai',
            'model_type': 'gpt-4o',
            'analysts_config': '["market", "fundamentals", "news"]',
            'analysis_depth': 'standard',
            'max_debate_rounds': 2,
            'online_tools': True,
            'description': '基于OpenAI GPT-4的分析模型',
            'is_active': False  # 默认不激活，需要配置API密钥
        },
        {
            'model_name': 'Google AI模型',
            'llm_provider': 'google',
            'model_type': 'gemini-2.0-flash',
            'analysts_config': '["market", "fundamentals", "news"]',
            'analysis_depth': 'standard',
            'max_debate_rounds': 2,
            'online_tools': True,
            'description': '基于Google Gemini的分析模型',
            'is_active': False  # 默认不激活，需要配置API密钥
        }
    ]
    
    for config_data in default_configs:
        # 检查是否已存在
        existing = AIModelConfig.query.filter_by(
            model_name=config_data['model_name']
        ).first()
        
        if not existing:
            config = AIModelConfig(**config_data)
            db.session.add(config)
    
    db.session.commit()

def check_ai_analysis_tables():
    """检查AI分析表是否存在"""
    
    app = create_app('development')
    
    with app.app_context():
        try:
            # 检查表是否存在
            result = db.session.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('ai_analysis_results', 'ai_model_configs')"
            ).fetchall()
            
            table_names = [row[0] for row in result]
            
            print("现有AI分析相关表:")
            for table_name in table_names:
                print(f"  - {table_name}")
            
            if 'ai_analysis_results' in table_names:
                count = db.session.execute("SELECT COUNT(*) FROM ai_analysis_results").scalar()
                print(f"  ai_analysis_results 表中有 {count} 条记录")
            
            if 'ai_model_configs' in table_names:
                count = db.session.execute("SELECT COUNT(*) FROM ai_model_configs").scalar()
                print(f"  ai_model_configs 表中有 {count} 条记录")
            
            return len(table_names) == 2
            
        except Exception as e:
            print(f"检查AI分析表失败: {e}")
            return False

def drop_ai_analysis_tables():
    """删除AI分析相关表（谨慎使用）"""
    
    app = create_app('development')
    
    with app.app_context():
        try:
            print("⚠️  警告：即将删除AI分析相关数据表...")
            confirm = input("确认删除？(yes/no): ")
            
            if confirm.lower() == 'yes':
                # 删除表
                AIAnalysisResult.__table__.drop(db.engine, checkfirst=True)
                AIModelConfig.__table__.drop(db.engine, checkfirst=True)
                
                print("✅ AI分析数据表已删除")
                return True
            else:
                print("❌ 操作已取消")
                return False
                
        except Exception as e:
            print(f"❌ 删除AI分析数据表失败: {e}")
            return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='AI分析数据表管理工具')
    parser.add_argument('action', choices=['create', 'check', 'drop'], 
                       help='操作类型: create(创建), check(检查), drop(删除)')
    
    args = parser.parse_args()
    
    if args.action == 'create':
        success = create_ai_analysis_tables()
        sys.exit(0 if success else 1)
    elif args.action == 'check':
        exists = check_ai_analysis_tables()
        sys.exit(0 if exists else 1)
    elif args.action == 'drop':
        success = drop_ai_analysis_tables()
        sys.exit(0 if success else 1)
