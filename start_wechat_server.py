#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信股票分析服务器启动脚本
WeChat Stock Analysis Server Startup Script
"""

import subprocess
import sys
import time
import os
import threading
from datetime import datetime

def check_dependencies():
    """检查依赖包"""
    print("🔍 检查依赖包...")
    
    required_packages = ['flask', 'requests', 'pandas', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - 已安装")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 正在安装缺失的包: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ 依赖包安装完成")
        except subprocess.CalledProcessError:
            print("❌ 依赖包安装失败，请手动安装")
            return False
    
    return True

def test_wechat_config():
    """测试微信配置"""
    print("\n🧪 测试微信配置...")
    
    try:
        from wechat_sender import WeChatSender
        sender = WeChatSender()
        
        # 测试获取access_token
        token = sender.get_access_token()
        if token:
            print("✅ 微信配置正常，access_token获取成功")
            return True
        else:
            print("❌ 微信配置有问题，无法获取access_token")
            return False
            
    except Exception as e:
        print(f"❌ 微信配置测试失败: {e}")
        return False

def start_flask_server():
    """启动Flask服务器"""
    print("\n🚀 启动Flask微信接口服务器...")
    
    try:
        # 导入并启动服务器
        from wechat_server import app
        
        print("📱 服务器配置信息:")
        print("   - 地址: http://localhost:5000")
        print("   - 接口: http://localhost:5000/wechat")
        print("   - Token: StockAnalysisBot2024")
        print("   - 测试: http://localhost:5000/test")
        
        print("\n💡 下一步操作:")
        print("   1. 使用ngrok等工具获取公网URL")
        print("   2. 在微信测试号后台配置接口URL")
        print("   3. 开始与微信机器人对话")
        
        print(f"\n🕐 服务器启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        # 启动Flask应用
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except Exception as e:
        print(f"❌ Flask服务器启动失败: {e}")
        return False

def show_ngrok_instructions():
    """显示ngrok使用说明"""
    print("\n🌐 内网穿透配置说明:")
    print("=" * 50)
    print("为了让微信服务器访问您的接口，需要使用内网穿透工具：")
    print()
    print("📥 方案1：ngrok（推荐）")
    print("   1. 访问 https://ngrok.com/ 下载")
    print("   2. 注册账号并获取authtoken")
    print("   3. 运行: ngrok http 5000")
    print("   4. 复制显示的https URL")
    print()
    print("📥 方案2：花生壳")
    print("   1. 下载花生壳客户端")
    print("   2. 注册账号并配置内网穿透")
    print("   3. 映射本地5000端口")
    print()
    print("⚙️ 微信配置:")
    print("   - URL: https://your-url.ngrok.io/wechat")
    print("   - Token: StockAnalysisBot2024")
    print("=" * 50)

def run_daily_test():
    """运行每日推送测试"""
    print("\n🧪 运行每日推送测试...")
    
    try:
        from daily_stock_report import DailyStockReport
        reporter = DailyStockReport()
        
        # 运行测试
        success = reporter.test_report()
        
        if success:
            print("✅ 每日推送测试成功")
        else:
            print("❌ 每日推送测试失败")
            
        return success
        
    except Exception as e:
        print(f"❌ 每日推送测试异常: {e}")
        return False

def main():
    """主函数"""
    print("🤖 微信股票分析服务器启动程序")
    print("=" * 50)
    
    # 1. 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败，程序退出")
        return
    
    # 2. 测试微信配置
    if not test_wechat_config():
        print("❌ 微信配置测试失败，请检查配置")
        print("💡 请确认 wechat_config.py 中的配置正确")
        return
    
    # 3. 运行每日推送测试
    run_daily_test()
    
    # 4. 显示ngrok说明
    show_ngrok_instructions()
    
    # 5. 询问是否启动服务器
    print("\n❓ 是否现在启动Flask服务器？")
    print("   输入 'y' 启动服务器")
    print("   输入 'n' 退出程序")
    print("   输入 't' 仅运行测试")
    
    choice = input("\n请选择 (y/n/t): ").lower().strip()
    
    if choice == 'y':
        print("\n🚀 启动服务器...")
        start_flask_server()
    elif choice == 't':
        print("\n🧪 运行完整测试...")
        run_daily_test()
        print("✅ 测试完成")
    else:
        print("\n👋 程序退出")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()
