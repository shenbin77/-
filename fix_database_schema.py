#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复数据库模式，使用SQLAlchemy模型重新创建表
"""

from app import create_app
from app.extensions import db
from app.models import (
    StockBasic, StockDailyHistory, StockDailyBasic, 
    StockMoneyflow, StockCyqPerf
)
from datetime import datetime, timedelta
import random

def recreate_tables():
    """重新创建表"""
    app = create_app()
    with app.app_context():
        try:
            # 删除现有表
            print("🗑️ 删除现有表...")
            db.drop_all()
            
            # 重新创建表
            print("🔨 创建新表...")
            db.create_all()
            
            print("✅ 表结构重新创建成功")
            return True
        except Exception as e:
            print(f"❌ 重新创建表失败: {e}")
            return False

def insert_sample_data():
    """插入示例数据"""
    app = create_app()
    with app.app_context():
        try:
            # 示例股票列表
            sample_stocks = [
                {
                    'ts_code': '000001.SZ',
                    'symbol': '000001', 
                    'name': '平安银行',
                    'area': '深圳',
                    'industry': '银行',
                    'list_date': datetime.strptime('19910403', '%Y%m%d').date()
                },
                {
                    'ts_code': '000002.SZ',
                    'symbol': '000002',
                    'name': '万科A', 
                    'area': '深圳',
                    'industry': '房地产开发',
                    'list_date': datetime.strptime('19910129', '%Y%m%d').date()
                },
                {
                    'ts_code': '000858.SZ',
                    'symbol': '000858',
                    'name': '五粮液',
                    'area': '四川', 
                    'industry': '白酒',
                    'list_date': datetime.strptime('19980427', '%Y%m%d').date()
                },
                {
                    'ts_code': '000876.SZ',
                    'symbol': '000876',
                    'name': '新希望',
                    'area': '四川',
                    'industry': '饲料',
                    'list_date': datetime.strptime('19980623', '%Y%m%d').date()
                },
                {
                    'ts_code': '002415.SZ',
                    'symbol': '002415',
                    'name': '海康威视',
                    'area': '浙江',
                    'industry': '安防设备',
                    'list_date': datetime.strptime('20100528', '%Y%m%d').date()
                },
                {
                    'ts_code': '600000.SH',
                    'symbol': '600000',
                    'name': '浦发银行',
                    'area': '上海',
                    'industry': '银行',
                    'list_date': datetime.strptime('19991110', '%Y%m%d').date()
                },
                {
                    'ts_code': '600036.SH',
                    'symbol': '600036',
                    'name': '招商银行',
                    'area': '深圳',
                    'industry': '银行',
                    'list_date': datetime.strptime('20020409', '%Y%m%d').date()
                },
                {
                    'ts_code': '600519.SH',
                    'symbol': '600519',
                    'name': '贵州茅台',
                    'area': '贵州',
                    'industry': '白酒',
                    'list_date': datetime.strptime('20010827', '%Y%m%d').date()
                },
                {
                    'ts_code': '600887.SH',
                    'symbol': '600887',
                    'name': '伊利股份',
                    'area': '内蒙古',
                    'industry': '乳品',
                    'list_date': datetime.strptime('19961212', '%Y%m%d').date()
                }
            ]
            
            # 插入股票基本信息
            print("📊 插入股票基本信息...")
            for stock_data in sample_stocks:
                stock = StockBasic(**stock_data)
                db.session.add(stock)
            
            db.session.commit()
            print(f"✅ 插入了 {len(sample_stocks)} 只股票的基本信息")
            
            # 生成最近30天的示例交易数据
            print("📈 生成历史交易数据...")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            for stock_data in sample_stocks[:5]:  # 只为前5只股票生成数据
                ts_code = stock_data['ts_code']
                base_price = random.uniform(10, 100)
                
                current_date = start_date
                while current_date <= end_date:
                    # 跳过周末
                    if current_date.weekday() < 5:
                        trade_date = current_date.date()
                        
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
                        
                        # 创建历史数据记录
                        history = StockDailyHistory(
                            ts_code=ts_code,
                            trade_date=trade_date,
                            open=round(open_price, 2),
                            high=round(high, 2),
                            low=round(low, 2),
                            close=round(close, 2),
                            pre_close=round(pre_close, 2),
                            change=round(change_c, 2),
                            pct_chg=round(pct_chg, 4),
                            vol=vol,
                            amount=round(amount, 2)
                        )
                        
                        db.session.add(history)
                        base_price = close
                    
                    current_date += timedelta(days=1)
            
            db.session.commit()
            print("✅ 历史交易数据生成完成")
            
            return True
        except Exception as e:
            print(f"❌ 插入数据失败: {e}")
            db.session.rollback()
            return False

def main():
    """主函数"""
    print("🚀 开始修复数据库模式...")
    
    # 重新创建表
    if not recreate_tables():
        return False
    
    # 插入示例数据
    if not insert_sample_data():
        return False
    
    print("🎉 数据库模式修复完成！")
    return True

if __name__ == "__main__":
    main()
