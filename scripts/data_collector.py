#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据收集脚本
从各种数据源收集股票数据
"""

import os
import sys
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import time

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataCollector:
    """数据收集器"""
    
    def __init__(self):
        self.db_path = 'stock_analysis.db'
        self.init_database()
    
    def get_db_connection(self):
        """获取数据库连接"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return None
    
    def init_database(self):
        """初始化数据库"""
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # 创建股票基本信息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_info (
                    stock_code TEXT PRIMARY KEY,
                    stock_name TEXT,
                    industry TEXT,
                    market TEXT,
                    list_date DATE,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建股票价格数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_prices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_code TEXT NOT NULL,
                    trade_date DATE NOT NULL,
                    open_price REAL,
                    high_price REAL,
                    low_price REAL,
                    close_price REAL,
                    volume REAL,
                    amount REAL,
                    change_percent REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(stock_code, trade_date)
                )
            ''')
            
            # 创建财务数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS financial_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_code TEXT NOT NULL,
                    report_date DATE NOT NULL,
                    revenue REAL,
                    net_profit REAL,
                    total_assets REAL,
                    total_equity REAL,
                    pe_ratio REAL,
                    pb_ratio REAL,
                    roe REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(stock_code, report_date)
                )
            ''')
            
            conn.commit()
            logger.info("数据库初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            return False
        finally:
            conn.close()
    
    def generate_sample_stock_info(self):
        """生成示例股票基本信息"""
        sample_stocks = [
            ('000001', '平安银行', '银行', '深圳主板', '1991-04-03'),
            ('000002', '万科A', '房地产', '深圳主板', '1991-01-29'),
            ('600000', '浦发银行', '银行', '上海主板', '1999-11-10'),
            ('600036', '招商银行', '银行', '上海主板', '2002-04-09'),
            ('000858', '五粮液', '食品饮料', '深圳主板', '1998-04-27'),
            ('002415', '海康威视', '电子', '深圳中小板', '2010-05-28'),
            ('300059', '东方财富', '非银金融', '创业板', '2010-03-19'),
            ('000063', '中兴通讯', '通信', '深圳主板', '1997-11-18'),
            ('600519', '贵州茅台', '食品饮料', '上海主板', '2001-08-27'),
            ('000166', '申万宏源', '非银金融', '深圳主板', '1994-06-17')
        ]
        
        return sample_stocks
    
    def collect_stock_info(self):
        """收集股票基本信息"""
        logger.info("开始收集股票基本信息...")
        
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            sample_stocks = self.generate_sample_stock_info()
            
            for stock_code, stock_name, industry, market, list_date in sample_stocks:
                cursor.execute('''
                    INSERT OR REPLACE INTO stock_info 
                    (stock_code, stock_name, industry, market, list_date)
                    VALUES (?, ?, ?, ?, ?)
                ''', (stock_code, stock_name, industry, market, list_date))
            
            conn.commit()
            logger.info(f"成功收集{len(sample_stocks)}只股票的基本信息")
            return True
            
        except Exception as e:
            logger.error(f"收集股票基本信息失败: {e}")
            return False
        finally:
            conn.close()
    
    def generate_sample_price_data(self, stock_code, days=30):
        """生成示例价格数据"""
        np.random.seed(hash(stock_code) % 2**32)
        
        # 基础价格
        base_price = np.random.uniform(10, 200)
        
        # 生成价格序列
        prices = []
        current_price = base_price
        
        for i in range(days):
            # 随机波动
            change = np.random.normal(0, 0.02)  # 2%的日波动
            current_price *= (1 + change)
            
            # 确保价格为正
            current_price = max(current_price, 1.0)
            
            # 生成OHLC数据
            high = current_price * np.random.uniform(1.0, 1.05)
            low = current_price * np.random.uniform(0.95, 1.0)
            open_price = np.random.uniform(low, high)
            close_price = current_price
            
            # 成交量
            volume = int(np.random.uniform(1000000, 50000000))
            amount = volume * close_price
            
            # 涨跌幅
            if i > 0:
                change_percent = (close_price - prices[i-1]['close_price']) / prices[i-1]['close_price'] * 100
            else:
                change_percent = 0
            
            trade_date = (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')
            
            prices.append({
                'stock_code': stock_code,
                'trade_date': trade_date,
                'open_price': round(open_price, 2),
                'high_price': round(high, 2),
                'low_price': round(low, 2),
                'close_price': round(close_price, 2),
                'volume': volume,
                'amount': round(amount, 2),
                'change_percent': round(change_percent, 2)
            })
        
        return prices
    
    def collect_price_data(self, stock_codes=None, days=30):
        """收集股票价格数据"""
        if stock_codes is None:
            stock_codes = [info[0] for info in self.generate_sample_stock_info()]
        
        logger.info(f"开始收集{len(stock_codes)}只股票的价格数据...")
        
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            total_records = 0
            
            for stock_code in stock_codes:
                logger.info(f"收集股票{stock_code}的价格数据...")
                
                price_data = self.generate_sample_price_data(stock_code, days)
                
                for data in price_data:
                    cursor.execute('''
                        INSERT OR REPLACE INTO stock_prices 
                        (stock_code, trade_date, open_price, high_price, low_price, 
                         close_price, volume, amount, change_percent)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        data['stock_code'], data['trade_date'], data['open_price'],
                        data['high_price'], data['low_price'], data['close_price'],
                        data['volume'], data['amount'], data['change_percent']
                    ))
                
                total_records += len(price_data)
                time.sleep(0.1)  # 避免过快请求
            
            conn.commit()
            logger.info(f"成功收集{total_records}条价格数据")
            return True
            
        except Exception as e:
            logger.error(f"收集价格数据失败: {e}")
            return False
        finally:
            conn.close()
    
    def generate_sample_financial_data(self, stock_code):
        """生成示例财务数据"""
        np.random.seed(hash(stock_code) % 2**32)
        
        # 生成最近4个季度的财务数据
        financial_data = []
        base_date = datetime.now()
        
        for i in range(4):
            # 报告期
            quarter = (base_date.month - 1) // 3 + 1 - i
            year = base_date.year
            if quarter <= 0:
                quarter += 4
                year -= 1
            
            report_date = f"{year}-{quarter*3:02d}-30"
            
            # 财务指标
            revenue = np.random.uniform(1000000000, 50000000000)  # 营收
            net_profit = revenue * np.random.uniform(0.05, 0.25)  # 净利润
            total_assets = revenue * np.random.uniform(2, 8)  # 总资产
            total_equity = total_assets * np.random.uniform(0.3, 0.7)  # 净资产
            pe_ratio = np.random.uniform(10, 50)  # 市盈率
            pb_ratio = np.random.uniform(1, 10)  # 市净率
            roe = net_profit / total_equity * 100  # ROE
            
            financial_data.append({
                'stock_code': stock_code,
                'report_date': report_date,
                'revenue': round(revenue, 2),
                'net_profit': round(net_profit, 2),
                'total_assets': round(total_assets, 2),
                'total_equity': round(total_equity, 2),
                'pe_ratio': round(pe_ratio, 2),
                'pb_ratio': round(pb_ratio, 2),
                'roe': round(roe, 2)
            })
        
        return financial_data
    
    def collect_financial_data(self, stock_codes=None):
        """收集财务数据"""
        if stock_codes is None:
            stock_codes = [info[0] for info in self.generate_sample_stock_info()]
        
        logger.info(f"开始收集{len(stock_codes)}只股票的财务数据...")
        
        conn = self.get_db_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            total_records = 0
            
            for stock_code in stock_codes:
                logger.info(f"收集股票{stock_code}的财务数据...")
                
                financial_data = self.generate_sample_financial_data(stock_code)
                
                for data in financial_data:
                    cursor.execute('''
                        INSERT OR REPLACE INTO financial_data 
                        (stock_code, report_date, revenue, net_profit, total_assets,
                         total_equity, pe_ratio, pb_ratio, roe)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        data['stock_code'], data['report_date'], data['revenue'],
                        data['net_profit'], data['total_assets'], data['total_equity'],
                        data['pe_ratio'], data['pb_ratio'], data['roe']
                    ))
                
                total_records += len(financial_data)
                time.sleep(0.1)
            
            conn.commit()
            logger.info(f"成功收集{total_records}条财务数据")
            return True
            
        except Exception as e:
            logger.error(f"收集财务数据失败: {e}")
            return False
        finally:
            conn.close()
    
    def run_data_collection(self):
        """执行数据收集"""
        logger.info("开始执行数据收集任务...")
        
        try:
            # 收集股票基本信息
            if not self.collect_stock_info():
                logger.error("股票基本信息收集失败")
                return False
            
            # 收集价格数据
            if not self.collect_price_data():
                logger.error("价格数据收集失败")
                return False
            
            # 收集财务数据
            if not self.collect_financial_data():
                logger.error("财务数据收集失败")
                return False
            
            logger.info("数据收集任务执行完成")
            return True
            
        except Exception as e:
            logger.error(f"数据收集任务执行失败: {e}")
            return False

def main():
    """主函数"""
    # 创建必要的目录
    os.makedirs('logs', exist_ok=True)
    
    # 执行数据收集
    collector = DataCollector()
    success = collector.run_data_collection()
    
    if success:
        print("✅ 数据收集执行成功")
        sys.exit(0)
    else:
        print("❌ 数据收集执行失败")
        sys.exit(1)

if __name__ == '__main__':
    main()
