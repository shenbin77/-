#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试修复后的ML API功能
"""

import requests
import json

BASE_URL = 'http://localhost:5001'

def test_create_model():
    """测试创建模型"""
    url = f'{BASE_URL}/api/ml-factor/models/create'
    data = {
        "model_id": "test_new_model",
        "model_name": "测试新模型",
        "model_type": "xgboost",
        "factor_list": ["momentum_1d", "momentum_5d", "volatility_20d"],
        "target_type": "return_5d"
    }
    
    print("🔍 测试创建模型...")
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

def test_train_model():
    """测试训练模型"""
    url = f'{BASE_URL}/api/ml-factor/models/train'
    data = {
        "model_id": "my_xgb_model",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31"
    }
    
    print("\n🔍 测试训练模型...")
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

def test_get_models():
    """测试获取模型列表"""
    url = f'{BASE_URL}/api/ml-factor/models/list'
    
    print("\n🔍 测试获取模型列表...")
    print(f"📡 GET {url}")
    
    try:
        response = requests.get(url)
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 错误: {response.text}")
            
    except Exception as e:
        print(f"❌ 异常: {e}")

def test_model_predict():
    """测试模型预测"""
    url = f'{BASE_URL}/api/ml-factor/models/predict'
    data = {
        "model_id": "my_xgb_model",
        "trade_date": "2024-01-15"
    }
    
    print("\n🔍 测试模型预测...")
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
    print("🚀 开始测试修复后的ML API功能...")
    
    # 1. 测试获取模型列表
    test_get_models()
    
    # 2. 测试创建模型
    test_create_model()
    
    # 3. 测试训练模型
    test_train_model()
    
    # 4. 测试模型预测
    test_model_predict()
    
    print("\n🎉 ML API功能测试完成！")

if __name__ == "__main__":
    main()
