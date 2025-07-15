#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据导入脚本
Stock Data Import Script
"""

import os
os.environ['TUSHARE_TOKEN'] = 'your_tushare_token_here'
os.environ['FLASK_SECRET_KEY'] = 'test-secret-key'

from app import create_app
from app.extensions import db
from app.models.stock import StockBasicInfo, StockDailyHistory

def import_basic_stocks():
    """导入基础股票数据"""
    basic_stocks = [
        {'symbol': '000001.SZ', 'name': '平安银行', 'market': 'SZ', 'industry': '银行'},
        {'symbol': '000002.SZ', 'name': '万科A', 'market': 'SZ', 'industry': '房地产'},
        {'symbol': '600036.SH', 'name': '招商银行', 'market': 'SH', 'industry': '银行'},
        {'symbol': '600519.SH', 'name': '贵州茅台', 'market': 'SH', 'industry': '白酒'},
        {'symbol': '000858.SZ', 'name': '五粮液', 'market': 'SZ', 'industry': '白酒'},
        {'symbol': '300750.SZ', 'name': '宁德时代', 'market': 'SZ', 'industry': '新能源'},
        {'symbol': '002415.SZ', 'name': '海康威视', 'market': 'SZ', 'industry': '电子'},
        {'symbol': '600276.SH', 'name': '恒瑞医药', 'market': 'SH', 'industry': '医药'},
        {'symbol': '002594.SZ', 'name': '比亚迪', 'market': 'SZ', 'industry': '汽车'},
        {'symbol': '600000.SH', 'name': '浦发银行', 'market': 'SH', 'industry': '银行'}
    ]
    
    app = create_app()
    with app.app_context():
        for stock_data in basic_stocks:
            existing = StockBasicInfo.query.filter_by(symbol=stock_data['symbol']).first()
            if not existing:
                stock = StockBasicInfo(**stock_data)
                db.session.add(stock)
                print(f"添加股票: {stock_data['symbol']} - {stock_data['name']}")
        
        db.session.commit()
        print("基础股票数据导入完成！")

if __name__ == "__main__":
    import_basic_stocks()
