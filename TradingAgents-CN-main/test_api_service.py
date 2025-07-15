#!/usr/bin/env python3
"""
TradingAgents-CN API服务测试脚本
"""

import requests
import json
import time
from typing import Dict, Any

# API服务地址
API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ 健康检查通过")
            print(f"   响应: {response.json()}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_supported_analysts():
    """测试获取支持的分析师"""
    print("\n🔍 测试获取支持的分析师...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/supported_analysts")
        if response.status_code == 200:
            data = response.json()
            print("✅ 获取分析师列表成功")
            for analyst in data["analysts"]:
                print(f"   - {analyst['name']} ({analyst['type']}): {analyst['description']}")
            return True
        else:
            print(f"❌ 获取分析师列表失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取分析师列表异常: {e}")
        return False

def test_supported_models():
    """测试获取支持的模型"""
    print("\n🔍 测试获取支持的模型...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/supported_models")
        if response.status_code == 200:
            data = response.json()
            print("✅ 获取模型列表成功")
            for provider, info in data["providers"].items():
                print(f"   - {info['name']} ({provider}): {', '.join(info['models'])}")
            return True
        else:
            print(f"❌ 获取模型列表失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取模型列表异常: {e}")
        return False

def test_stock_analysis(stock_code: str = "000001.SZ", use_simple_config: bool = True):
    """测试股票分析"""
    print(f"\n🔍 测试股票分析: {stock_code}")
    
    # 构建请求数据
    if use_simple_config:
        # 简单配置，适合快速测试
        request_data = {
            "stock_code": stock_code,
            "market": "A股",
            "analysis_config": {
                "analysts": ["market", "fundamentals"],
                "depth": "quick",
                "llm_provider": "dashscope",
                "model": "qwen-turbo",
                "max_debate_rounds": 1,
                "online_tools": True
            }
        }
    else:
        # 完整配置，包含量化数据
        request_data = {
            "stock_code": stock_code,
            "market": "A股",
            "quantitative_data": {
                "pe_ratio": 12.5,
                "pb_ratio": 1.2,
                "roe": 0.15,
                "current_price": 15.68,
                "ma5": 15.2,
                "ma20": 14.8,
                "rsi": 65.2,
                "macd": 0.12
            },
            "analysis_config": {
                "analysts": ["market", "fundamentals", "news"],
                "depth": "standard",
                "llm_provider": "dashscope",
                "model": "qwen-plus",
                "max_debate_rounds": 2,
                "online_tools": True
            }
        }
    
    try:
        print(f"   发送请求...")
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/analyze_stock",
            json=request_data,
            timeout=300  # 5分钟超时
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                result = data["data"]
                print("✅ 股票分析成功")
                print(f"   耗时: {duration:.1f}秒")
                print(f"   股票: {result['stock_name']} ({result['stock_code']})")
                print(f"   建议: {result['overall_rating']}")
                print(f"   置信度: {result['confidence_score']:.1%}")
                print(f"   风险评分: {result['risk_score']:.1%}")
                print(f"   摘要: {result['summary']}")
                
                # 显示智能体观点
                if result.get('agents_opinions'):
                    print("   智能体观点:")
                    for opinion in result['agents_opinions']:
                        print(f"     - {opinion['agent_type']}: 评分 {opinion['score']:.2f}")
                
                return True
            else:
                print(f"❌ 股票分析失败: {data['error']}")
                return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时（5分钟）")
        return False
    except Exception as e:
        print(f"❌ 股票分析异常: {e}")
        return False

def run_comprehensive_test():
    """运行综合测试"""
    print("🧪 开始 TradingAgents-CN API 综合测试")
    print("=" * 60)
    
    # 测试列表
    tests = [
        ("健康检查", test_health_check),
        ("支持的分析师", test_supported_analysts),
        ("支持的模型", test_supported_models),
        ("股票分析（简单）", lambda: test_stock_analysis("000001.SZ", True)),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📈 总体结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！API服务运行正常")
    else:
        print("⚠️  部分测试失败，请检查服务配置")

def interactive_test():
    """交互式测试"""
    print("🎮 进入交互式测试模式")
    print("输入股票代码进行分析，输入 'quit' 退出")
    
    while True:
        stock_code = input("\n请输入股票代码 (如 000001.SZ): ").strip()
        
        if stock_code.lower() == 'quit':
            print("👋 退出交互式测试")
            break
        
        if not stock_code:
            print("⚠️  请输入有效的股票代码")
            continue
        
        test_stock_analysis(stock_code, True)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "interactive":
            interactive_test()
        elif sys.argv[1] == "quick":
            # 快速测试
            test_health_check()
            test_stock_analysis("000001.SZ", True)
        else:
            print("用法:")
            print("  python test_api_service.py           # 运行综合测试")
            print("  python test_api_service.py quick     # 快速测试")
            print("  python test_api_service.py interactive # 交互式测试")
    else:
        run_comprehensive_test()
