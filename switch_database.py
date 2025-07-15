#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库切换工具
支持在SQLite和MySQL之间切换
"""

import os
import sys
import argparse
from app import create_app
from app.extensions import db

def switch_to_sqlite():
    """切换到SQLite数据库"""
    print("🔄 切换到SQLite数据库...")
    
    # 修改config_simple.py
    config_file = 'config_simple.py'
    
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 注释MySQL配置，启用SQLite配置
    content = content.replace(
        "    SQLALCHEMY_DATABASE_URI = 'sqlite:///stock_analysis.db'",
        "    SQLALCHEMY_DATABASE_URI = 'sqlite:///stock_analysis.db'"
    )
    content = content.replace(
        "    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://",
        "    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://"
    )
    
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 已切换到SQLite数据库")
    print("📁 数据库文件: stock_analysis.db")

def switch_to_mysql(host='localhost', user='root', password='', database='stock_analysis'):
    """切换到MySQL数据库"""
    print("🔄 切换到MySQL数据库...")
    
    # 修改config_simple.py
    config_file = 'config_simple.py'
    
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 注释SQLite配置，启用MySQL配置
    mysql_uri = f"mysql+pymysql://{user}:{password}@{host}/{database}?charset=utf8mb4"
    
    content = content.replace(
        "    SQLALCHEMY_DATABASE_URI = 'sqlite:///stock_analysis.db'",
        "    # SQLALCHEMY_DATABASE_URI = 'sqlite:///stock_analysis.db'"
    )
    content = content.replace(
        "    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:your_password@localhost/stock_analysis?charset=utf8mb4'",
        f"    SQLALCHEMY_DATABASE_URI = '{mysql_uri}'"
    )
    
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 已切换到MySQL数据库")
    print(f"🔗 连接字符串: {mysql_uri}")

def create_mysql_database(host='localhost', user='root', password='', database='stock_analysis'):
    """创建MySQL数据库"""
    try:
        import pymysql
        
        print(f"🔨 创建MySQL数据库: {database}")
        
        # 连接到MySQL服务器
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 创建数据库
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ 数据库 {database} 创建成功")
        
        connection.close()
        return True
        
    except ImportError:
        print("❌ 请先安装pymysql: pip install pymysql")
        return False
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        return False

def init_database():
    """初始化数据库表"""
    print("🔨 初始化数据库表...")
    
    try:
        app = create_app()
        with app.app_context():
            db.create_all()
            print("✅ 数据库表创建成功")
            return True
    except Exception as e:
        print(f"❌ 初始化数据库失败: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='数据库切换工具')
    parser.add_argument('database', choices=['sqlite', 'mysql'], help='目标数据库类型')
    parser.add_argument('--host', default='localhost', help='MySQL主机地址')
    parser.add_argument('--user', default='root', help='MySQL用户名')
    parser.add_argument('--password', default='', help='MySQL密码')
    parser.add_argument('--database-name', default='stock_analysis', help='数据库名称')
    parser.add_argument('--create-db', action='store_true', help='创建MySQL数据库')
    parser.add_argument('--init-tables', action='store_true', help='初始化数据库表')
    
    args = parser.parse_args()
    
    if args.database == 'sqlite':
        switch_to_sqlite()
    elif args.database == 'mysql':
        if args.create_db:
            if not create_mysql_database(args.host, args.user, args.password, args.database_name):
                return
        
        switch_to_mysql(args.host, args.user, args.password, args.database_name)
    
    if args.init_tables:
        init_database()
    
    print("\n🎉 数据库切换完成！")
    print("💡 提示: 请重启应用以使配置生效")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("📊 数据库切换工具")
        print("\n使用方法:")
        print("  python switch_database.py sqlite                    # 切换到SQLite")
        print("  python switch_database.py mysql --password=123456   # 切换到MySQL")
        print("  python switch_database.py mysql --create-db --init-tables --password=123456  # 完整MySQL设置")
        print("\n当前配置:")
        
        try:
            from config_simple import Config
            print(f"  数据库URI: {Config.SQLALCHEMY_DATABASE_URI}")
        except:
            print("  无法读取当前配置")
    else:
        main()
