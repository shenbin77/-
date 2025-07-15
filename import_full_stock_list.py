#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全量股票数据导入脚本
Full Stock List Import Script
"""

import os
import sys
import time
import random
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import text
import requests
import json

# 设置环境变量
os.environ['TUSHARE_TOKEN'] = 'your_tushare_token_here'
os.environ['FLASK_SECRET_KEY'] = 'test-secret-key'

try:
    from app import create_app
    from app.extensions import db
except ImportError as e:
    print(f"❌ 导入模块失败: {e}")
    sys.exit(1)

# 股票数据源选择
DATA_SOURCE = 'manual'  # 可选: 'akshare', 'baostock', 'manual'

# 股票列表 - 用于手动导入模式
MANUAL_STOCK_LIST = [
    # 上证50成分股 (部分)
    {'ts_code': '600000.SH', 'symbol': '600000', 'name': '浦发银行', 'area': '上海', 'industry': '银行', 'list_date': '1999-11-10'},
    {'ts_code': '600016.SH', 'symbol': '600016', 'name': '民生银行', 'area': '北京', 'industry': '银行', 'list_date': '2000-12-19'},
    {'ts_code': '600019.SH', 'symbol': '600019', 'name': '宝钢股份', 'area': '上海', 'industry': '钢铁', 'list_date': '2000-12-12'},
    {'ts_code': '600028.SH', 'symbol': '600028', 'name': '中国石化', 'area': '北京', 'industry': '石油加工', 'list_date': '2001-08-08'},
    {'ts_code': '600030.SH', 'symbol': '600030', 'name': '中信证券', 'area': '北京', 'industry': '证券', 'list_date': '2003-01-06'},
    {'ts_code': '600036.SH', 'symbol': '600036', 'name': '招商银行', 'area': '深圳', 'industry': '银行', 'list_date': '2002-04-09'},
    {'ts_code': '600048.SH', 'symbol': '600048', 'name': '保利发展', 'area': '广州', 'industry': '房地产', 'list_date': '2006-07-31'},
    {'ts_code': '600050.SH', 'symbol': '600050', 'name': '中国联通', 'area': '北京', 'industry': '通信', 'list_date': '2002-10-09'},
    {'ts_code': '600104.SH', 'symbol': '600104', 'name': '上汽集团', 'area': '上海', 'industry': '汽车整车', 'list_date': '1997-11-07'},
    
    # 深证成指成分股 (部分)
    {'ts_code': '000001.SZ', 'symbol': '000001', 'name': '平安银行', 'area': '深圳', 'industry': '银行', 'list_date': '1991-04-03'},
    {'ts_code': '000002.SZ', 'symbol': '000002', 'name': '万科A', 'area': '深圳', 'industry': '房地产', 'list_date': '1991-01-29'},
    {'ts_code': '000063.SZ', 'symbol': '000063', 'name': '中兴通讯', 'area': '深圳', 'industry': '通信设备', 'list_date': '1997-11-18'},
    {'ts_code': '000066.SZ', 'symbol': '000066', 'name': '中国长城', 'area': '深圳', 'industry': '计算机设备', 'list_date': '1997-06-10'},
    {'ts_code': '000069.SZ', 'symbol': '000069', 'name': '华侨城A', 'area': '深圳', 'industry': '旅游景点', 'list_date': '1997-09-10'},
    {'ts_code': '000100.SZ', 'symbol': '000100', 'name': 'TCL科技', 'area': '广东', 'industry': '电子', 'list_date': '1999-01-07'},
    {'ts_code': '000333.SZ', 'symbol': '000333', 'name': '美的集团', 'area': '广东', 'industry': '家用电器', 'list_date': '2013-09-18'},
    {'ts_code': '000651.SZ', 'symbol': '000651', 'name': '格力电器', 'area': '广东', 'industry': '家用电器', 'list_date': '1996-11-18'},
    {'ts_code': '000725.SZ', 'symbol': '000725', 'name': '京东方A', 'area': '北京', 'industry': '光学光电子', 'list_date': '1997-05-29'},
    {'ts_code': '000858.SZ', 'symbol': '000858', 'name': '五粮液', 'area': '四川', 'industry': '白酒', 'list_date': '1998-04-27'},
    
    # 创业板成分股 (部分)
    {'ts_code': '300059.SZ', 'symbol': '300059', 'name': '东方财富', 'area': '上海', 'industry': '互联网', 'list_date': '2010-03-19'},
    {'ts_code': '300122.SZ', 'symbol': '300122', 'name': '智飞生物', 'area': '重庆', 'industry': '生物制品', 'list_date': '2010-11-12'},
    {'ts_code': '300274.SZ', 'symbol': '300274', 'name': '阳光电源', 'area': '安徽', 'industry': '电气设备', 'list_date': '2011-11-02'},
    {'ts_code': '300315.SZ', 'symbol': '300315', 'name': '掌趣科技', 'area': '北京', 'industry': '互联网', 'list_date': '2012-05-09'},
    {'ts_code': '300316.SZ', 'symbol': '300316', 'name': '晶盛机电', 'area': '浙江', 'industry': '专用设备', 'list_date': '2012-05-11'},
    {'ts_code': '300433.SZ', 'symbol': '300433', 'name': '蓝思科技', 'area': '湖南', 'industry': '电子', 'list_date': '2015-03-18'},
    {'ts_code': '300498.SZ', 'symbol': '300498', 'name': '温氏股份', 'area': '广东', 'industry': '农业', 'list_date': '2015-11-02'},
    {'ts_code': '300750.SZ', 'symbol': '300750', 'name': '宁德时代', 'area': '福建', 'industry': '电池', 'list_date': '2018-06-11'},
    {'ts_code': '300759.SZ', 'symbol': '300759', 'name': '康龙化成', 'area': '北京', 'industry': '医药', 'list_date': '2019-01-28'},
    {'ts_code': '300760.SZ', 'symbol': '300760', 'name': '迈瑞医疗', 'area': '深圳', 'industry': '医疗器械', 'list_date': '2018-10-16'},
    
    # 科创板成分股 (部分)
    {'ts_code': '688005.SH', 'symbol': '688005', 'name': '容百科技', 'area': '浙江', 'industry': '电池', 'list_date': '2019-07-22'},
    {'ts_code': '688008.SH', 'symbol': '688008', 'name': '澜起科技', 'area': '上海', 'industry': '半导体', 'list_date': '2019-07-22'},
    {'ts_code': '688012.SH', 'symbol': '688012', 'name': '中微公司', 'area': '上海', 'industry': '半导体', 'list_date': '2019-07-22'},
    {'ts_code': '688036.SH', 'symbol': '688036', 'name': '传音控股', 'area': '深圳', 'industry': '通信设备', 'list_date': '2019-09-30'},
    {'ts_code': '688111.SH', 'symbol': '688111', 'name': '金山办公', 'area': '北京', 'industry': '软件', 'list_date': '2019-11-18'},
    {'ts_code': '688126.SH', 'symbol': '688126', 'name': '沪硅产业', 'area': '上海', 'industry': '半导体', 'list_date': '2020-04-20'},
    {'ts_code': '688169.SH', 'symbol': '688169', 'name': '石头科技', 'area': '北京', 'industry': '家用电器', 'list_date': '2020-02-21'},
    {'ts_code': '688363.SH', 'symbol': '688363', 'name': '华熙生物', 'area': '山东', 'industry': '医药', 'list_date': '2019-11-06'},
    {'ts_code': '688981.SH', 'symbol': '688981', 'name': '中芯国际', 'area': '上海', 'industry': '半导体', 'list_date': '2020-07-16'},
    
    # 其他知名股票
    {'ts_code': '600519.SH', 'symbol': '600519', 'name': '贵州茅台', 'area': '贵州', 'industry': '白酒', 'list_date': '2001-08-27'},
    {'ts_code': '601318.SH', 'symbol': '601318', 'name': '中国平安', 'area': '深圳', 'industry': '保险', 'list_date': '2007-03-01'},
    {'ts_code': '601398.SH', 'symbol': '601398', 'name': '工商银行', 'area': '北京', 'industry': '银行', 'list_date': '2006-10-27'},
    {'ts_code': '601857.SH', 'symbol': '601857', 'name': '中国石油', 'area': '北京', 'industry': '石油', 'list_date': '2007-11-05'},
    {'ts_code': '601988.SH', 'symbol': '601988', 'name': '中国银行', 'area': '北京', 'industry': '银行', 'list_date': '2006-07-05'},
    {'ts_code': '002594.SZ', 'symbol': '002594', 'name': '比亚迪', 'area': '广东', 'industry': '汽车', 'list_date': '2011-06-30'},
    {'ts_code': '002415.SZ', 'symbol': '002415', 'name': '海康威视', 'area': '浙江', 'industry': '安防设备', 'list_date': '2010-05-28'},
    {'ts_code': '600276.SH', 'symbol': '600276', 'name': '恒瑞医药', 'area': '江苏', 'industry': '医药', 'list_date': '2000-10-16'},
    {'ts_code': '600887.SH', 'symbol': '600887', 'name': '伊利股份', 'area': '内蒙古', 'industry': '乳品', 'list_date': '1996-03-12'},
    {'ts_code': '000876.SZ', 'symbol': '000876', 'name': '新希望', 'area': '四川', 'industry': '饲料', 'list_date': '1998-06-23'},
]

def get_stock_list_from_akshare():
    """从AKShare获取股票列表"""
    print("📊 正在从AKShare获取股票列表...")
    
    try:
        # 尝试导入akshare
        import akshare as ak
        
        # 获取A股上市公司基本信息
        stock_info_a_code_name_df = ak.stock_info_a_code_name()
        print(f"✅ 成功获取 {len(stock_info_a_code_name_df)} 只股票的基本信息")
        
        # 获取行业信息
        stock_sector_df = ak.stock_sector_detail(sector="行业")
        print(f"✅ 成功获取 {len(stock_sector_df)} 只股票的行业信息")
        
        # 合并数据
        stock_info_df = pd.merge(
            stock_info_a_code_name_df, 
            stock_sector_df[['代码', '板块名称']], 
            left_on='code', 
            right_on='代码', 
            how='left'
        )
        
        # 转换为需要的格式
        stocks = []
        for _, row in stock_info_df.iterrows():
            # 处理代码格式 (添加.SH或.SZ后缀)
            code = row['code']
            if code.startswith('6'):
                ts_code = f"{code}.SH"
            else:
                ts_code = f"{code}.SZ"
                
            stocks.append({
                'ts_code': ts_code,
                'symbol': code,
                'name': row['name'],
                'area': '中国',  # AKShare没有地区信息
                'industry': row.get('板块名称', '未知'),
                'list_date': '2000-01-01'  # AKShare没有上市日期信息
            })
        
        print(f"✅ 成功处理 {len(stocks)} 只股票数据")
        return stocks
        
    except ImportError:
        print("❌ 未安装AKShare，请使用pip install akshare安装")
        return []
    except Exception as e:
        print(f"❌ 获取股票列表失败: {e}")
        return []

def get_stock_list_from_baostock():
    """从BaoStock获取股票列表"""
    print("📊 正在从BaoStock获取股票列表...")
    
    try:
        # 尝试导入baostock
        import baostock as bs
        
        # 登录系统
        lg = bs.login()
        if lg.error_code != '0':
            print(f"❌ BaoStock登录失败: {lg.error_msg}")
            return []
            
        # 获取证券基本资料
        rs = bs.query_stock_basic()
        if rs.error_code != '0':
            print(f"❌ 获取股票列表失败: {rs.error_msg}")
            bs.logout()
            return []
            
        # 处理数据
        data_list = []
        while (rs.next()):
            data_list.append(rs.get_row_data())
        
        # 登出系统
        bs.logout()
        
        # 转换为DataFrame
        stock_df = pd.DataFrame(data_list, columns=rs.fields)
        print(f"✅ 成功获取 {len(stock_df)} 只股票的基本信息")
        
        # 转换为需要的格式
        stocks = []
        for _, row in stock_df.iterrows():
            # 处理代码格式
            code = row['code']
            if code.startswith('sh.'):
                ts_code = f"{code[3:]}.SH"
            elif code.startswith('sz.'):
                ts_code = f"{code[3:]}.SZ"
            else:
                continue
                
            stocks.append({
                'ts_code': ts_code,
                'symbol': code[3:],
                'name': row['code_name'],
                'area': '中国',  # BaoStock没有地区信息
                'industry': row.get('industry', '未知'),
                'list_date': row.get('ipoDate', '2000-01-01')
            })
        
        print(f"✅ 成功处理 {len(stocks)} 只股票数据")
        return stocks
        
    except ImportError:
        print("❌ 未安装BaoStock，请使用pip install baostock安装")
        return []
    except Exception as e:
        print(f"❌ 获取股票列表失败: {e}")
        return []

def import_stocks_to_db(stocks):
    """将股票数据导入数据库"""
    print(f"📥 正在导入 {len(stocks)} 只股票数据到数据库...")
    
    app = create_app()
    with app.app_context():
        try:
            # 检查表是否存在
            with db.engine.connect() as conn:
                # 获取现有股票数量
                result = conn.execute(text("SELECT COUNT(*) FROM stock_basic"))
                existing_count = result.fetchone()[0]
                print(f"📊 数据库中已有 {existing_count} 只股票")
                
                # 导入股票数据
                imported_count = 0
                for stock in stocks:
                    try:
                        # 检查股票是否已存在
                        result = conn.execute(
                            text("SELECT COUNT(*) FROM stock_basic WHERE ts_code = :ts_code"),
                            {"ts_code": stock['ts_code']}
                        )
                        exists = result.fetchone()[0] > 0
                        
                        if not exists:
                            # 插入新股票
                            conn.execute(text("""
                                INSERT INTO stock_basic (ts_code, symbol, name, area, industry, list_date)
                                VALUES (:ts_code, :symbol, :name, :area, :industry, :list_date)
                            """), stock)
                            conn.commit()
                            imported_count += 1
                            
                            if imported_count % 50 == 0:
                                print(f"✅ 已导入 {imported_count} 只股票")
                    except Exception as e:
                        print(f"❌ 导入股票 {stock['ts_code']} 失败: {e}")
                
                print(f"✅ 成功导入 {imported_count} 只新股票")
                print(f"📊 数据库中现有 {existing_count + imported_count} 只股票")
                
                return imported_count
                
        except Exception as e:
            print(f"❌ 导入股票数据失败: {e}")
            return 0

def main():
    """主函数"""
    print("🚀 开始导入全量股票数据...")
    
    # 获取股票列表
    if DATA_SOURCE == 'akshare':
        stocks = get_stock_list_from_akshare()
    elif DATA_SOURCE == 'baostock':
        stocks = get_stock_list_from_baostock()
    else:
        stocks = MANUAL_STOCK_LIST
        print(f"📋 使用手动配置的 {len(stocks)} 只股票")
    
    if not stocks:
        print("❌ 未获取到股票数据，导入失败")
        return 1
    
    # 导入数据库
    imported_count = import_stocks_to_db(stocks)
    
    if imported_count > 0:
        print(f"🎉 成功导入 {imported_count} 只新股票！")
        return 0
    else:
        print("⚠️ 没有新股票被导入")
        return 1

if __name__ == "__main__":
    sys.exit(main())
