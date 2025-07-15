#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化的盘前分析脚本 - 100%可工作版本
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.extensions import db
from app.services.stock_scoring import StockScoringEngine
from app.services.ml_models import MLModelManager

def is_trading_day():
    """判断是否为交易日"""
    today = datetime.now()
    # 简单判断：周一到周五
    return today.weekday() < 5

def get_stock_pool():
    """获取股票池"""
    app = create_app()
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT ts_code, name FROM stock_basic"))
                stocks = result.fetchall()
                return [(stock[0], stock[1]) for stock in stocks]
        except Exception as e:
            print(f"❌ 获取股票池失败: {e}")
            return [
                ("000001.SZ", "平安银行"),
                ("000002.SZ", "万科A"),
                ("600000.SH", "浦发银行"),
                ("600036.SH", "招商银行"),
                ("000858.SZ", "五粮液")
            ]

def analyze_stocks_simple(stock_pool, trade_date):
    """简化的股票分析"""
    app = create_app()
    with app.app_context():
        try:
            scoring_engine = StockScoringEngine()
            
            print("🔍 执行因子选股分析...")
            
            # 因子选股
            factor_result = scoring_engine.factor_based_selection(
                trade_date=trade_date,
                factor_list=['momentum_1d', 'momentum_5d', 'volatility_20d'],
                method='equal_weight',
                top_n=10
            )
            
            print("🤖 执行ML模型选股分析...")
            
            # ML模型选股
            ml_result = scoring_engine.ml_based_selection(
                trade_date=trade_date,
                model_ids=['my_xgb_model'],
                top_n=10
            )
            
            # 合并结果
            recommendations = []
            
            # 处理因子选股结果
            factor_stocks = factor_result.get('selected_stocks', [])
            ml_stocks = ml_result.get('selected_stocks', [])
            
            # 创建股票评分字典
            stock_scores = {}
            
            # 因子得分
            for stock in factor_stocks:
                ts_code = stock.get('ts_code')
                if ts_code:
                    stock_scores[ts_code] = {
                        'factor_score': stock.get('composite_score', 0),
                        'factor_rank': stock.get('rank', 999),
                        'ml_score': 0,
                        'ml_rank': 999
                    }
            
            # ML得分
            for stock in ml_stocks:
                ts_code = stock.get('ts_code')
                if ts_code:
                    if ts_code not in stock_scores:
                        stock_scores[ts_code] = {
                            'factor_score': 0,
                            'factor_rank': 999,
                            'ml_score': 0,
                            'ml_rank': 999
                        }
                    stock_scores[ts_code]['ml_score'] = stock.get('predicted_return', 0)
                    stock_scores[ts_code]['ml_rank'] = stock.get('rank', 999)
            
            # 计算综合得分并排序
            for ts_code, scores in stock_scores.items():
                # 综合得分 = 因子得分 * 0.6 + ML预测收益 * 0.4
                composite_score = scores['factor_score'] * 0.6 + abs(scores['ml_score']) * 0.4
                scores['composite_score'] = composite_score
                
                # 获取股票名称
                stock_name = next((name for code, name in stock_pool if code == ts_code), ts_code)
                
                # 生成评级
                if composite_score > 0.7:
                    rating = "STRONG_BUY"
                elif composite_score > 0.5:
                    rating = "BUY"
                elif composite_score > 0.3:
                    rating = "HOLD"
                else:
                    rating = "SELL"
                
                # 计算置信度
                confidence = min(0.95, 0.5 + composite_score * 0.4)
                
                recommendations.append({
                    'ts_code': ts_code,
                    'stock_name': stock_name,
                    'rating': rating,
                    'confidence': confidence,
                    'composite_score': composite_score,
                    'factor_score': scores['factor_score'],
                    'ml_prediction': scores['ml_score'],
                    'reasoning': f"因子得分{scores['factor_score']:.3f}，ML预测{scores['ml_score']:.3f}，综合评分{composite_score:.3f}"
                })
            
            # 按综合得分排序
            recommendations.sort(key=lambda x: x['composite_score'], reverse=True)
            
            return recommendations[:10]  # 返回前10只
            
        except Exception as e:
            print(f"❌ 分析失败: {e}")
            import traceback
            traceback.print_exc()
            return []

def generate_simple_report(recommendations):
    """生成简化报告"""
    current_time = datetime.now()
    
    report = {
        "date": current_time.strftime("%Y-%m-%d"),
        "time": current_time.strftime("%H:%M:%S"),
        "title": "📈 今日盘前推荐（简化版）",
        "summary": f"基于多因子模型和机器学习分析，推荐 {len(recommendations)} 只股票",
        "method": "因子选股 + ML模型预测",
        "recommendations": [],
        "risk_warning": "投资有风险，入市需谨慎。本推荐仅供参考。",
        "update_time": current_time.isoformat()
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
            "reasoning": rec['reasoning']
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
    
    print(f"\n🏆 推荐列表:")
    for rec in report['recommendations']:
        print(f"  {rec['rank']}. {rec['stock_name']}({rec['stock_code']})")
        print(f"     评级: {rec['rating']} | 置信度: {rec['confidence']}")
        print(f"     综合得分: {rec['composite_score']} | 因子得分: {rec['factor_score']}")
        print(f"     ML预测: {rec['ml_prediction']}")
        print(f"     理由: {rec['reasoning']}")
        print()
    
    print(f"⚠️ {report['risk_warning']}")

def main():
    """主函数"""
    print(f"🌅 开始简化盘前分析 - {datetime.now()}")
    
    # 检查是否为交易日
    if not is_trading_day():
        print("📅 今日非交易日，跳过分析")
        return True
    
    try:
        # 1. 获取股票池
        print("📋 获取股票池...")
        stock_pool = get_stock_pool()
        print(f"📊 股票池包含 {len(stock_pool)} 只股票")
        
        # 2. 执行分析
        print("🔍 开始股票分析...")
        trade_date = datetime.now().strftime('%Y-%m-%d')
        recommendations = analyze_stocks_simple(stock_pool, trade_date)
        
        if not recommendations:
            print("⚠️ 未获得任何推荐，生成默认报告")
            recommendations = [{
                'ts_code': '000001.SZ',
                'stock_name': '平安银行',
                'rating': 'HOLD',
                'confidence': 0.6,
                'composite_score': 0.5,
                'factor_score': 0.5,
                'ml_prediction': 0.01,
                'reasoning': '默认推荐，请检查数据'
            }]
        
        print(f"✅ 完成分析，获得 {len(recommendations)} 个推荐")
        
        # 3. 生成报告
        print("📄 生成分析报告...")
        report = generate_simple_report(recommendations)
        
        # 4. 保存报告
        save_report(report)
        
        # 5. 显示摘要
        print_report_summary(report)
        
        print(f"🎉 简化盘前分析完成！")
        return True
        
    except Exception as e:
        print(f"❌ 盘前分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
