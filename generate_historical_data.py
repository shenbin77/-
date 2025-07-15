#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成更多历史数据以支持因子计算和模型训练
"""

from app import create_app
from app.extensions import db
from datetime import datetime, timedelta
import random
import pandas as pd
import numpy as np

def generate_extended_historical_data():
    """生成扩展的历史数据"""
    app = create_app()
    with app.app_context():
        try:
            # 获取现有股票列表
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT ts_code, name FROM stock_basic"))
                stocks = result.fetchall()
                
                print(f"📊 为 {len(stocks)} 只股票生成历史数据...")
                
                # 生成过去2年的数据（足够计算各种因子）
                end_date = datetime.now()
                start_date = end_date - timedelta(days=730)  # 2年
                
                for stock in stocks:
                    ts_code = stock[0]
                    stock_name = stock[1]
                    
                    print(f"  📈 生成 {ts_code} ({stock_name}) 的历史数据...")
                    
                    # 删除现有数据
                    conn.execute(db.text("DELETE FROM stock_daily_history WHERE ts_code = :ts_code"), 
                               {'ts_code': ts_code})
                    
                    # 生成基础价格（根据股票类型设定不同的价格范围）
                    if '600' in ts_code or '000001' in ts_code:  # 大盘股
                        base_price = random.uniform(15, 80)
                    elif '002' in ts_code:  # 中小板
                        base_price = random.uniform(8, 40)
                    else:  # 其他
                        base_price = random.uniform(5, 30)
                    
                    current_date = start_date
                    current_price = base_price
                    
                    # 生成价格走势趋势
                    trend_days = 0
                    trend_direction = random.choice([-1, 1])
                    trend_strength = random.uniform(0.001, 0.003)
                    
                    while current_date <= end_date:
                        # 跳过周末
                        if current_date.weekday() < 5:
                            trade_date = current_date.strftime('%Y-%m-%d')
                            
                            # 趋势变化
                            trend_days += 1
                            if trend_days > random.randint(5, 20):  # 趋势持续5-20天
                                trend_direction = random.choice([-1, 1])
                                trend_strength = random.uniform(0.001, 0.003)
                                trend_days = 0
                            
                            # 计算价格变化
                            trend_change = trend_direction * trend_strength
                            random_change = random.uniform(-0.08, 0.08)  # 日内随机波动
                            total_change = trend_change + random_change
                            
                            # 限制单日涨跌幅
                            total_change = max(-0.10, min(0.10, total_change))
                            
                            # 计算新价格
                            new_price = current_price * (1 + total_change)
                            new_price = max(0.1, new_price)  # 价格不能为负
                            
                            # 生成OHLC数据
                            close = round(new_price, 2)
                            pre_close = round(current_price, 2)
                            
                            # 开盘价在前收盘价附近波动
                            open_price = round(pre_close * (1 + random.uniform(-0.03, 0.03)), 2)
                            
                            # 最高价和最低价
                            high = round(max(open_price, close) * (1 + random.uniform(0, 0.05)), 2)
                            low = round(min(open_price, close) * (1 - random.uniform(0, 0.05)), 2)
                            
                            # 确保价格逻辑正确
                            high = max(high, open_price, close)
                            low = min(low, open_price, close)
                            
                            # 计算涨跌额和涨跌幅
                            change = round(close - pre_close, 2)
                            pct_chg = round((change / pre_close) * 100, 4) if pre_close > 0 else 0
                            
                            # 生成成交量（与价格变化相关）
                            volume_base = random.randint(1000000, 10000000)
                            volume_multiplier = 1 + abs(pct_chg) * 0.1  # 涨跌幅越大，成交量越大
                            vol = int(volume_base * volume_multiplier)
                            
                            # 计算成交额
                            amount = round(vol * (high + low + open_price + close) / 4, 2)
                            
                            # 插入数据
                            conn.execute(db.text("""
                                INSERT INTO stock_daily_history 
                                (ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount)
                                VALUES (:ts_code, :trade_date, :open, :high, :low, :close, :pre_close, :change, :pct_chg, :vol, :amount)
                            """), {
                                'ts_code': ts_code,
                                'trade_date': trade_date,
                                'open': open_price,
                                'high': high,
                                'low': low,
                                'close': close,
                                'pre_close': pre_close,
                                'change': change,
                                'pct_chg': pct_chg,
                                'vol': vol,
                                'amount': amount
                            })
                            
                            current_price = close
                        
                        current_date += timedelta(days=1)
                
                conn.commit()
                
                # 验证生成的数据
                result = conn.execute(db.text("SELECT COUNT(*) FROM stock_daily_history"))
                total_records = result.fetchone()[0]
                
                result = conn.execute(db.text("SELECT MIN(trade_date), MAX(trade_date) FROM stock_daily_history"))
                date_range = result.fetchone()
                
                print(f"✅ 历史数据生成完成！")
                print(f"📊 总记录数: {total_records}")
                print(f"📅 日期范围: {date_range[0]} 到 {date_range[1]}")
                
                return True
                
        except Exception as e:
            print(f"❌ 生成历史数据失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def generate_basic_data():
    """生成基本面数据"""
    app = create_app()
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # 获取股票列表
                result = conn.execute(db.text("SELECT ts_code FROM stock_basic"))
                stocks = [row[0] for row in result.fetchall()]
                
                print(f"📊 为 {len(stocks)} 只股票生成基本面数据...")
                
                # 生成最近1年的基本面数据
                end_date = datetime.now()
                start_date = end_date - timedelta(days=365)
                
                current_date = start_date
                while current_date <= end_date:
                    if current_date.weekday() < 5:  # 工作日
                        trade_date = current_date.strftime('%Y-%m-%d')
                        
                        for ts_code in stocks:
                            # 生成基本面数据
                            pe = round(random.uniform(8, 50), 2)
                            pb = round(random.uniform(0.5, 8), 2)
                            ps = round(random.uniform(1, 15), 2)
                            total_mv = round(random.uniform(50, 5000) * 100000000, 2)  # 市值（元）
                            circ_mv = round(total_mv * random.uniform(0.3, 1.0), 2)  # 流通市值
                            turnover_rate = round(random.uniform(0.1, 15), 4)  # 换手率
                            
                            # 获取当日收盘价
                            price_result = conn.execute(db.text("""
                                SELECT close FROM stock_daily_history 
                                WHERE ts_code = :ts_code AND trade_date = :trade_date
                            """), {'ts_code': ts_code, 'trade_date': trade_date})
                            
                            price_row = price_result.fetchone()
                            close_price = price_row[0] if price_row else random.uniform(10, 50)
                            
                            # 插入基本面数据
                            conn.execute(db.text("""
                                INSERT OR REPLACE INTO stock_daily_basic 
                                (ts_code, trade_date, close, turnover_rate, pe, pb, ps, total_mv, circ_mv)
                                VALUES (:ts_code, :trade_date, :close, :turnover_rate, :pe, :pb, :ps, :total_mv, :circ_mv)
                            """), {
                                'ts_code': ts_code,
                                'trade_date': trade_date,
                                'close': close_price,
                                'turnover_rate': turnover_rate,
                                'pe': pe,
                                'pb': pb,
                                'ps': ps,
                                'total_mv': total_mv,
                                'circ_mv': circ_mv
                            })
                    
                    current_date += timedelta(days=1)
                
                conn.commit()
                
                # 验证数据
                result = conn.execute(db.text("SELECT COUNT(*) FROM stock_daily_basic"))
                basic_count = result.fetchone()[0]
                
                print(f"✅ 基本面数据生成完成！")
                print(f"📊 基本面记录数: {basic_count}")
                
                return True
                
        except Exception as e:
            print(f"❌ 生成基本面数据失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """主函数"""
    print("🚀 开始生成扩展历史数据...")
    
    # 生成历史价格数据
    if not generate_extended_historical_data():
        return False
    
    # 生成基本面数据
    if not generate_basic_data():
        return False
    
    print("🎉 所有数据生成完成！")
    print("💡 现在可以运行因子计算和模型训练了")
    
    return True

if __name__ == "__main__":
    main()
