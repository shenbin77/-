#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试数据库查询
"""

from app import create_app
from app.extensions import db
from app.models.stock_basic import StockBasic

def test_database_query():
    """测试数据库查询"""
    app = create_app()
    with app.app_context():
        try:
            # 直接SQL查询
            print("🔍 直接SQL查询:")
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SELECT * FROM stock_basic LIMIT 5"))
                rows = result.fetchall()
                print(f"  找到 {len(rows)} 条记录")
                for row in rows:
                    print(f"  - {row}")
            
            # 使用SQLAlchemy模型查询
            print("\n🔍 SQLAlchemy模型查询:")
            stocks = StockBasic.query.limit(5).all()
            print(f"  找到 {len(stocks)} 条记录")
            for stock in stocks:
                print(f"  - {stock.ts_code}: {stock.name}")
                
            # 测试总数
            total = StockBasic.query.count()
            print(f"\n📊 总股票数量: {total}")
            
        except Exception as e:
            print(f"❌ 查询失败: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_database_query()
