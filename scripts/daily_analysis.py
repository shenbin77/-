#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日股票分析脚本
自动执行每日股票分析并生成报告
"""

import os
import sys
import json
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import requests

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/daily_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DailyAnalyzer:
    """每日分析器"""
    
    def __init__(self):
        self.db_path = 'stock_analysis.db'
        self.api_base_url = 'http://localhost:5000/api'
        
    def get_db_connection(self):
        """获取数据库连接"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return None
    
    def get_stock_list(self):
        """获取股票列表"""
        # 示例股票列表
        return [
            '000001', '000002', '600000', '600036', '000858',
            '002415', '300059', '000063', '600519', '000166'
        ]
    
    def analyze_single_stock(self, stock_code):
        """分析单只股票"""
        try:
            # 调用API进行分析
            response = requests.post(
                f'{self.api_base_url}/analysis/basic',
                json={'stock_code': stock_code},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"分析股票{stock_code}失败: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"分析股票{stock_code}异常: {e}")
            return None
    
    def generate_market_overview(self):
        """生成市场概览"""
        try:
            response = requests.get(
                f'{self.api_base_url}/data/market-overview',
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"获取市场概览失败: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"获取市场概览异常: {e}")
            return None
    
    def get_daily_recommendations(self):
        """获取每日推荐"""
        try:
            response = requests.get(
                f'{self.api_base_url}/recommendations/daily',
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"获取每日推荐失败: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"获取每日推荐异常: {e}")
            return None
    
    def save_analysis_result(self, analysis_data):
        """保存分析结果到数据库"""
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # 创建分析结果表（如果不存在）
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_date DATE NOT NULL,
                    stock_code TEXT,
                    analysis_type TEXT,
                    result_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 插入分析结果
            cursor.execute('''
                INSERT INTO daily_analysis 
                (analysis_date, stock_code, analysis_type, result_data)
                VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().strftime('%Y-%m-%d'),
                analysis_data.get('stock_code', ''),
                analysis_data.get('analysis_type', 'basic'),
                json.dumps(analysis_data, ensure_ascii=False)
            ))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"保存分析结果失败: {e}")
            return False
        finally:
            conn.close()
    
    def generate_daily_report(self, analysis_results):
        """生成每日报告"""
        try:
            report_date = datetime.now().strftime('%Y-%m-%d')
            report_content = {
                "report_date": report_date,
                "summary": {
                    "total_stocks_analyzed": len(analysis_results),
                    "successful_analysis": len([r for r in analysis_results if r is not None]),
                    "failed_analysis": len([r for r in analysis_results if r is None])
                },
                "market_overview": self.generate_market_overview(),
                "daily_recommendations": self.get_daily_recommendations(),
                "stock_analysis": analysis_results,
                "generated_at": datetime.now().isoformat()
            }
            
            # 保存报告到文件
            os.makedirs('reports', exist_ok=True)
            report_file = f'reports/daily_report_{report_date}.json'
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_content, f, ensure_ascii=False, indent=2)
            
            logger.info(f"每日报告已生成: {report_file}")
            return report_content
            
        except Exception as e:
            logger.error(f"生成每日报告失败: {e}")
            return None
    
    def run_daily_analysis(self):
        """执行每日分析"""
        logger.info("开始执行每日股票分析...")
        
        try:
            # 获取股票列表
            stock_list = self.get_stock_list()
            logger.info(f"待分析股票数量: {len(stock_list)}")
            
            # 分析每只股票
            analysis_results = []
            for stock_code in stock_list:
                logger.info(f"正在分析股票: {stock_code}")
                result = self.analyze_single_stock(stock_code)
                
                if result:
                    # 保存分析结果
                    self.save_analysis_result(result.get('data', {}))
                    analysis_results.append(result)
                    logger.info(f"股票{stock_code}分析完成")
                else:
                    analysis_results.append(None)
                    logger.warning(f"股票{stock_code}分析失败")
            
            # 生成每日报告
            report = self.generate_daily_report(analysis_results)
            
            if report:
                logger.info("每日分析执行完成")
                return True
            else:
                logger.error("每日报告生成失败")
                return False
                
        except Exception as e:
            logger.error(f"每日分析执行失败: {e}")
            return False

def main():
    """主函数"""
    # 创建必要的目录
    os.makedirs('logs', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    # 执行每日分析
    analyzer = DailyAnalyzer()
    success = analyzer.run_daily_analysis()
    
    if success:
        print("✅ 每日分析执行成功")
        sys.exit(0)
    else:
        print("❌ 每日分析执行失败")
        sys.exit(1)

if __name__ == '__main__':
    main()
