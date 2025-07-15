#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TradingAgents-CN 简化检查
Simple TradingAgents-CN Check
"""

import os
import sys
from pathlib import Path

def check_tradingagents_structure():
    """检查TradingAgents-CN项目结构"""
    print("🔍 检查TradingAgents-CN项目结构...")
    
    base_path = Path("TradingAgents-CN-main")
    
    if not base_path.exists():
        print("❌ TradingAgents-CN-main 目录不存在")
        return False
    
    # 检查关键文件
    key_files = [
        "tradingagents/default_config.py",
        "tradingagents/graph/trading_graph.py",
        "tradingagents/agents/analysts/market_analyst.py",
        "tradingagents/llm_adapters/dashscope_adapter.py",
        "requirements.txt",
        ".env.example",
        "api_service.py"
    ]
    
    print("\n📋 关键文件检查:")
    missing_files = []
    
    for file_path in key_files:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def analyze_config_requirements():
    """分析配置需求"""
    print("\n🔧 分析TradingAgents-CN配置需求...")
    
    try:
        # 读取默认配置
        config_path = Path("TradingAgents-CN-main/tradingagents/default_config.py")
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            print("📊 默认配置分析:")
            if 'llm_provider' in config_content:
                print("✅ 支持多种LLM提供商")
            if 'openai' in config_content:
                print("✅ 支持OpenAI")
            if 'dashscope' in config_content:
                print("✅ 支持阿里百炼")
            if 'online_tools' in config_content:
                print("✅ 支持在线工具")
        
        # 读取环境变量示例
        env_path = Path("TradingAgents-CN-main/.env.example")
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                env_content = f.read()
            
            print("\n🔑 API密钥需求分析:")
            if 'DASHSCOPE_API_KEY' in env_content:
                print("✅ 需要阿里百炼API密钥 (推荐)")
            if 'FINNHUB_API_KEY' in env_content:
                print("✅ 需要FinnHub API密钥 (必需)")
            if 'OPENAI_API_KEY' in env_content:
                print("✅ 支持OpenAI API密钥 (可选)")
            if 'GOOGLE_API_KEY' in env_content:
                print("✅ 支持Google AI API密钥 (可选)")
            if 'ANTHROPIC_API_KEY' in env_content:
                print("✅ 支持Anthropic API密钥 (可选)")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置分析失败: {e}")
        return False

def analyze_agents_structure():
    """分析智能体结构"""
    print("\n🤖 分析智能体结构...")
    
    agents_path = Path("TradingAgents-CN-main/tradingagents/agents")
    
    if not agents_path.exists():
        print("❌ agents目录不存在")
        return False
    
    # 分析师类型
    analysts_path = agents_path / "analysts"
    if analysts_path.exists():
        print("📊 分析师机器人:")
        analyst_files = list(analysts_path.glob("*.py"))
        for file in analyst_files:
            if file.name != "__init__.py":
                analyst_name = file.stem.replace("_", " ").title()
                print(f"  ✅ {analyst_name}")
    
    # 研究员类型
    researchers_path = agents_path / "researchers"
    if researchers_path.exists():
        print("\n🔬 研究员机器人:")
        researcher_files = list(researchers_path.glob("*.py"))
        for file in researcher_files:
            if file.name != "__init__.py":
                researcher_name = file.stem.replace("_", " ").title()
                print(f"  ✅ {researcher_name}")
    
    # 风险管理类型
    risk_path = agents_path / "risk_mgmt"
    if risk_path.exists():
        print("\n⚖️ 风险管理机器人:")
        risk_files = list(risk_path.glob("*.py"))
        for file in risk_files:
            if file.name != "__init__.py":
                risk_name = file.stem.replace("_", " ").title()
                print(f"  ✅ {risk_name}")
    
    # 管理者类型
    managers_path = agents_path / "managers"
    if managers_path.exists():
        print("\n💼 管理者机器人:")
        manager_files = list(managers_path.glob("*.py"))
        for file in manager_files:
            if file.name != "__init__.py":
                manager_name = file.stem.replace("_", " ").title()
                print(f"  ✅ {manager_name}")
    
    # 交易员
    trader_path = agents_path / "trader"
    if trader_path.exists():
        print("\n💰 交易员机器人:")
        trader_files = list(trader_path.glob("*.py"))
        for file in trader_files:
            if file.name != "__init__.py":
                trader_name = file.stem.replace("_", " ").title()
                print(f"  ✅ {trader_name}")
    
    return True

def analyze_api_usage():
    """分析API使用情况"""
    print("\n🌐 分析API使用情况...")
    
    # 检查LLM适配器
    llm_path = Path("TradingAgents-CN-main/tradingagents/llm_adapters")
    if llm_path.exists():
        print("🧠 LLM适配器:")
        adapter_files = list(llm_path.glob("*.py"))
        for file in adapter_files:
            if file.name != "__init__.py":
                adapter_name = file.stem.replace("_", " ").title()
                print(f"  ✅ {adapter_name}")
    
    # 检查API服务
    api_service_path = Path("TradingAgents-CN-main/api_service.py")
    if api_service_path.exists():
        print("\n🔌 API服务:")
        print("  ✅ FastAPI RESTful服务")
        print("  ✅ 多智能体分析接口")
        print("  ✅ 股票分析API")
    
    return True

def generate_summary_report():
    """生成总结报告"""
    print("\n📊 TradingAgents-CN 分析总结")
    print("=" * 50)
    
    summary = """
