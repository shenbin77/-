#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查股票数据完整性
Check Stock Data Completeness
"""

import os
import sys
from datetime import datetime
from sqlalchemy import text

# 设置环境变量
os.environ['TUSHARE_TOKEN'] = 'your_tushare_token_here'
os.environ['FLASK_SECRET_KEY'] = 'test-secret-key'

try:
    from app import create_app
    from app.extensions import db
    from app.services.stock_service import StockService
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    sys.exit(1)

def check_database_tables():
    """检查数据库表结构"""
    print("🔍 检查数据库表结构...")
    
    app = create_app()
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # 检查所有表
                result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
                tables = [row[0] for row in result.fetchall()]
                
                print(f"📋 数据库中的表 ({len(tables)}个):")
                for table in tables:
                    print(f"  ✅ {table}")
                
                return tables
                
        except Exception as e:
            print(f"❌ 检查表结构失败: {e}")
            return []

def check_stock_basic_info():
    """检查股票基本信息"""
    print("\n📊 检查股票基本信息...")

    app = create_app()
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # 检查总数 (使用实际的表名 stock_basic)
                result = conn.execute(text("SELECT COUNT(*) as count FROM stock_basic"))
                total_count = result.fetchone()[0]
                print(f"📈 股票总数: {total_count}只")

                if total_count > 0:
                    # 检查各行业分布
                    result = conn.execute(text("SELECT industry, COUNT(*) as count FROM stock_basic GROUP BY industry"))
                    industries = result.fetchall()
                    print(f"🏢 各行业分布:")
                    for industry, count in industries:
                        print(f"  {industry}: {count}只")

                    # 检查样本数据
                    result = conn.execute(text("SELECT ts_code, name, area, industry FROM stock_basic LIMIT 10"))
                    samples = result.fetchall()
                    print(f"📋 样本数据 (前10只):")
                    for ts_code, name, area, industry in samples:
                        print(f"  {ts_code} - {name} ({area}, {industry})")

                return total_count

        except Exception as e:
            print(f"❌ 检查股票基本信息失败: {e}")
            return 0

def check_stock_history_data():
    """检查股票历史数据"""
    print("\n📈 检查股票历史数据...")

    app = create_app()
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # 检查总记录数
                result = conn.execute(text("SELECT COUNT(*) as count FROM stock_daily_history"))
                total_records = result.fetchone()[0]
                print(f"📊 历史数据记录总数: {total_records}条")

                if total_records > 0:
                    # 检查数据日期范围 (使用实际的列名 trade_date)
                    result = conn.execute(text("SELECT MIN(trade_date) as min_date, MAX(trade_date) as max_date FROM stock_daily_history"))
                    min_date, max_date = result.fetchone()
                    print(f"📅 数据日期范围: {min_date} 到 {max_date}")

                    # 检查有数据的股票数量 (使用实际的列名 ts_code)
                    result = conn.execute(text("SELECT COUNT(DISTINCT ts_code) as count FROM stock_daily_history"))
                    stocks_with_data = result.fetchone()[0]
                    print(f"📈 有历史数据的股票数: {stocks_with_data}只")

                    # 检查最新数据
                    result = conn.execute(text("SELECT ts_code, trade_date, close FROM stock_daily_history ORDER BY trade_date DESC LIMIT 5"))
                    latest_data = result.fetchall()
                    print(f"📊 最新数据样本:")
                    for ts_code, trade_date, close in latest_data:
                        print(f"  {ts_code}: {trade_date} 收盘价 {close}")

                return total_records

        except Exception as e:
            print(f"❌ 检查历史数据失败: {e}")
            return 0

def check_stock_service():
    """检查股票服务功能"""
    print("\n🔧 检查股票服务功能...")
    
    app = create_app()
    with app.app_context():
        try:
            service = StockService()
            
            # 检查股票列表获取
            stocks = service.get_stock_list()
            print(f"📋 通过服务获取的股票数: {len(stocks)}只")
            
            if len(stocks) > 0:
                print(f"📊 样本股票:")
                for i, stock in enumerate(stocks[:5]):
                    print(f"  {i+1}. {stock}")
            
            return len(stocks)
            
        except Exception as e:
            print(f"❌ 检查股票服务失败: {e}")
            return 0

def check_major_stocks():
    """检查主要股票是否存在"""
    print("\n🔍 检查主要股票是否存在...")

    # 主要股票列表
    major_stocks = [
        ('000001.SZ', '平安银行'),
        ('000002.SZ', '万科A'),
        ('600036.SH', '招商银行'),
        ('600519.SH', '贵州茅台'),
        ('000858.SZ', '五粮液'),
        ('300750.SZ', '宁德时代'),
        ('002415.SZ', '海康威视'),
        ('600276.SH', '恒瑞医药'),
        ('002594.SZ', '比亚迪'),
        ('600000.SH', '浦发银行'),
        ('000876.SZ', '新希望')
    ]

    app = create_app()
    with app.app_context():
        found_count = 0
        missing_stocks = []

        try:
            with db.engine.connect() as conn:
                for ts_code, expected_name in major_stocks:
                    result = conn.execute(text("SELECT name FROM stock_basic WHERE ts_code = :ts_code"), {"ts_code": ts_code})
                    stock_data = result.fetchone()

                    if stock_data:
                        print(f"  ✅ {ts_code} - {stock_data[0]}")
                        found_count += 1
                    else:
                        print(f"  ❌ {ts_code} - {expected_name} (未找到)")
                        missing_stocks.append((ts_code, expected_name))

                print(f"\n📊 主要股票检查结果:")
                print(f"  ✅ 找到: {found_count}/{len(major_stocks)}只")
                print(f"  ❌ 缺失: {len(missing_stocks)}只")

                if missing_stocks:
                    print(f"📋 缺失的股票:")
                    for ts_code, name in missing_stocks:
                        print(f"  - {ts_code} ({name})")

                return found_count, missing_stocks

        except Exception as e:
            print(f"❌ 检查主要股票失败: {e}")
            return 0, major_stocks

def generate_stock_import_script():
    """生成股票数据导入脚本"""
    print("\n🔧 生成股票数据导入脚本...")
    
    script_content = '''#!/usr/bin/env python3
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
'''
    
    with open('import_basic_stocks.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("✅ 已生成 import_basic_stocks.py 脚本")

def main():
    """主函数"""
    print("🔍 股票数据完整性检查")
    print("=" * 50)
    
    # 检查数据库表
    tables = check_database_tables()
    
    if 'stock_basic' not in tables:
        print("❌ 缺少 stock_basic 表")
        return False

    if 'stock_daily_history' not in tables:
        print("❌ 缺少 stock_daily_history 表")
        return False
    
    # 检查股票基本信息
    basic_count = check_stock_basic_info()
    
    # 检查历史数据
    history_count = check_stock_history_data()
    
    # 检查股票服务
    service_count = check_stock_service()
    
    # 检查主要股票
    found_count, missing_stocks = check_major_stocks()
    
    # 生成导入脚本
    generate_stock_import_script()
    
    # 总结
    print("\n📊 检查结果总结:")
    print(f"  📋 数据库表: {'✅ 完整' if len(tables) >= 2 else '❌ 不完整'}")
    print(f"  📈 股票基本信息: {basic_count}只")
    print(f"  📊 历史数据记录: {history_count}条")
    print(f"  🔧 服务可用股票: {service_count}只")
    print(f"  🎯 主要股票覆盖: {found_count}/12只")
    
    if basic_count >= 10 and found_count >= 8:
        print("\n✅ 股票数据基本完整，可以正常使用")
        return True
    else:
        print("\n⚠️ 股票数据不完整，建议运行导入脚本")
        print("💡 运行命令: python import_basic_stocks.py")
        return False

if __name__ == "__main__":
    main()
