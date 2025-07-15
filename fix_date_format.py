#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复数据库中的日期格式
"""

from app import create_app
from app.extensions import db
from datetime import datetime

def fix_date_format():
    """修复日期格式"""
    app = create_app()
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # 获取所有记录
                result = conn.execute(db.text("SELECT ts_code, list_date FROM stock_basic"))
                rows = result.fetchall()
                
                print(f"🔍 找到 {len(rows)} 条记录需要修复")
                
                # 修复每条记录的日期格式
                for row in rows:
                    ts_code = row[0]
                    list_date_int = row[1]
                    
                    # 将整数日期转换为日期对象
                    if isinstance(list_date_int, int):
                        date_str = str(list_date_int)
                        if len(date_str) == 8:  # YYYYMMDD格式
                            year = int(date_str[:4])
                            month = int(date_str[4:6])
                            day = int(date_str[6:8])
                            date_obj = datetime(year, month, day).date()
                            
                            # 更新数据库
                            conn.execute(db.text("""
                                UPDATE stock_basic 
                                SET list_date = :list_date 
                                WHERE ts_code = :ts_code
                            """), {
                                'list_date': date_obj,
                                'ts_code': ts_code
                            })
                            
                            print(f"  ✅ {ts_code}: {date_str} -> {date_obj}")
                
                conn.commit()
                print("🎉 日期格式修复完成！")
                
        except Exception as e:
            print(f"❌ 修复失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    fix_date_format()
