#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单的数据初始化脚本
只创建基础股票数据，避免复杂的模型冲突
"""

from app import create_app
from app.extensions import db
from datetime import datetime, timedelta
import random

def create_sample_data():
    """创建示例数据"""
    app = create_app()
    with app.app_context():
        try:
            # 直接使用SQL创建和插入数据
            with db.engine.connect() as conn:
                # 创建股票基本信息表
                conn.execute(db.text("""
                    CREATE TABLE IF NOT EXISTS stock_basic (
                        ts_code VARCHAR(20) PRIMARY KEY,
                        symbol VARCHAR(10),
                        name VARCHAR(50),
                        area VARCHAR(20),
                        industry VARCHAR(50),
                        list_date VARCHAR(10)
                    )
                """))
                
                # 创建股票日线历史数据表
                conn.execute(db.text("""
                    CREATE TABLE IF NOT EXISTS stock_daily_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ts_code VARCHAR(20),
                        trade_date VARCHAR(10),
                        open DECIMAL(10,2),
                        high DECIMAL(10,2),
                        low DECIMAL(10,2),
                        close DECIMAL(10,2),
                        pre_close DECIMAL(10,2),
                        change DECIMAL(10,2),
                        pct_chg DECIMAL(10,4),
                        vol BIGINT,
                        amount DECIMAL(20,2),
                        UNIQUE(ts_code, trade_date)
                    )
                """))
                
                # 插入股票基本信息
                stocks = [
                    ('000001.SZ', '000001', '平安银行', '深圳', '银行', '19910403'),
                    ('000002.SZ', '000002', '万科A', '深圳', '房地产开发', '19910129'),
                    ('000858.SZ', '000858', '五粮液', '四川', '白酒', '19980427'),
                    ('000876.SZ', '000876', '新希望', '四川', '饲料', '19980623'),
                    ('002415.SZ', '002415', '海康威视', '浙江', '安防设备', '20100528'),
                    ('600000.SH', '600000', '浦发银行', '上海', '银行', '19991110'),
                    ('600036.SH', '600036', '招商银行', '深圳', '银行', '20020409'),
                    ('600519.SH', '600519', '贵州茅台', '贵州', '白酒', '20010827'),
                    ('600887.SH', '600887', '伊利股份', '内蒙古', '乳品', '19961212')
                ]
                
                for stock in stocks:
                    conn.execute(db.text("""
                        INSERT OR REPLACE INTO stock_basic 
                        (ts_code, symbol, name, area, industry, list_date) 
                        VALUES (:ts_code, :symbol, :name, :area, :industry, :list_date)
                    """), {
                        'ts_code': stock[0],
                        'symbol': stock[1],
                        'name': stock[2],
                        'area': stock[3],
                        'industry': stock[4],
                        'list_date': stock[5]
                    })
                
                # 生成最近30天的示例交易数据
                end_date = datetime.now()
                start_date = end_date - timedelta(days=30)
                
                for stock in stocks[:5]:  # 只为前5只股票生成数据
                    ts_code = stock[0]
                    base_price = random.uniform(10, 100)
                    
                    current_date = start_date
                    while current_date <= end_date:
                        # 跳过周末
                        if current_date.weekday() < 5:
                            trade_date = current_date.strftime('%Y%m%d')
                            
                            # 生成随机价格数据
                            change_pct = random.uniform(-0.05, 0.05)
                            close = base_price * (1 + change_pct)
                            open_price = close * random.uniform(0.98, 1.02)
                            high = max(open_price, close) * random.uniform(1.0, 1.03)
                            low = min(open_price, close) * random.uniform(0.97, 1.0)
                            pre_close = base_price
                            change = close - pre_close
                            pct_chg = change_pct * 100
                            vol = random.randint(1000000, 10000000)
                            amount = vol * close
                            
                            conn.execute(db.text("""
                                INSERT OR REPLACE INTO stock_daily_history 
                                (ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount)
                                VALUES (:ts_code, :trade_date, :open, :high, :low, :close, :pre_close, :change, :pct_chg, :vol, :amount)
                            """), {
                                'ts_code': ts_code,
                                'trade_date': trade_date,
                                'open': round(open_price, 2),
                                'high': round(high, 2),
                                'low': round(low, 2),
                                'close': round(close, 2),
                                'pre_close': round(pre_close, 2),
                                'change': round(change, 2),
                                'pct_chg': round(pct_chg, 4),
                                'vol': vol,
                                'amount': round(amount, 2)
                            })
                            
                            base_price = close
                        
                        current_date += timedelta(days=1)
                
                conn.commit()
                
            print("✅ 示例数据创建成功")
            
            # 验证数据
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT COUNT(*) FROM stock_basic"))
                stock_count = result.fetchone()[0]
                
                result = conn.execute(db.text("SELECT COUNT(*) FROM stock_daily_history"))
                history_count = result.fetchone()[0]
                
                print(f"📊 股票数量: {stock_count}")
                print(f"📈 历史记录数量: {history_count}")
            
            return True
        except Exception as e:
            print(f"❌ 创建数据失败: {e}")
            return False

def main():
    """主函数"""
    print("🚀 开始创建示例数据...")
    
    if create_sample_data():
        print("🎉 数据初始化完成！")
    else:
        print("❌ 数据初始化失败！")

if __name__ == "__main__":
    main()
