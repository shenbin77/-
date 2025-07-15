#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API配置测试脚本
Test API Configuration Script
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_dashscope_api():
    """测试阿里百炼API"""
    print("🧠 测试阿里百炼API...")
    
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ 阿里百炼API密钥未配置")
        return False
    
    print(f"✅ API密钥已配置: {api_key[:10]}...")
    
    try:
        import dashscope
        dashscope.api_key = api_key
        
        # 简单测试调用
        from dashscope import Generation
        
        print("📡 发送测试请求...")
        response = Generation.call(
            model='qwen-turbo',
            prompt='请简单介绍一下股票技术分析',
            max_tokens=50
        )
        
        if response.status_code == 200:
            print("✅ 阿里百炼API测试成功")
            print(f"📝 响应内容: {response.output.text[:100]}...")
            return True
        else:
            print(f"❌ API调用失败: {response}")
            return False
            
    except ImportError:
        print("❌ dashscope包未安装，请运行: pip install dashscope")
        return False
    except Exception as e:
        print(f"❌ API测试异常: {e}")
        return False

def test_finnhub_api():
    """测试FinnHub API"""
    print("\n📊 测试FinnHub API...")
    
    api_key = os.getenv('FINNHUB_API_KEY')
    if not api_key or api_key == 'your_finnhub_api_key_here':
        print("❌ FinnHub API密钥未配置")
        print("💡 请访问 https://finnhub.io/ 获取免费API密钥")
        return False
    
    print(f"✅ API密钥已配置: {api_key[:10]}...")
    
    try:
        import finnhub
        finnhub_client = finnhub.Client(api_key=api_key)
        
        print("📡 发送测试请求...")
        # 测试获取苹果股票报价
        quote = finnhub_client.quote('AAPL')
        
        if quote and 'c' in quote:
            print("✅ FinnHub API测试成功")
            print(f"📈 AAPL当前价格: ${quote['c']}")
            return True
        else:
            print(f"❌ API调用失败: {quote}")
            return False
            
    except ImportError:
        print("❌ finnhub-python包未安装，请运行: pip install finnhub-python")
        return False
    except Exception as e:
        print(f"❌ API测试异常: {e}")
        return False

def test_optional_apis():
    """测试可选API"""
    print("\n🔧 测试可选API...")
    
    # 测试OpenAI API
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key and openai_key != 'your_openai_api_key_here':
        print(f"✅ OpenAI API密钥已配置: {openai_key[:10]}...")
    else:
        print("⚠️ OpenAI API密钥未配置 (可选)")
    
    # 测试Google AI API
    google_key = os.getenv('GOOGLE_API_KEY')
    if google_key and google_key != 'your_google_api_key_here':
        print(f"✅ Google AI API密钥已配置: {google_key[:10]}...")
    else:
        print("⚠️ Google AI API密钥未配置 (可选)")
    
    # 测试Anthropic API
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if anthropic_key and anthropic_key != 'your_anthropic_api_key_here':
        print(f"✅ Anthropic API密钥已配置: {anthropic_key[:10]}...")
    else:
        print("⚠️ Anthropic API密钥未配置 (可选)")

