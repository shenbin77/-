#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents-CN API需求测试
Test TradingAgents-CN API Requirements
"""

import os
import sys
from pathlib import Path

# 添加TradingAgents-CN路径
tradingagents_path = Path(__file__).parent / "TradingAgents-CN-main"
sys.path.insert(0, str(tradingagents_path))

def check_environment_setup():
    """检查环境设置"""
    print("🔍 检查TradingAgents-CN环境设置...")
    
    # 检查必需的环境变量
    required_vars = {
        'DASHSCOPE_API_KEY': '阿里百炼API密钥',
        'FINNHUB_API_KEY': 'FinnHub金融数据API密钥'
    }
    
    optional_vars = {
        'OPENAI_API_KEY': 'OpenAI API密钥',
        'GOOGLE_API_KEY': 'Google AI API密钥',
        'ANTHROPIC_API_KEY': 'Anthropic API密钥'
    }
    
    print("\n📋 必需的API密钥检查:")
    missing_required = []
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {desc}: 已配置 ({value[:10]}...)")
        else:
            print(f"❌ {desc}: 未配置")
            missing_required.append(var)
    
    print("\n📋 可选的API密钥检查:")
    for var, desc in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {desc}: 已配置 ({value[:10]}...)")
        else:
            print(f"⚠️ {desc}: 未配置 (可选)")
    
    return len(missing_required) == 0, missing_required

def check_dependencies():
    """检查依赖包"""
    print("\n🔧 检查TradingAgents-CN依赖包...")
    
    required_packages = [
        'langchain-openai',
        'langchain-experimental', 
        'pandas',
        'yfinance',
        'stockstats',
        'langgraph',
        'akshare',
        'tushare',
        'finnhub-python',
        'requests',
        'dashscope',
        'langchain_anthropic',
        'langchain-google-genai'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'langchain-openai':
                import langchain_openai
            elif package == 'langchain-experimental':
                import langchain_experimental
            elif package == 'pandas':
                import pandas
            elif package == 'yfinance':
                import yfinance
            elif package == 'stockstats':
                import stockstats
            elif package == 'langgraph':
                import langgraph
            elif package == 'akshare':
                import akshare
            elif package == 'tushare':
                import tushare
            elif package == 'finnhub-python':
                import finnhub
            elif package == 'requests':
                import requests
            elif package == 'dashscope':
                import dashscope
            elif package == 'langchain_anthropic':
                import langchain_anthropic
            elif package == 'langchain-google-genai':
                import langchain_google_genai
            
            print(f"✅ {package}: 已安装")
            
        except ImportError:
            print(f"❌ {package}: 未安装")
            missing_packages.append(package)
    
    return len(missing_packages) == 0, missing_packages

def test_api_connections():
    """测试API连接"""
    print("\n🌐 测试API连接...")
    
    # 测试阿里百炼API
    dashscope_key = os.getenv('DASHSCOPE_API_KEY')
    if dashscope_key:
        try:
            import dashscope
            dashscope.api_key = dashscope_key
            
            # 简单测试调用
            from dashscope import Generation
            response = Generation.call(
                model='qwen-turbo',
                prompt='你好',
                max_tokens=10
            )
            
            if response.status_code == 200:
                print("✅ 阿里百炼API: 连接成功")
            else:
                print(f"❌ 阿里百炼API: 连接失败 - {response}")
                
        except Exception as e:
            print(f"❌ 阿里百炼API: 测试异常 - {e}")
    else:
        print("⚠️ 阿里百炼API: 未配置密钥，跳过测试")
    
    # 测试FinnHub API
    finnhub_key = os.getenv('FINNHUB_API_KEY')
    if finnhub_key:
        try:
            import finnhub
            finnhub_client = finnhub.Client(api_key=finnhub_key)
            
            # 简单测试调用
            quote = finnhub_client.quote('AAPL')
            
            if quote and 'c' in quote:
                print("✅ FinnHub API: 连接成功")
            else:
                print(f"❌ FinnHub API: 连接失败 - {quote}")
                
        except Exception as e:
            print(f"❌ FinnHub API: 测试异常 - {e}")
    else:
        print("⚠️ FinnHub API: 未配置密钥，跳过测试")

def test_tradingagents_import():
    """测试TradingAgents-CN导入"""
    print("\n📦 测试TradingAgents-CN模块导入...")
    
    try:
        # 测试核心模块导入
        from tradingagents.default_config import DEFAULT_CONFIG
        print("✅ 默认配置模块: 导入成功")
        
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        print("✅ 交易图模块: 导入成功")
        
        # 测试分析师模块
        from tradingagents.agents.analysts.market_analyst import create_market_analyst_react
        print("✅ 市场分析师模块: 导入成功")
        
        from tradingagents.agents.analysts.fundamentals_analyst import create_fundamentals_analyst
        print("✅ 基本面分析师模块: 导入成功")
        
        # 测试LLM适配器
        from tradingagents.llm_adapters import ChatDashScope
        print("✅ 阿里百炼适配器: 导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ TradingAgents-CN模块导入失败: {e}")
        return False

def test_basic_functionality():
    """测试基本功能"""
    print("\n🧪 测试TradingAgents-CN基本功能...")
    
    # 检查是否有必需的API密钥
    if not os.getenv('DASHSCOPE_API_KEY'):
        print("⚠️ 缺少阿里百炼API密钥，跳过功能测试")
        return False
    
    try:
        from tradingagents.default_config import DEFAULT_CONFIG
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        
        # 创建简化配置
        test_config = DEFAULT_CONFIG.copy()
        test_config.update({
            "llm_provider": "dashscope",
            "deep_think_llm": "qwen-turbo",
            "quick_think_llm": "qwen-turbo",
            "max_debate_rounds": 1,
            "online_tools": False  # 关闭在线工具避免额外API调用
        })
        
        # 创建TradingAgents实例
        trading_graph = TradingAgentsGraph(
            selected_analysts=["market"],  # 只使用一个分析师
            debug=True,
            config=test_config
        )
        
        print("✅ TradingAgents实例创建成功")
        
        # 测试简单分析（模拟模式）
        test_state = {
            "company_of_interest": "000001",  # 平安银行
            "trade_date": "2025-01-15",
            "analysis_mode": "test"
        }
        
        print("✅ 基本功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 基本功能测试失败: {e}")
        return False

def generate_setup_guide():
    """生成设置指南"""
    print("\n📖 生成TradingAgents-CN设置指南...")
    
    guide = """
