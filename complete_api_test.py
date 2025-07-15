#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整API配置测试
Complete API Configuration Test
"""

import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_updated_apis():
    """测试更新后的API配置"""
    print("🔧 测试更新后的API配置")
    print("=" * 50)
    
    # 1. 测试阿里百炼API
    print("\n🧠 测试阿里百炼API...")
    dashscope_key = os.getenv('DASHSCOPE_API_KEY')
    
    if dashscope_key:
        print(f"✅ API密钥已配置: {dashscope_key[:15]}...")
        
        try:
            import dashscope
            from dashscope import Generation
            
            dashscope.api_key = dashscope_key
            
            print("📡 发送测试请求...")
            response = Generation.call(
                model='qwen-turbo',
                prompt='请用一句话介绍股票技术分析的核心思想',
                max_tokens=100
            )
            
            if response.status_code == 200:
                print("✅ 阿里百炼API测试成功")
                print(f"📝 响应: {response.output.text}")
                dashscope_ok = True
            else:
                print(f"❌ API调用失败: {response}")
                dashscope_ok = False
                
        except Exception as e:
            print(f"❌ API测试异常: {e}")
            dashscope_ok = False
    else:
        print("❌ 阿里百炼API密钥未配置")
        dashscope_ok = False
    
    # 2. 测试FinnHub API
    print("\n📊 测试FinnHub API...")
    finnhub_key = os.getenv('FINNHUB_API_KEY')
    
    if finnhub_key and finnhub_key != 'your_finnhub_api_key_here':
        print(f"✅ API密钥已配置: {finnhub_key[:15]}...")
        
        try:
            import finnhub
            finnhub_client = finnhub.Client(api_key=finnhub_key)
            
            print("📡 发送测试请求...")
            # 测试获取苹果股票报价
            quote = finnhub_client.quote('AAPL')
            
            if quote and 'c' in quote:
                print("✅ FinnHub API测试成功")
                print(f"📈 AAPL当前价格: ${quote['c']}")
                print(f"📊 今日变化: {quote['d']} ({quote['dp']:.2f}%)")
                finnhub_ok = True
            else:
                print(f"❌ API调用失败: {quote}")
                finnhub_ok = False
                
        except Exception as e:
            print(f"❌ API测试异常: {e}")
            finnhub_ok = False
    else:
        print("❌ FinnHub API密钥未配置")
        finnhub_ok = False
    
    return dashscope_ok, finnhub_ok

def test_stock_analysis_integration():
    """测试股票分析集成功能"""
    print("\n🔬 测试股票分析集成功能...")
    
    # 检查API状态
    dashscope_key = os.getenv('DASHSCOPE_API_KEY')
    finnhub_key = os.getenv('FINNHUB_API_KEY')
    
    if not dashscope_key or not finnhub_key:
        print("❌ 缺少必要的API密钥，跳过集成测试")
        return False
    
    try:
        import dashscope
        import finnhub
        from dashscope import Generation
        
        # 初始化API客户端
        dashscope.api_key = dashscope_key
        finnhub_client = finnhub.Client(api_key=finnhub_key)
        
        # 1. 获取股票数据
        print("📊 获取股票数据...")
        symbol = 'AAPL'
        quote = finnhub_client.quote(symbol)
        
        if not quote or 'c' not in quote:
            print("❌ 无法获取股票数据")
            return False
        
        # 2. 构建分析Prompt
        current_price = quote['c']
        change = quote['d']
        change_percent = quote['dp']
        
        analysis_prompt = f"""
# 系统角色
你是一位专业的股票技术分析师，具备概率思维和风险意识。

# 分析任务
基于以下实时数据，对苹果公司(AAPL)进行技术分析：

## 基础信息
- 标的: AAPL (苹果公司)
- 当前价格: ${current_price}
- 今日变化: {change} ({change_percent:.2f}%)
- 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 分析要求
请基于当前价格走势进行分析，并严格按照以下JSON格式输出：

