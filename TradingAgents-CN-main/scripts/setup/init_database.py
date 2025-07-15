#!/usr/bin/env python3
"""
数据库初始化脚本
创建MongoDB集合和索引，初始化Redis缓存结构
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def init_mongodb():
    """初始化MongoDB数据库"""
    print("📊 初始化MongoDB数据库...")
    
    try:
        from tradingagents.config.database_manager import get_database_manager

        db_manager = get_database_manager()

        if not db_manager.is_mongodb_available():
            print("❌ MongoDB未连接，请先启动MongoDB服务")
            return False

        mongodb_client = db_manager.get_mongodb_client()
        db = mongodb_client[db_manager.mongodb_config["database"]]
        
        # 创建股票数据集合和索引
        print("📈 创建股票数据集合...")
        stock_data_collection = db.stock_data
        
        # 创建索引
        stock_data_collection.create_index([("symbol", 1), ("market_type", 1)], unique=True)
        stock_data_collection.create_index([("created_at", -1)])
        stock_data_collection.create_index([("updated_at", -1)])
        
        print("✅ 股票数据集合创建完成")
        
        # 创建分析结果集合和索引
        print("📊 创建分析结果集合...")
        analysis_collection = db.analysis_results
        
        # 创建索引
        analysis_collection.create_index([("symbol", 1), ("analysis_type", 1)])
        analysis_collection.create_index([("created_at", -1)])
        analysis_collection.create_index([("symbol", 1), ("created_at", -1)])
        
        print("✅ 分析结果集合创建完成")
        
        # 创建用户会话集合和索引
        print("👤 创建用户会话集合...")
        sessions_collection = db.user_sessions
        
        # 创建索引
        sessions_collection.create_index([("session_id", 1)], unique=True)
        sessions_collection.create_index([("created_at", -1)])
        sessions_collection.create_index([("last_activity", -1)])
        
        print("✅ 用户会话集合创建完成")
        
        # 创建配置集合
        print("⚙️ 创建配置集合...")
        config_collection = db.configurations
        
        # 创建索引
        config_collection.create_index([("config_type", 1), ("config_name", 1)], unique=True)
        config_collection.create_index([("updated_at", -1)])
        
        print("✅ 配置集合创建完成")
        
        # 插入初始配置数据
        print("📝 插入初始配置数据...")
        initial_configs = [
            {
                "config_type": "cache",
                "config_name": "ttl_settings",
                "config_value": {
                    "us_stock_data": 7200,
                    "china_stock_data": 3600,
                    "us_news": 21600,
                    "china_news": 14400,
                    "us_fundamentals": 86400,
                    "china_fundamentals": 43200
                },
                "description": "缓存TTL配置",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "config_type": "llm",
                "config_name": "default_models",
                "config_value": {
                    "default_provider": "dashscope",
                    "models": {
                        "dashscope": "qwen-plus-latest",
                        "openai": "gpt-4o-mini",
                        "google": "gemini-pro"
                    }
                },
                "description": "默认LLM模型配置",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        
        for config in initial_configs:
            config_collection.replace_one(
                {"config_type": config["config_type"], "config_name": config["config_name"]},
                config,
                upsert=True
            )
        
        print("✅ 初始配置数据插入完成")
        
        # 显示数据库统计
        print("\n📊 数据库统计:")
        print(f"  - 股票数据: {stock_data_collection.count_documents({})} 条记录")
        print(f"  - 分析结果: {analysis_collection.count_documents({})} 条记录")
        print(f"  - 用户会话: {sessions_collection.count_documents({})} 条记录")
        print(f"  - 配置项: {config_collection.count_documents({})} 条记录")
        
        return True
        
    except Exception as e:
        print(f"❌ MongoDB初始化失败: {e}")
        return False


def init_redis():
    """初始化Redis缓存"""
    print("\n📦 初始化Redis缓存...")
    
    try:
        from tradingagents.config.database_manager import get_database_manager

        db_manager = get_database_manager()

        if not db_manager.is_redis_available():
            print("❌ Redis未连接，请先启动Redis服务")
            return False
        
        redis_client = db_manager.get_redis_client()
        
        # 清理现有缓存（可选）
        print("🧹 清理现有缓存...")
        redis_client.flushdb()
        
        # 设置初始缓存配置
        print("⚙️ 设置缓存配置...")
        cache_config = {
            "version": "1.0",
            "initialized_at": datetime.utcnow().isoformat(),
            "ttl_settings": {
                "us_stock_data": 7200,
                "china_stock_data": 3600,
                "us_news": 21600,
                "china_news": 14400,
                "us_fundamentals": 86400,
                "china_fundamentals": 43200
            }
        }
        
        db_manager.cache_set("system:cache_config", cache_config, ttl=86400*30)  # 30天
        
        # 设置缓存统计初始值
        print("📊 初始化缓存统计...")
        stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "total_requests": 0,
            "last_reset": datetime.utcnow().isoformat()
        }
        
        db_manager.cache_set("system:cache_stats", stats, ttl=86400*7)  # 7天
        
        # 测试缓存功能
        print("🧪 测试缓存功能...")
        test_key = "test:init"
        test_value = {"message": "Redis初始化成功", "timestamp": datetime.utcnow().isoformat()}
        
        if db_manager.cache_set(test_key, test_value, ttl=60):
            retrieved_value = db_manager.cache_get(test_key)
            if retrieved_value and retrieved_value["message"] == test_value["message"]:
                print("✅ 缓存读写测试通过")
                db_manager.cache_delete(test_key)  # 清理测试数据
            else:
                print("❌ 缓存读取测试失败")
                return False
        else:
            print("❌ 缓存写入测试失败")
            return False
        
        # 显示Redis统计
        info = redis_client.info()
        print("\n📦 Redis统计:")
        print(f"  - 已用内存: {info.get('used_memory_human', 'N/A')}")
        print(f"  - 连接客户端: {info.get('connected_clients', 0)}")
        print(f"  - 总命令数: {info.get('total_commands_processed', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis初始化失败: {e}")
        return False


def test_database_connection():
    """测试数据库连接"""
    print("\n🔗 测试数据库连接...")
    
    try:
        from tradingagents.dataflows.database_manager import get_database_manager
        
        db_manager = get_database_manager()
        
        # 测试MongoDB连接
        mongodb_ok = False
        if db_manager.mongodb_client:
            try:
                db_manager.mongodb_client.admin.command('ping')
                print("✅ MongoDB连接正常")
                mongodb_ok = True
            except Exception as e:
                print(f"❌ MongoDB连接失败: {e}")
        else:
            print("❌ MongoDB未连接")
        
        # 测试Redis连接
        redis_ok = False
        if db_manager.redis_client:
            try:
                db_manager.redis_client.ping()
                print("✅ Redis连接正常")
                redis_ok = True
            except Exception as e:
                print(f"❌ Redis连接失败: {e}")
        else:
            print("❌ Redis未连接")
        
        return mongodb_ok and redis_ok
        
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False


def main():
    """主函数"""
    print("🚀 TradingAgents 数据库初始化")
    print("=" * 50)
    
    # 测试连接
    if not test_database_connection():
        print("\n❌ 数据库连接失败，请检查:")
        print("1. Docker服务是否启动: docker ps")
        print("2. 运行启动脚本: scripts/start_docker_services.bat")
        print("3. 检查环境变量配置: .env文件")
        return False
    
    # 初始化MongoDB
    mongodb_success = init_mongodb()
    
    # 初始化Redis
    redis_success = init_redis()
    
    # 输出结果
    print("\n" + "=" * 50)
    print("📋 初始化结果:")
    print(f"  MongoDB: {'✅ 成功' if mongodb_success else '❌ 失败'}")
    print(f"  Redis: {'✅ 成功' if redis_success else '❌ 失败'}")
    
    if mongodb_success and redis_success:
        print("\n🎉 数据库初始化完成！")
        print("\n💡 下一步:")
        print("1. 启动Web应用: cd web && python -m streamlit run app.py")
        print("2. 访问缓存管理: http://localhost:8501 -> 缓存管理")
        print("3. 访问Redis管理界面: http://localhost:8081")
        return True
    else:
        print("\n⚠️ 部分初始化失败，请检查错误信息")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
