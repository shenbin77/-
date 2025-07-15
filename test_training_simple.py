#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单测试训练功能
"""

import requests
import json

def test_training_with_available_dates():
    """使用可用日期测试训练"""
    url = 'http://localhost:5001/api/ml-factor/models/train'
    
    # 使用我们数据的实际日期范围
    data = {
        "model_id": "my_xgb_model",
        "start_date": "2024-01-01",  # 使用更近的日期
        "end_date": "2025-07-15"
    }
    
    print("🔍 测试模型训练（使用可用日期）...")
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

def test_training_with_all_dates():
    """使用全部日期测试训练"""
    url = 'http://localhost:5001/api/ml-factor/models/train'
    
    # 不指定具体日期，让系统使用所有可用数据
    data = {
        "model_id": "my_xgb_model",
        "start_date": "2020-01-01",  # 很早的日期
        "end_date": "2030-12-31"     # 很晚的日期
    }
    
    print("\n🔍 测试模型训练（使用全部日期）...")
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
    print("🚀 开始简单训练测试...")
    
    # 1. 使用可用日期测试
    test_training_with_available_dates()
    
    # 2. 使用全部日期测试
    test_training_with_all_dates()
    
    print("\n🎉 训练测试完成！")

if __name__ == "__main__":
    main()