{{
    "basic_info": {{
        "symbol": "AAPL",
        "current_price": {current_price},
        "daily_change": {change},
        "change_percent": {change_percent:.2f}
    }},
    "technical_analysis": {{
        "trend_direction": "基于价格变化判断趋势方向",
        "strength_level": "趋势强度评估",
        "market_sentiment": "市场情绪分析"
    }},
    "probability_analysis": {{
        "upward_probability": "上涨概率百分比",
        "downward_probability": "下跌概率百分比",
        "sideways_probability": "震荡概率百分比"
    }},
    "summary": "综合分析总结"
}}
"""
        
        # 3. 调用AI分析
        print("🧠 AI分析中...")
        response = Generation.call(
            model='qwen-plus',
            prompt=analysis_prompt,
            max_tokens=500
        )
        
        if response.status_code == 200:
            print("✅ 股票分析集成测试成功")
            print("\n📝 AI分析结果:")
            print(response.output.text)
            return True
        else:
            print(f"❌ AI分析失败: {response}")
            return False
            
    except Exception as e:
        print(f"❌ 集成测试异常: {e}")
        return False

def test_tradingagents_compatibility():
    """测试TradingAgents兼容性"""
    print("\n🤖 测试TradingAgents兼容性...")
    
    # 检查TradingAgents-CN目录
    tradingagents_path = "TradingAgents-CN-main"
    if not os.path.exists(tradingagents_path):
        print("❌ TradingAgents-CN-main目录不存在")
        return False
    
    # 检查关键文件
    key_files = [
        "tradingagents/default_config.py",
        "tradingagents/graph/trading_graph.py",
        "api_service.py"
    ]
    
    missing_files = []
    for file_path in key_files:
        full_path = os.path.join(tradingagents_path, file_path)
        if os.path.exists(full_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ 缺少关键文件: {missing_files}")
        return False
    
    print("✅ TradingAgents-CN结构完整")
    return True

def generate_configuration_summary():
    """生成配置总结"""
    print("\n📋 生成配置总结...")
    
    summary = {
        "api_configuration": {
            "dashscope": {
                "key": os.getenv('DASHSCOPE_API_KEY', 'Not configured'),
                "status": "✅ 已配置" if os.getenv('DASHSCOPE_API_KEY') else "❌ 未配置"
            },
            "finnhub": {
                "key": os.getenv('FINNHUB_API_KEY', 'Not configured'),
                "status": "✅ 已配置" if os.getenv('FINNHUB_API_KEY') else "❌ 未配置"
            }
        },
        "system_capabilities": [
            "多智能体股票分析",
            "实时数据获取",
            "AI驱动的技术分析",
            "概率化风险评估",
            "结构化JSON输出"
        ],
        "cost_estimation": {
            "dashscope_per_analysis": "0.1-0.3元",
            "finnhub_free_limit": "每分钟60次请求",
            "monthly_cost_estimate": "150-500元 (中等使用量)"
        },
        "next_steps": [
            "测试完整的TradingAgents功能",
            "开发实时数据更新模块",
            "优化用户界面展示",
            "集成更多技术指标"
        ]
    }
    
    # 保存配置总结
    with open("API_Configuration_Summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print("✅ 配置总结已保存到 API_Configuration_Summary.json")
    
    return summary

def main():
    """主函数"""
    print("🚀 完整API配置测试")
    print("=" * 60)
    
    # 1. 测试更新后的API
    dashscope_ok, finnhub_ok = test_updated_apis()
    
    # 2. 测试股票分析集成
    if dashscope_ok and finnhub_ok:
        integration_ok = test_stock_analysis_integration()
    else:
        integration_ok = False
    
    # 3. 测试TradingAgents兼容性
    tradingagents_ok = test_tradingagents_compatibility()
    
    # 4. 生成配置总结
    summary = generate_configuration_summary()
    
    # 5. 最终报告
    print("\n" + "=" * 60)
    print("📊 最终测试报告")
    print("=" * 60)
    
    print(f"✅ 阿里百炼API: {'通过' if dashscope_ok else '失败'}")
    print(f"✅ FinnHub API: {'通过' if finnhub_ok else '失败'}")
    print(f"✅ 股票分析集成: {'通过' if integration_ok else '失败'}")
    print(f"✅ TradingAgents兼容性: {'通过' if tradingagents_ok else '失败'}")
    
    if dashscope_ok and finnhub_ok and integration_ok:
        print("\n🎉 恭喜！所有测试通过，系统已准备就绪！")
        print("\n🚀 您现在可以：")
        print("1. 使用TradingAgents进行股票分析")
        print("2. 调用实时股票数据")
        print("3. 获得AI驱动的投资建议")
        print("4. 享受概率化的风险评估")
        
        print(f"\n💰 成本预估：")
        print("- 每次分析约0.1-0.3元")
        print("- 每月约150-500元 (中等使用量)")
        print("- FinnHub免费版足够日常使用")
        
    else:
        print("\n⚠️ 部分测试未通过，请检查配置")
        if not dashscope_ok:
            print("- 检查阿里百炼API密钥")
        if not finnhub_ok:
            print("- 检查FinnHub API密钥")
        if not integration_ok:
            print("- 检查API集成功能")
        if not tradingagents_ok:
            print("- 检查TradingAgents-CN目录结构")

if __name__ == "__main__":
    main()
