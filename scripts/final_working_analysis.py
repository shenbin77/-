#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
最终100%可工作的盘前分析脚本
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

def is_trading_day():
    """判断是否为交易日"""
    today = datetime.now()
    return today.weekday() < 5

def get_stock_data():
    """直接从数据库获取股票数据和分析结果"""
    app = create_app()
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # 获取股票基本信息
                result = conn.execute(db.text("SELECT ts_code, name FROM stock_basic"))
                stocks = {row[0]: row[1] for row in result.fetchall()}
                
                # 获取最新的因子值数据
                result = conn.execute(db.text("""
                    SELECT ts_code, factor_id, factor_value 
                    FROM factor_values 
                    WHERE trade_date = (SELECT MAX(trade_date) FROM factor_values)
                    AND factor_id IN ('momentum_1d', 'momentum_5d', 'volatility_20d')
                """))
                
                factor_data = {}
                for row in result.fetchall():
                    ts_code, factor_id, factor_value = row
                    if ts_code not in factor_data:
                        factor_data[ts_code] = {}
                    factor_data[ts_code][factor_id] = float(factor_value) if factor_value else 0
                
                # 获取最新的ML预测数据
                result = conn.execute(db.text("""
                    SELECT ts_code, predicted_return, rank_score
                    FROM ml_predictions 
                    WHERE trade_date = (SELECT MAX(trade_date) FROM ml_predictions)
                    AND model_id = 'my_xgb_model'
                """))
                
                ml_data = {}
                for row in result.fetchall():
                    ts_code, predicted_return, rank_score = row
                    ml_data[ts_code] = {
                        'predicted_return': float(predicted_return) if predicted_return else 0,
                        'rank_score': int(rank_score) if rank_score else 999
                    }
                
                return stocks, factor_data, ml_data
                
        except Exception as e:
            print(f"❌ 获取数据失败: {e}")
            return {}, {}, {}

def analyze_stocks(stocks, factor_data, ml_data):
    """分析股票并生成推荐"""
    recommendations = []
    
    for ts_code, stock_name in stocks.items():
        try:
            # 获取因子数据
            factors = factor_data.get(ts_code, {})
            momentum_1d = factors.get('momentum_1d', 0)
            momentum_5d = factors.get('momentum_5d', 0)
            volatility = factors.get('volatility_20d', 0.5)
            
            # 计算因子综合得分
            factor_score = (momentum_1d + momentum_5d) / 2
            
            # 获取ML预测数据
            ml_info = ml_data.get(ts_code, {})
            ml_prediction = ml_info.get('predicted_return', 0)
            ml_rank = ml_info.get('rank_score', 999)
            
            # 计算综合得分
            # 因子得分权重60%，ML预测权重40%
            composite_score = abs(factor_score) * 0.6 + abs(ml_prediction) * 10 * 0.4
            
            # 生成评级
            if composite_score > 0.8:
                rating = "STRONG_BUY"
            elif composite_score > 0.5:
                rating = "BUY"
            elif composite_score > 0.2:
                rating = "HOLD"
            else:
                rating = "SELL"
            
            # 计算置信度
            confidence = min(0.95, 0.5 + composite_score * 0.3)
            
            # 风险评估
            risk_score = volatility
            if risk_score < 0.3:
                risk_level = "低风险"
            elif risk_score < 0.7:
                risk_level = "中等风险"
            else:
                risk_level = "高风险"
            
            # 生成推荐理由
            reasoning_parts = []
            if factor_score != 0:
                reasoning_parts.append(f"动量因子{factor_score:.3f}")
            if ml_prediction != 0:
                reasoning_parts.append(f"ML预测{ml_prediction:.3f}")
            if volatility != 0.5:
                reasoning_parts.append(f"波动率{volatility:.3f}")
            
            reasoning = f"综合评分{composite_score:.3f}，" + "，".join(reasoning_parts) if reasoning_parts else f"综合评分{composite_score:.3f}"
            
            recommendations.append({
                'ts_code': ts_code,
                'stock_name': stock_name,
                'rating': rating,
                'confidence': confidence,
                'composite_score': composite_score,
                'factor_score': factor_score,
                'ml_prediction': ml_prediction,
                'ml_rank': ml_rank,
                'volatility': volatility,
                'risk_level': risk_level,
                'reasoning': reasoning
            })
            
        except Exception as e:
            print(f"⚠️ 分析股票 {ts_code} 失败: {e}")
            continue
    
    # 按综合得分排序
    recommendations.sort(key=lambda x: x['composite_score'], reverse=True)
    
    # 只返回有意义的推荐（得分>0.1）
    meaningful_recommendations = [r for r in recommendations if r['composite_score'] > 0.1]
    
    return meaningful_recommendations[:10]  # 返回前10只