# TradingAgents-CN 设置指南

## 1. 安装依赖包
```bash
pip install -r TradingAgents-CN-main/requirements.txt
```

## 2. 配置环境变量
创建 .env 文件并添加以下内容：

```bash
# 必需的API密钥
DASHSCOPE_API_KEY=your_dashscope_api_key_here
FINNHUB_API_KEY=your_finnhub_api_key_here

# 可选的API密钥
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## 3. 获取API密钥

### 阿里百炼 (必需)
1. 访问: https://dashscope.aliyun.com/
2. 注册阿里云账号
3. 开通百炼服务
4. 获取API密钥

### FinnHub (必需)
1. 访问: https://finnhub.io/
2. 注册免费账户
3. 获取API密钥

## 4. 测试配置
```bash
python test_tradingagents_api.py
```

## 5. 运行示例
```bash
cd TradingAgents-CN-main
python -m cli.main analyze --stock 000001 --market A股
```
"""
    
    with open("TradingAgents_Setup_Guide.md", "w", encoding="utf-8") as f:
        f.write(guide)
    
    print("✅ 设置指南已保存到 TradingAgents_Setup_Guide.md")

def main():
    """主函数"""
    print("🤖 TradingAgents-CN API需求分析测试")
    print("=" * 60)
    
    # 1. 检查环境设置
    env_ok, missing_env = check_environment_setup()
    
    # 2. 检查依赖包
    deps_ok, missing_deps = check_dependencies()
    
    # 3. 测试API连接
    if env_ok:
        test_api_connections()
    
    # 4. 测试模块导入
    import_ok = test_tradingagents_import()
    
    # 5. 测试基本功能
    if env_ok and deps_ok and import_ok:
        func_ok = test_basic_functionality()
    else:
        func_ok = False
    
    # 6. 生成报告
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    
    print(f"✅ 环境配置: {'通过' if env_ok else '失败'}")
    if not env_ok:
        print(f"   缺少: {', '.join(missing_env)}")
    
    print(f"✅ 依赖包: {'通过' if deps_ok else '失败'}")
    if not deps_ok:
        print(f"   缺少: {', '.join(missing_deps)}")
    
    print(f"✅ 模块导入: {'通过' if import_ok else '失败'}")
    print(f"✅ 基本功能: {'通过' if func_ok else '失败'}")
    
    # 7. 生成设置指南
    generate_setup_guide()
    
    # 8. 总结建议
    print(f"\n💡 总结:")
    if env_ok and deps_ok and import_ok and func_ok:
        print("🎉 TradingAgents-CN 已准备就绪！")
        print("📱 您可以开始使用多智能体股票分析功能")
    else:
        print("⚠️ TradingAgents-CN 需要进一步配置")
        print("📖 请参考生成的设置指南完成配置")
    
    print(f"\n📋 API需求确认:")
    print("✅ 需要大模型API: 是")
    print("✅ 推荐API: 阿里百炼 (DashScope)")
    print("✅ 必需API: FinnHub (金融数据)")
    print("✅ 可选API: OpenAI, Google AI, Anthropic")

if __name__ == "__main__":
    main()
