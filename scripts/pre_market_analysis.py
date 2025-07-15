#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
盘前分析脚本 - 每个交易日早上8:30执行
"""

import asyncio
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
from app.services.trading_agents_service import unified_decision_engine

def is_trading_day():
    """判断是否为交易日"""
    today = datetime.now()
    # 简单判断：周一到周五，排除节假日
    if today.weekday() >= 5:  # 周末
        return False
    
    # TODO: 可以添加节假日判断
    return True

def get_active_stock_pool():
    """获取活跃股票池"""
    app = create_app()
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # 获取所有股票，后续可以根据条件筛选
                result = conn.execute(db.text("SELECT ts_code, name FROM stock_basic"))
                stocks = result.fetchall()
                return [stock[0] for stock in stocks]
        except Exception as e:
            print(f"❌ 获取股票池失败: {e}")
            return ["000001.SZ", "000002.SZ", "600000.SH", "600036.SH", "000858.SZ"]

def analyze_stock_batch(stock_codes, trade_date):
    """批量分析股票"""
    analysis_results = []
    
    for stock_code in stock_codes:
        try:
            print(f"🔍 分析股票: {stock_code}")
            
            # 使用统一决策引擎进行分析
            result = unified_decision_engine.comprehensive_analysis(stock_code, trade_date)
            
            if result.get('success'):
                analysis_results.append(result)
                print(f"✅ {stock_code} 分析完成")
            else:
                print(f"⚠️ {stock_code} 分析失败: {result.get('error', '未知错误')}")
                
        except Exception as e:
            print(f"❌ {stock_code} 分析异常: {e}")
    
    return analysis_results

def filter_recommendations(analysis_results):
    """筛选推荐股票"""
    recommendations = []
    
    for result in analysis_results:
        if not result.get('success'):
            continue
            
        final_decision = result.get('final_decision', {})
        rating = final_decision.get('rating', 'HOLD')
        confidence = final_decision.get('confidence', 0)
        
        # 筛选条件：BUY或STRONG_BUY，且置信度>60%
        if rating in ['BUY', 'STRONG_BUY'] and confidence > 0.6:
            recommendations.append(result)
        # 也包含高置信度的HOLD
        elif rating == 'HOLD' and confidence > 0.8:
            recommendations.append(result)
    
    # 按置信度排序
    recommendations.sort(key=lambda x: x['final_decision']['confidence'], reverse=True)
    
    return recommendations[:10]  # 返回前10只

def get_stock_name(stock_code):
    """获取股票名称"""
    app = create_app()
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT name FROM stock_basic WHERE ts_code = :code"), 
                                    {'code': stock_code})
                row = result.fetchone()
                return row[0] if row else stock_code
        except:
            return stock_code

def get_risk_level_text(risk_score):
    """获取风险等级文本"""
    if risk_score < 0.3:
        return "低风险"
    elif risk_score < 0.7:
        return "中等风险"
    else:
        return "高风险"

def generate_pre_market_report(recommendations):
    """生成盘前报告"""
    current_time = datetime.now()
    
    report = {
        "date": current_time.strftime("%Y-%m-%d"),
        "time": current_time.strftime("%H:%M:%S"),
        "title": "📈 今日盘前推荐",
        "summary": f"基于量化分析和AI智能体综合评估，今日推荐 {len(recommendations)} 只股票",
        "total_analyzed": len(recommendations),
        "recommendations": [],
        "market_outlook": "基于技术面和基本面分析",
        "risk_warning": "投资有风险，入市需谨慎。本推荐仅供参考，不构成投资建议。",
        "analysis_method": "多因子模型 + 机器学习 + AI智能体分析",
        "update_time": current_time.isoformat()
    }
    
    for i, rec in enumerate(recommendations, 1):
        stock_code = rec.get('stock_code', '')
        final_decision = rec.get('final_decision', {})
        ai_analysis = rec.get('ai_analysis', {})
        quant_analysis = rec.get('quantitative_analysis', {})
        
        # 获取量化分析得分
        factor_scores = quant_analysis.get('factor_scores', {})
        ml_prediction = quant_analysis.get('ml_prediction', {})
        
        recommendation = {
            "rank": i,
            "stock_code": stock_code,
            "stock_name": get_stock_name(stock_code),
            "rating": final_decision.get('rating', 'HOLD'),
            "confidence": f"{final_decision.get('confidence', 0):.1%}",
            "reasoning": final_decision.get('reasoning', ''),
            "risk_level": get_risk_level_text(final_decision.get('risk_level', 0.5)),
            "target_price": ai_analysis.get('target_price', ''),
            "predicted_return": f"{ml_prediction.get('predicted_return', 0):.2%}",
            "momentum_score": f"{factor_scores.get('momentum_score', 0):.2f}",
            "value_score": f"{factor_scores.get('value_score', 0):.2f}",
            "ai_available": ai_analysis.get('ai_available', False),
            "analysis_timestamp": rec.get('analysis_timestamp', '')
        }
        
        report["recommendations"].append(recommendation)
    
    return report

def save_report(report, filename="daily_analysis_report.json"):
    """保存报告到文件"""
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
    print(f"🔍 分析方法: {report['analysis_method']}")
    
    print(f"\n🏆 推荐列表:")
    for rec in report['recommendations'][:5]:  # 显示前5只
        print(f"  {rec['rank']}. {rec['stock_name']}({rec['stock_code']})")
        print(f"     评级: {rec['rating']} | 置信度: {rec['confidence']} | 风险: {rec['risk_level']}")
        print(f"     预测收益: {rec['predicted_return']} | 动量得分: {rec['momentum_score']}")
        print(f"     理由: {rec['reasoning'][:100]}...")
        print()
    
    print(f"⚠️ {report['risk_warning']}")

def main():
    """主函数"""
    print(f"🌅 开始盘前分析 - {datetime.now()}")
    
    # 检查是否为交易日
    if not is_trading_day():
        print("📅 今日非交易日，跳过分析")
        return
    
    try:
        # 1. 获取股票池
        print("📋 获取股票池...")
        stock_pool = get_active_stock_pool()
        print(f"📊 股票池包含 {len(stock_pool)} 只股票")
        
        # 2. 批量分析
        print("🔍 开始批量分析...")
        trade_date = datetime.now().strftime('%Y-%m-%d')
        analysis_results = analyze_stock_batch(stock_pool, trade_date)
        print(f"✅ 完成 {len(analysis_results)} 只股票分析")
        
        # 3. 筛选推荐
        print("🎯 筛选推荐股票...")
        recommendations = filter_recommendations(analysis_results)
        print(f"📈 筛选出 {len(recommendations)} 只推荐股票")
        
        # 4. 生成报告
        print("📄 生成分析报告...")
        report = generate_pre_market_report(recommendations)
        
        # 5. 保存报告
        save_report(report)
        
        # 6. 显示摘要
        print_report_summary(report)
        
        print(f"🎉 盘前分析完成！推荐 {len(recommendations)} 只股票")
        
        # 返回成功状态
        return True
        
    except Exception as e:
        print(f"❌ 盘前分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
