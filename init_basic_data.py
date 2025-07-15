#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化基础股票数据
"""

from app import create_app
from app.extensions import db
from datetime import datetime, timedelta
import random

def create_basic_tables():
    """创建基础数据表"""
    app = create_app()
    with app.app_context():
        try:
            # 创建基础股票信息表
            with db.engine.connect() as conn:
                conn.execute(db.text("""
                    CREATE TABLE IF NOT EXISTS stock_basic (
                        ts_code VARCHAR(20) PRIMARY KEY,
                        symbol VARCHAR(10),
                        name VARCHAR(50),
                        area VARCHAR(20),
                        industry VARCHAR(50),
                        list_date VARCHAR(10),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                        change_c DECIMAL(10,2),
                        pct_chg DECIMAL(10,4),
                        vol BIGINT,
                        amount DECIMAL(20,2),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(ts_code, trade_date)
                    )
                """))

                # 创建股票日线基本数据表
                conn.execute(db.text("""
                    CREATE TABLE IF NOT EXISTS stock_daily_basic (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ts_code VARCHAR(20),
                        trade_date VARCHAR(10),
                        close DECIMAL(10,2),
                        turnover_rate DECIMAL(10,4),
                        pe DECIMAL(10,2),
                        pb DECIMAL(10,2),
                        ps DECIMAL(10,2),
                        total_mv DECIMAL(20,2),
                        circ_mv DECIMAL(20,2),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(ts_code, trade_date)
                    )
                """))

                # 创建资金流向表
                conn.execute(db.text("""
                    CREATE TABLE IF NOT EXISTS stock_moneyflow (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ts_code VARCHAR(20),
                        trade_date VARCHAR(10),
                        buy_sm_vol BIGINT,
                        buy_sm_amount DECIMAL(20,2),
                        sell_sm_vol BIGINT,
                        sell_sm_amount DECIMAL(20,2),
                        buy_md_vol BIGINT,
                        buy_md_amount DECIMAL(20,2),
                        sell_md_vol BIGINT,
                        sell_md_amount DECIMAL(20,2),
                        buy_lg_vol BIGINT,
                        buy_lg_amount DECIMAL(20,2),
                        sell_lg_vol BIGINT,
                        sell_lg_amount DECIMAL(20,2),
                        buy_elg_vol BIGINT,
                        buy_elg_amount DECIMAL(20,2),
                        sell_elg_vol BIGINT,
                        sell_elg_amount DECIMAL(20,2),
                        net_mf_vol BIGINT,
                        net_mf_amount DECIMAL(20,2),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(ts_code, trade_date)
                    )
                """))

                # 创建筹码分布表
                conn.execute(db.text("""
                    CREATE TABLE IF NOT EXISTS stock_cyq_perf (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ts_code VARCHAR(20),
                        trade_date VARCHAR(10),
                        his_high DECIMAL(10,2),
                        his_low DECIMAL(10,2),
                        cost_5pct DECIMAL(10,2),
                        cost_15pct DECIMAL(10,2),
                        cost_50pct DECIMAL(10,2),
                        cost_85pct DECIMAL(10,2),
                        cost_95pct DECIMAL(10,2),
                        weight_avg DECIMAL(10,2),
                        winner_rate DECIMAL(10,4),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(ts_code, trade_date)
                    )
                """))

                conn.commit()

            print("✅ 基础数据表创建成功")
            return True
        except Exception as e:
            print(f"❌ 创建表失败: {e}")
            return False

def insert_sample_data():
    """插入示例数据"""
    app = create_app()
    with app.app_context():
        try:
            # 示例股票列表
            sample_stocks = [
                ('000001.SZ', '000001', '平安银行', '深圳', '银行', '19910403'),
                ('000002.SZ', '000002', '万科A', '深圳', '房地产开发', '19910129'),
                ('000858.SZ', '000858', '五粮液', '四川', '白酒', '19980427'),
                ('000876.SZ', '000876', '新希望', '四川', '饲料', '19980623'),
                ('002415.SZ', '002415', '海康威视', '浙江', '安防设备', '20100528'),
                ('600000.SH', '600000', '浦发银行', '上海', '银行', '19991110'),
                ('600036.SH', '600036', '招商银行', '深圳', '银行', '20020409'),
                ('600519.SH', '600519', '贵州茅台', '贵州', '白酒', '20010827'),
                ('600887.SH', '600887', '伊利股份', '内蒙古', '乳品', '19961212'),
                ('000858.SZ', '000858', '五粮液', '四川', '白酒', '19980427')
            ]
            
            # 插入股票基本信息
            with db.engine.connect() as conn:
                for stock in sample_stocks:
                    try:
                        conn.execute(
                            db.text("INSERT OR IGNORE INTO stock_basic (ts_code, symbol, name, area, industry, list_date) VALUES (:ts_code, :symbol, :name, :area, :industry, :list_date)"),
                            {
                                'ts_code': stock[0],
                                'symbol': stock[1],
                                'name': stock[2],
                                'area': stock[3],
                                'industry': stock[4],
                                'list_date': stock[5]
                            }
                        )
                    except:
                        pass
                conn.commit()
            
            # 生成最近30天的示例交易数据
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            for stock in sample_stocks[:5]:  # 只为前5只股票生成数据
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
                        change_c = close - pre_close
                        pct_chg = change_pct * 100
                        vol = random.randint(1000000, 10000000)
                        amount = vol * close
                        
                        try:
                            with db.engine.connect() as conn:
                                conn.execute(db.text("""
                                    INSERT OR IGNORE INTO stock_daily_history
                                    (ts_code, trade_date, open, high, low, close, pre_close, change_c, pct_chg, vol, amount)
                                    VALUES (:ts_code, :trade_date, :open, :high, :low, :close, :pre_close, :change_c, :pct_chg, :vol, :amount)
                                """), {
                                    'ts_code': ts_code,
                                    'trade_date': trade_date,
                                    'open': open_price,
                                    'high': high,
                                    'low': low,
                                    'close': close,
                                    'pre_close': pre_close,
                                    'change_c': change_c,
                                    'pct_chg': pct_chg,
                                    'vol': vol,
                                    'amount': amount
                                })
                                conn.commit()
                        except:
                            pass
                        
                        base_price = close
                    
                    current_date += timedelta(days=1)
            
            print("✅ 示例数据插入成功")
            return True
        except Exception as e:
            print(f"❌ 插入数据失败: {e}")
            return False

def main():
    """主函数"""
    print("🚀 开始初始化基础股票数据...")
    
    # 创建表
    if not create_basic_tables():
        return False
    
    # 插入示例数据
    if not insert_sample_data():
        return False
    
    print("🎉 基础数据初始化完成！")
    return True

if __name__ == "__main__":
    main()
