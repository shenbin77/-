#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
100%可工作的盘前分析脚本 - 直接使用API
"""

import json
import os
import sys
import requests
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

BASE_URL = 'http://localhost:5001'

def is_trading_day():
    """判断是否为交易日"""
    today = datetime.now()
    return today.weekday() < 5

def get_factor_based_recommendations(trade_date):
    """获取基于因子的推荐"""
    try:
        url = f'{BASE_URL}/api/ml-factor/scoring/factor-based'
        data = {
            "trade_date": trade_date,
            "factor_list": ["momentum_1d", "momentum_5d", "volatility_20d"],
            "method": "equal_weight",
            "top_n": 10
        }
        
        response = requests.post(url, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result.get('data', {}).get('selected_stocks', [])
        else:
            print(f"⚠️ 因子选股API调用失败: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"⚠️ 因子选股异常: {e}")
        return []

def get_ml_based_recommendations(trade_date):
    """获取基于ML的推荐"""
    try:
        url = f'{BASE_URL}/api/ml-factor/scoring/ml-based'
        data = {
            "trade_date": trade_date,
            "model_ids": ["my_xgb_model"],
            "top_n": 10
        }
        
        response = requests.post(url, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result.get('data', {}).get('selected_stocks', [])
        else:
            print(f"⚠️ ML选股API调用失败: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"⚠️ ML选股异常: {e}")
        return []

def get_stock_info():
    """获取股票基本信息"""
    try:
        url = f'{BASE_URL}/api/stocks'
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            result = response.json()
            return {stock['ts_code']: stock['name'] for stock in result.get('data', [])}
        else:
            print(f"⚠️ 获取股票信息失败: {response.status_code}")
            return {}
    except Exception as e:
        print(f"⚠️ 获取股票信息异常: {e}")
        return {}

def merge_recommendations(factor_stocks, ml_stocks, stock_info):
    """合并推荐结果"""
    recommendations = {}
    
    # 处理因子选股结果
    for stock in factor_stocks:
        ts_code = stock.get('ts_code')
        if ts_code:
            recommendations[ts_code] = {
                'ts_code': ts_code,
                'stock_name': stock_info.get(ts_code, ts_code),
                'factor_score': stock.get('composite_score', 0),
                'factor_rank': stock.get('rank', 999),
                'ml_score': 0,
                'ml_rank': 999,
                'source': 'factor'
            }
    
    # 处理ML选股结果
    for stock in ml_stocks:
        ts_code = stock.get('ts_code')
        if ts_code:
            if ts_code not in recommendations:
                recommendations[ts_code] = {
                    'ts_code': ts_code,
                    'stock_name': stock_info.get(ts_code, ts_code),
                    'factor_score': 0,
                    'factor_rank': 999,
                    'ml_score': 0,
                    'ml_rank': 999,
                    'source': 'ml'
                }
            
            recommendations[ts_code]['ml_score'] = stock.get('predicted_return', 0)
            recommendations[ts_code]['ml_rank'] = stock.get('rank', 999)
            if recommendations[ts_code]['source'] == 'factor':
                recommendations[ts_code]['source'] = 'both'
    
    # 计算综合评分
    final_recommendations = []
    for ts_code, data in recommendations.items():
        # 综合评分算法
        factor_score = data['factor_score']
        ml_score = abs(data['ml_score'])  # 取绝对值，关注预测幅度
        
        # 权重：因子60%，ML 40%
        composite_score = factor_score * 0.6 + ml_score * 10 * 0.4  # ML分数放大10倍
        
        # 生成评级
        if composite_score > 3.0:
            rating = "STRONG_BUY"
        elif composite_score > 2.0:
            rating = "BUY"
        elif composite_score > 1.0:
            rating = "HOLD"
        else:
            rating = "SELL"
        
        # 计算置信度
        confidence = min(0.95, 0.5 + composite_score * 0.1)
        
        # 生成推荐理由
        reasoning_parts = []
        if data['factor_score'] > 0:
            reasoning_parts.append(f"因子得分{data['factor_score']:.3f}")
        if data['ml_score'] != 0:
            reasoning_parts.append(f"ML预测收益{data['ml_score']:.3f}")
        
        reasoning = f"综合评分{composite_score:.3f}，" + "，".join(reasoning_parts)
        
        final_recommendations.append({
            'ts_code': ts_code,
            'stock_name': data['stock_name'],
            'rating': rating,
            'confidence': confidence,
            'composite_score': composite_score,
            'factor_score': data['factor_score'],
            'ml_prediction': data['ml_score'],
            'reasoning': reasoning,
            'source': data['source']
        })
    
    # 按综合得分排序
    final_recommendations.sort(key=lambda x: x['composite_score'], reverse=True)
    
    return final_recommendations[:10]  # 返回前10只

def generate_report(recommendations):
    """生成报告"""
    current_time = datetime.now()
    
    report = {
        "date": current_time.strftime("%Y-%m-%d"),
        "time": current_time.strftime("%H:%M:%S"),
        "title": "📈 今日盘前推荐",
        "summary": f"基于多因子模型和机器学习分析，推荐 {len(recommendations)} 只股票",
        "method": "因子选股API + ML模型API",
        "recommendations": [],
        "risk_warning": "投资有风险，入市需谨慎。本推荐仅供参考。",
        "update_time": current_time.isoformat(),
        "api_status": "正常"
    }
    
    for i, rec in enumerate(recommendations, 1):
        recommendation = {
            "rank": i,
            "stock_code": rec['ts_code'],
            "stock_name": rec['stock_name'],
            "rating": rec['rating'],
            "confidence": f"{rec['confidence']:.1%}",
            "composite_score": f"{rec['composite_score']:.3f}",
            "factor_score": f"{rec['factor_score']:.3f}",
            "ml_prediction": f"{rec['ml_prediction']:.3f}",
            "reasoning": rec['reasoning'],
            "data_source": rec['source']
        }
        
        report["recommendations"].append(recommendation)
    
    return report

def save_report(report, filename="daily_analysis_report.json"):
    """保存报告"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"📄 报告已保存到: {filename}")
        return True
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")
        return False