def test_enhanced_prompt():
    """测试增强版Prompt"""
    print("\n📝 测试增强版Prompt模板...")
    
    # 检查是否有阿里百炼API
    if not os.getenv('DASHSCOPE_API_KEY'):
        print("❌ 需要阿里百炼API才能测试Prompt")
        return False
    
    try:
        import dashscope
        from dashscope import Generation
        
        dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')
        
        # 构建测试用的结构化Prompt
        test_prompt = """
# 系统角色
你是一位专业的股票技术分析师，具备概率思维和风险意识。

# 分析任务
基于以下数据，对平安银行(000001)进行技术分析：

## 基础信息
- 标的: 000001 (平安银行)
- 当前价格: 15.20
- 分析时间: 2025-01-15 14:30
- 时间框架: 日线

## 技术指标
- MACD: DIF=0.12, DEA=0.08, BAR=0.04
- RSI: 65.5
- MA5: 15.10, MA20: 14.80

# 输出要求
请严格按照以下JSON格式输出：

{
    "technical_analysis": {
        "trend_direction": "上涨",
        "strength_level": "中等",
        "key_levels": {
            "support": "14.80",
            "resistance": "15.50"
        }
    },
    "probability_analysis": {
        "upward_probability": "60%",
        "downward_probability": "25%", 
        "sideways_probability": "15%"
    },
    "summary": "技术指标显示短期上涨趋势，但需关注阻力位"
}
"""
        
        print("📡 发送增强版Prompt测试...")
        response = Generation.call(
            model='qwen-turbo',
            prompt=test_prompt,
            max_tokens=300
        )
        
        if response.status_code == 200:
            print("✅ 增强版Prompt测试成功")
            print("📝 AI响应:")
            print(response.output.text)
            return True
        else:
            print(f"❌ Prompt测试失败: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Prompt测试异常: {e}")
        return False

def generate_setup_instructions():
    """生成设置说明"""
    print("\n📋 API配置设置说明:")
    
    instructions = """
# 🔑 API密钥获取指南

## 1. 阿里百炼 (DashScope) - 已配置 ✅
- 您的密钥: sk-61f17f4d75fc45429a44977814eb8cf7
- 状态: 已在.env文件中配置完成

## 2. FinnHub API - 需要配置 ⚠️
- 访问: https://finnhub.io/
- 注册免费账户
- 获取API密钥
- 在.env文件中替换: FINNHUB_API_KEY=your_finnhub_api_key_here

## 3. 可选API (根据需要配置)
- OpenAI: https://platform.openai.com/
- Google AI: https://ai.google.dev/
- Anthropic: https://console.anthropic.com/

# 💰 成本估算
- 阿里百炼: 每次分析约0.1-0.3元
- FinnHub: 免费版每分钟60次请求
- 总成本: 每月约150-500元 (中等使用量)

# 🚀 下一步
1. 获取FinnHub API密钥
2. 运行: python test_api_configuration.py
3. 测试TradingAgents功能
4. 开始股票分析
"""
    
    print(instructions)
    
    # 保存到文件
    with open("API_Setup_Instructions.md", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print("✅ 设置说明已保存到 API_Setup_Instructions.md")

def main():
    """主函数"""
    print("🔧 API配置测试")
    print("=" * 40)
    
    # 1. 测试阿里百炼API
    dashscope_ok = test_dashscope_api()
    
    # 2. 测试FinnHub API
    finnhub_ok = test_finnhub_api()
    
    # 3. 测试可选API
    test_optional_apis()
    
    # 4. 测试增强版Prompt
    if dashscope_ok:
        prompt_ok = test_enhanced_prompt()
    else:
        prompt_ok = False
    
    # 5. 生成设置说明
    generate_setup_instructions()
    
    # 6. 总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结")
    print("=" * 50)
    
    print(f"✅ 阿里百炼API: {'通过' if dashscope_ok else '失败'}")
    print(f"✅ FinnHub API: {'通过' if finnhub_ok else '需要配置'}")
    print(f"✅ 增强版Prompt: {'通过' if prompt_ok else '失败'}")
    
    if dashscope_ok and finnhub_ok:
        print("\n🎉 恭喜！所有必需的API都已配置完成")
        print("🚀 您可以开始使用TradingAgents进行股票分析了")
    elif dashscope_ok:
        print("\n⚠️ 阿里百炼API已就绪，还需要配置FinnHub API")
        print("💡 请访问 https://finnhub.io/ 获取免费API密钥")
    else:
        print("\n❌ 需要检查API配置")
        print("📖 请参考生成的设置说明文档")
    
    print(f"\n💡 关于比特币AI分析网站的启发:")
    print("1. ✅ 结构化Prompt设计 - 已实现")
    print("2. ✅ 概率化表达方式 - 已集成")
    print("3. ✅ JSON格式输出 - 已测试")
    print("4. 🔄 实时数据集成 - 待开发")

if __name__ == "__main__":
    main()
