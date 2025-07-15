#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成分析报告脚本
"""

import os
import sys
import json
import logging
import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import AnalysisResult, Stock

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_daily_report():
    """生成每日分析报告"""
    try:
        app = create_app()
        with app.app_context():
            today = datetime.date.today()
            
            # 获取今日分析结果
            results = AnalysisResult.query.filter_by(analysis_date=today).all()
            
            if not results:
                logger.warning("今日没有分析结果")
                return False
            
            # 生成报告数据
            report_data = {
                'date': today.isoformat(),
                'total_analyzed': len(results),
                'recommendations': {
                    'BUY': [],
                    'SELL': [],
                    'HOLD': []
                },
                'summary': {
                    'buy_count': 0,
                    'sell_count': 0,
                    'hold_count': 0
                }
            }
            
            # 分类推荐
            for result in results:
                rec_type = result.recommendation
                stock_info = {
                    'stock_code': result.stock_code,
                    'confidence': result.confidence,
                    'target_price': result.target_price,
                    'analysis_data': result.analysis_data
                }
                
                if rec_type in report_data['recommendations']:
                    report_data['recommendations'][rec_type].append(stock_info)
                    report_data['summary'][f'{rec_type.lower()}_count'] += 1
            
            # 保存JSON报告
            reports_dir = Path('reports')
            reports_dir.mkdir(exist_ok=True)
            
            json_file = reports_dir / f'daily_report_{today.isoformat()}.json'
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            # 生成HTML报告
            html_content = generate_html_report(report_data)
            html_file = reports_dir / f'daily_report_{today.isoformat()}.html'
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"报告已生成: {json_file}, {html_file}")
            return True
            
    except Exception as e:
        logger.error(f"生成报告失败: {e}")
        return False

def generate_html_report(data):
    """生成HTML格式报告"""
    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日股票分析报告 - {data['date']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
        .summary {{ display: flex; justify-content: space-around; margin: 20px 0; }}
        .summary-item {{ text-align: center; padding: 10px; background-color: #e9e9e9; border-radius: 5px; }}
        .recommendations {{ margin: 20px 0; }}
        .rec-section {{ margin: 15px 0; }}
        .rec-title {{ font-size: 18px; font-weight: bold; margin-bottom: 10px; }}
        .stock-item {{ background-color: #f9f9f9; padding: 10px; margin: 5px 0; border-radius: 3px; }}
        .buy {{ border-left: 4px solid #4CAF50; }}
        .sell {{ border-left: 4px solid #f44336; }}
        .hold {{ border-left: 4px solid #ff9800; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>每日股票分析报告</h1>
        <p>日期: {data['date']}</p>
        <p>分析股票总数: {data['total_analyzed']}</p>
    </div>
    
    <div class="summary">
        <div class="summary-item">
            <h3>买入推荐</h3>
            <p>{data['summary']['buy_count']}</p>
        </div>
        <div class="summary-item">
            <h3>卖出推荐</h3>
            <p>{data['summary']['sell_count']}</p>
        </div>
        <div class="summary-item">
            <h3>持有推荐</h3>
            <p>{data['summary']['hold_count']}</p>
        </div>
    </div>
    
    <div class="recommendations">
"""
    
    # 添加推荐详情
    for rec_type, stocks in data['recommendations'].items():
        if stocks:
            css_class = rec_type.lower()
            html += f"""
        <div class="rec-section">
            <div class="rec-title">{rec_type} 推荐 ({len(stocks)}只)</div>
"""
            for stock in stocks:
                html += f"""
            <div class="stock-item {css_class}">
                <strong>股票代码:</strong> {stock['stock_code']} | 
                <strong>置信度:</strong> {stock['confidence']:.2f} | 
                <strong>目标价:</strong> {stock['target_price']:.2f}
            </div>
"""
            html += "        </div>\n"
    
    html += """
    </div>
    
    <div class="footer">
        <p><small>本报告由AI自动生成，仅供参考，不构成投资建议。</small></p>
    </div>
</body>
</html>
"""
    return html

def main():
    """主函数"""
    try:
        success = generate_daily_report()
        if success:
            logger.info("报告生成成功")
            sys.exit(0)
        else:
            logger.error("报告生成失败")
            sys.exit(1)
    except Exception as e:
        logger.error(f"脚本执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