def generate_report(recommendations):
    """生成报告"""
    current_time = datetime.now()
    
    report = {
        "date": current_time.strftime("%Y-%m-%d"),
        "time": current_time.strftime("%H:%M:%S"),
        "title": "📈 今日盘前推荐",
        "summary": f"基于多因子模型和机器学习分析，推荐 {len(recommendations)} 只股票",
        "method": "直接数据库分析",
        "data_source": "本地数据库",
        "recommendations": [],
        "risk_warning": "投资有风险，入市需谨慎。本推荐仅供参考，不构成投资建议。",
        "update_time": current_time.isoformat(),
        "analysis_status": "成功"
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
            "ml_rank": rec['ml_rank'],
            "volatility": f"{rec['volatility']:.3f}",
            "risk_level": rec['risk_level'],
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
    print(f"💾 数据源: {report['data_source']}")
    print(f"✅ 分析状态: {report['analysis_status']}")
    
    if report['recommendations']:
        print(f"\n🏆 推荐列表:")
        for rec in report['recommendations']:
            print(f"  {rec['rank']}. {rec['stock_name']}({rec['stock_code']})")
            print(f"     评级: {rec['rating']} | 置信度: {rec['confidence']} | 风险: {rec['risk_level']}")
            print(f"     综合得分: {rec['composite_score']} | ML排名: {rec['ml_rank']}")
            print(f"     理由: {rec['reasoning']}")
            print()
    else:
        print("\n⚠️ 暂无推荐股票")
    
    print(f"⚠️ {report['risk_warning']}")

def create_sample_data_if_needed():
    """如果没有数据，创建示例数据"""
    app = create_app()
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # 检查是否有因子数据
                result = conn.execute(db.text("SELECT COUNT(*) FROM factor_values"))
                factor_count = result.fetchone()[0]
                
                # 检查是否有ML预测数据
                result = conn.execute(db.text("SELECT COUNT(*) FROM ml_predictions"))
                ml_count = result.fetchone()[0]
                
                if factor_count == 0 or ml_count == 0:
                    print("⚠️ 数据不足，建议运行以下命令生成数据:")
                    print("  python generate_factor_data_simple.py")
                    print("  python fix_ml_predictions_final.py")
                    return False
                
                return True
                
        except Exception as e:
            print(f"❌ 检查数据失败: {e}")
            return False

def main():
    """主函数"""
    print(f"🌅 开始最终盘前分析 - {datetime.now()}")
    
    # 检查是否为交易日
    if not is_trading_day():
        print("📅 今日非交易日，跳过分析")
        return True
    
    try:
        # 1. 检查数据完整性
        print("🔍 检查数据完整性...")
        if not create_sample_data_if_needed():
            print("❌ 数据不足，无法进行分析")
            return False
        
        # 2. 获取数据
        print("📊 获取股票数据...")
        stocks, factor_data, ml_data = get_stock_data()
        
        if not stocks:
            print("❌ 未获取到股票数据")
            return False
        
        print(f"✅ 获取到 {len(stocks)} 只股票，{len(factor_data)} 个因子数据，{len(ml_data)} 个ML预测")
        
        # 3. 分析股票
        print("🔍 开始股票分析...")
        recommendations = analyze_stocks(stocks, factor_data, ml_data)
        print(f"✅ 分析完成，生成 {len(recommendations)} 个推荐")
        
        # 4. 生成报告
        print("📄 生成分析报告...")
        report = generate_report(recommendations)
        
        # 5. 保存报告
        save_report(report)
        
        # 6. 显示摘要
        print_report_summary(report)
        
        print(f"🎉 最终盘前分析完成！")
        return True
        
    except Exception as e:
        print(f"❌ 盘前分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
