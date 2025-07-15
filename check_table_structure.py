#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据库表结构
"""

from app import create_app
from app.extensions import db

def check_table_structure():
    """检查表结构"""
    app = create_app()
    with app.app_context():
        try:
            with db.engine.connect() as conn:
                # 检查 stock_daily_history 表结构
                result = conn.execute(db.text("PRAGMA table_info(stock_daily_history)"))
                columns = result.fetchall()
                
                print("📊 stock_daily_history 表结构:")
                for col in columns:
                    print(f"  - {col[1]} ({col[2]})")
                
                # 检查 stock_basic 表结构
                result = conn.execute(db.text("PRAGMA table_info(stock_basic)"))
                columns = result.fetchall()
                
                print("\n📊 stock_basic 表结构:")
                for col in columns:
                    print(f"  - {col[1]} ({col[2]})")
                    
        except Exception as e:
            print(f"❌ 检查失败: {e}")

if __name__ == "__main__":
    check_table_structure()