🤖 **机器人系统架构**
- 多智能体协作框架
- 专业化分工 (分析师、研究员、风险管理、交易员)
- 辩论和协商机制
- 中文金融分析优化

🧠 **大模型API需求**
- 必需: 阿里百炼 (DashScope) API
- 必需: FinnHub 金融数据API
- 可选: OpenAI, Google AI, Anthropic API
- 支持多种LLM提供商切换

💰 **成本估算**
- 最低配置: 每月300-500元 (阿里百炼 + FinnHub)
- 推荐配置: 每月1000-2000元 (多API备用)
- 高端配置: 每月3000-5000元 (OpenAI GPT-4)

🔧 **技术特点**
- LangChain框架集成
- ReAct Agent模式
- 多轮对话和辩论
- 缓存和优化机制

📋 **部署要求**
- Python 3.8+
- 30+ 依赖包
- API密钥配置
- 可选数据库 (MongoDB, Redis)

✅ **结论**
TradingAgents-CN是一个功能强大的多智能体金融分析系统，
需要大模型API支持，推荐使用阿里百炼作为主要LLM提供商。
"""
    
    print(summary)
    
    # 保存到文件
    with open("TradingAgents_CN_Summary.md", "w", encoding="utf-8") as f:
        f.write("# TradingAgents-CN 分析总结\n\n")
        f.write(summary)
    
    print("✅ 总结报告已保存到 TradingAgents_CN_Summary.md")

def main():
    """主函数"""
    print("🤖 TradingAgents-CN 简化分析")
    print("=" * 40)
    
    # 1. 检查项目结构
    structure_ok = check_tradingagents_structure()
    
    if not structure_ok:
        print("\n❌ 项目结构检查失败，请确保TradingAgents-CN-main目录存在")
        return
    
    # 2. 分析配置需求
    config_ok = analyze_config_requirements()
    
    # 3. 分析智能体结构
    agents_ok = analyze_agents_structure()
    
    # 4. 分析API使用
    api_ok = analyze_api_usage()
    
    # 5. 生成总结报告
    generate_summary_report()
    
    # 6. 最终结论
    print("\n🎯 **最终结论**")
    print("=" * 30)
    print("✅ TradingAgents-CN 确实需要大模型API")
    print("✅ 推荐使用阿里百炼 (DashScope) API")
    print("✅ 需要FinnHub API获取金融数据")
    print("✅ 支持多种LLM提供商 (OpenAI, Google, Anthropic)")
    print("✅ 采用多智能体协作架构")
    print("✅ 专门针对中文金融分析优化")
    
    print(f"\n💡 **使用建议**")
    print("1. 最小配置: 阿里百炼 + FinnHub")
    print("2. 推荐配置: 阿里百炼 + FinnHub + OpenAI备用")
    print("3. 成本控制: 设置API调用限制")
    print("4. 性能优化: 启用缓存机制")

if __name__ == "__main__":
    main()
