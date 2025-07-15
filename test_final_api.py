#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终API测试
"""

import requests
import json

def test_ml_based_selection():
    """测试基于ML模型的选股"""
    url = 'http://localhost:5001/api/ml-factor/scoring/ml-based'
    data = {
        "trade_date": "2024-01-15",
        "model_ids": ["my_xgb_model"],
        "top_n": 5
    }
    
    print("🔍 测试基于ML模型选股...")
    print(f"📡 POST {url}")
    print(f"📤 请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 错误: {response.text}")
            
    except Exception as e:
        print(f"❌ 异常: {e}")

def test_factor_calculation():
    """测试因子计算"""
    url = 'http://localhost:5001/api/ml-factor/factors/calculate'
    data = {
        "trade_date": "2025-07-15",
        "factor_ids": ["momentum_1d", "momentum_5d"]
    }
    
    print("\n🔍 测试因子计算...")
    print(f"📡 POST {url}")
    print(f"📤 请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 错误: {response.text}")
            
    except Exception as e:
        print(f"❌ 异常: {e}")

def test_factor_based_selection():
    """测试基于因子的选股"""
    url = 'http://localhost:5001/api/ml-factor/scoring/factor-based'
    data = {
        "trade_date": "2025-07-15",
        "factor_list": ["momentum_1d", "momentum_5d"],
        "method": "equal_weight",
        "top_n": 5
    }
    
    print("\n🔍 测试基于因子选股...")
    print(f"📡 POST {url}")
    print(f"📤 请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 错误: {response.text}")
            
    except Exception as e:
        print(f"❌ 异常: {e}")

def main():
    """主函数"""
    print("🚀 开始最终API测试...")
    
    # 测试因子计算
    test_factor_calculation()
    
    # 测试基于因子的选股
    test_factor_based_selection()
    
    # 测试基于ML模型的选股
    test_ml_based_selection()
    
    print("\n🎉 最终测试完成！")

if __name__ == "__main__":
    main()