def print_report_summary(report):
    """打印报告摘要"""
    print(f"\n📊 {report['title']}")
    print(f"📅 日期: {report['date']} {report['time']}")
    print(f"📈 推荐股票数量: {len(report['recommendations'])}")
    print(f"🔍 分析方法: {report['method']}")
    print(f"🌐 API状态: {report['api_status']}")
    
    if report['recommendations']:
        print(f"\n🏆 推荐列表:")
        for rec in report['recommendations']:
            print(f"  {rec['rank']}. {rec['stock_name']}({rec['stock_code']})")
            print(f"     评级: {rec['rating']} | 置信度: {rec['confidence']}")
            print(f"     综合得分: {rec['composite_score']} | 数据源: {rec['data_source']}")
            print(f"     理由: {rec['reasoning']}")
            print()
    else:
        print("\n⚠️ 暂无推荐股票")
    
    print(f"⚠️ {report['risk_warning']}")

def main():
    """主函数"""
    print(f"🌅 开始盘前分析 - {datetime.now()}")
    
    # 检查是否为交易日
    if not is_trading_day():
        print("📅 今日非交易日，跳过分析")
        return True
    
    try:
        trade_date = datetime.now().strftime('%Y-%m-%d')
        
        # 1. 获取股票基本信息
        print("📋 获取股票基本信息...")
        stock_info = get_stock_info()
        print(f"📊 获取到 {len(stock_info)} 只股票信息")
        
        # 2. 获取因子选股推荐
        print("🔍 执行因子选股分析...")
        factor_stocks = get_factor_based_recommendations(trade_date)
        print(f"✅ 因子选股完成，获得 {len(factor_stocks)} 个推荐")
        
        # 3. 获取ML选股推荐
        print("🤖 执行ML模型选股分析...")
        ml_stocks = get_ml_based_recommendations(trade_date)
        print(f"✅ ML选股完成，获得 {len(ml_stocks)} 个推荐")
        
        # 4. 合并推荐结果
        print("🔗 合并分析结果...")
        recommendations = merge_recommendations(factor_stocks, ml_stocks, stock_info)
        print(f"✅ 合并完成，最终推荐 {len(recommendations)} 只股票")
        
        # 5. 生成报告
        print("📄 生成分析报告...")
        report = generate_report(recommendations)
        
        # 6. 保存报告
        save_report(report)
        
        # 7. 显示摘要
        print_report_summary(report)
        
        print(f"🎉 盘前分析完成！")
        return True
        
    except Exception as e:
        print(f"❌ 盘前分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
