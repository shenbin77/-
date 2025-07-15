#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试多因子模型系统API
"""

import requests
import json
import time

# 服务器地址 - 根据您的系统调整端口
BASE_URL = 'http://localhost:5001'  # 我们的系统运行在5001端口

def test_api_call(method, url, data=None, description=""):
    """测试API调用"""
    print(f"\n🔍 测试: {description}")
    print(f"📡 {method.upper()} {url}")
    
    try:
        if method.lower() == 'get':
            response = requests.get(url)
        elif method.lower() == 'post':
            response = requests.post(url, json=data)
            if data:
                print(f"📤 请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        print(f"📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return result
        else:
            print(f"❌ 错误: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 异常: {e}")
        return None

def main():
    """主测试函数"""
    print("🚀 开始测试多因子模型系统API...")
    
    # 1. 测试获取因子列表
    test_api_call(
        'GET', 
        f'{BASE_URL}/api/ml-factor/factors/list',
        description="获取因子列表"
    )
    
    # 2. 测试创建自定义因子
    factor_data = {
        "factor_id": "custom_momentum",
        "factor_name": "自定义动量因子",
        "factor_type": "momentum",
        "factor_formula": "close.pct_change(10)",
        "description": "10日价格变化率"
    }
    test_api_call(
        'POST',
        f'{BASE_URL}/api/ml-factor/factors/custom',
        factor_data,
        "创建自定义因子"
    )
    
    # 3. 测试计算因子值
    calc_data = {
        "trade_date": "2024-01-15",
        "factor_ids": ["momentum_1d", "momentum_5d"]
    }
    test_api_call(
        'POST',
        f'{BASE_URL}/api/ml-factor/factors/calculate',
        calc_data,
        "计算因子值"
    )
    
    # 4. 测试创建模型
    model_data = {
        "model_id": "my_xgb_model",
        "model_name": "我的XGBoost模型",
        "model_type": "xgboost",
        "factor_list": ["momentum_1d", "momentum_5d", "volatility_20d"],
        "target_type": "return_5d"
    }
    test_api_call(
        'POST',
        f'{BASE_URL}/api/ml-factor/models/create',
        model_data,
        "创建模型"
    )
    
    # 5. 测试训练模型
    train_data = {
        "model_id": "my_xgb_model",
        "start_date": "2023-01-01",
        "end_date": "2023-12-31"
    }
    test_api_call(
        'POST',
        f'{BASE_URL}/api/ml-factor/models/train',
        train_data,
        "训练模型"
    )
    
    # 6. 测试基于因子选股
    selection_data = {
        "trade_date": "2024-01-15",
        "factor_list": ["momentum_1d", "momentum_5d"],
        "method": "equal_weight",
        "top_n": 50
    }
    test_api_call(
        'POST',
        f'{BASE_URL}/api/ml-factor/scoring/factor-based',
        selection_data,
        "基于因子选股"
    )
    
    # 7. 测试基于ML模型选股
    ml_selection_data = {
        "trade_date": "2024-01-15",
        "model_ids": ["my_xgb_model"],
        "top_n": 50
    }
    test_api_call(
        'POST',
        f'{BASE_URL}/api/ml-factor/scoring/ml-based',
        ml_selection_data,
        "基于ML模型选股"
    )
    
    # 8. 测试其他基础API
    print("\n" + "="*50)
    print("🔍 测试基础API...")
    
    # 测试股票列表
    test_api_call(
        'GET',
        f'{BASE_URL}/api/stocks?page_size=5',
        description="获取股票列表"
    )
    
    # 测试行业列表
    test_api_call(
        'GET',
        f'{BASE_URL}/api/industries',
        description="获取行业列表"
    )
    
    # 测试地区列表
    test_api_call(
        'GET',
        f'{BASE_URL}/api/areas',
        description="获取地区列表"
    )
    
    print("\n🎉 API测试完成！")

if __name__ == "__main__":
    main()
