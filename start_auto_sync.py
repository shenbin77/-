#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub自动同步启动器
Auto GitHub Sync Launcher
"""

import os
import sys
import time
import subprocess
from datetime import datetime

def check_git_config():
    """检查Git配置"""
    print("🔍 检查Git配置...")
    
    try:
        # 检查是否在Git仓库中
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ 当前目录不是Git仓库")
            return False
            
        # 检查远程仓库
        result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
        if result.returncode != 0 or not result.stdout.strip():
            print("❌ 没有配置远程仓库")
            return False
            
        print("✅ Git配置正常")
        print(f"📍 远程仓库: {result.stdout.strip().split()[1]}")
        return True
        
    except Exception as e:
        print(f"❌ Git配置检查失败: {e}")
        return False

def test_github_connection():
    """测试GitHub连接"""
    print("🌐 测试GitHub连接...")
    
    try:
        # 尝试fetch来测试连接
        result = subprocess.run(
            ['git', 'fetch', '--dry-run'], 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ GitHub连接正常")
            return True
        else:
            print(f"❌ GitHub连接失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ GitHub连接超时")
        return False
    except Exception as e:
        print(f"❌ GitHub连接测试异常: {e}")
        return False

def show_current_status():
    """显示当前状态"""
    print("\n📊 当前仓库状态:")
    print("-" * 30)
    
    try:
        # 显示分支信息
        result = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"🌿 当前分支: {result.stdout.strip()}")
            
        # 显示最后一次提交
        result = subprocess.run(['git', 'log', '-1', '--oneline'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"📝 最后提交: {result.stdout.strip()}")
            
        # 显示未提交的更改
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if result.returncode == 0:
            changes = result.stdout.strip()
            if changes:
                change_count = len(changes.split('\n'))
                print(f"📋 未提交更改: {change_count}个文件")
            else:
                print("✅ 没有未提交的更改")
                
    except Exception as e:
        print(f"❌ 获取状态失败: {e}")

def create_windows_service():
    """创建Windows服务脚本"""
    service_script = f"""@echo off
cd /d "{os.getcwd()}"
python auto_sync.py
pause
"""
    
    with open("start_auto_sync.bat", "w", encoding="utf-8") as f:
        f.write(service_script)
        
    print("✅ 已创建 start_auto_sync.bat 启动脚本")

def main():
    """主函数"""
    print("🚀 GitHub自动同步系统启动器")
    print("=" * 50)
    print(f"📅 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 工作目录: {os.getcwd()}")
    
    # 检查Git配置
    if not check_git_config():
        print("\n❌ Git配置检查失败，请先配置Git仓库")
        print("💡 解决方案:")
        print("   1. 确保当前目录是Git仓库: git init")
        print("   2. 添加远程仓库: git remote add origin <your-repo-url>")
        print("   3. 配置用户信息: git config user.name 和 git config user.email")
        input("\n按Enter键退出...")
        return
    
    # 测试GitHub连接
    if not test_github_connection():
        print("\n⚠️ GitHub连接测试失败")
        print("💡 可能的原因:")
        print("   1. 网络连接问题")
        print("   2. GitHub访问权限问题")
        print("   3. 仓库URL配置错误")
        
        choice = input("\n是否继续启动自动同步？(y/n): ").lower()
        if choice != 'y':
            return
    
    # 显示当前状态
    show_current_status()
    
    # 创建Windows启动脚本
    create_windows_service()
    
    print("\n🎯 自动同步配置:")
    print("   ⏰ 检查间隔: 5分钟")
    print("   📝 自动提交: 是")
    print("   🚀 自动推送: 是")
    print("   🔄 智能消息: 是")
    
    print("\n💡 使用说明:")
    print("   1. 系统会每5分钟检查一次代码变化")
    print("   2. 发现变化后自动提交并推送到GitHub")
    print("   3. 会自动忽略临时文件和缓存文件")
    print("   4. 生成智能的提交消息")
    
    print("\n⚙️ 启动选项:")
    print("   1. 前台运行 - 可以看到实时日志")
    print("   2. 后台运行 - 最小化到系统托盘")
    print("   3. 仅测试 - 只执行一次同步测试")
    
    while True:
        choice = input("\n请选择启动方式 (1/2/3): ").strip()
        
        if choice == '1':
            print("\n🚀 启动前台自动同步...")
            from auto_sync import AutoGitSync
            syncer = AutoGitSync(sync_interval=300)
            
            try:
                syncer.manual_sync()  # 先执行一次
                syncer.start()
                
                print("\n✅ 自动同步已启动！")
                print("💡 按 Ctrl+C 停止自动同步")
                
                while syncer.is_running:
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print("\n🛑 用户中断")
                syncer.stop()
            break
            
        elif choice == '2':
            print("\n🚀 启动后台自动同步...")
            print("💡 请运行 start_auto_sync.bat 文件")
            print("💡 或者使用任务计划程序设置开机自启")
            break
            
        elif choice == '3':
            print("\n🧪 执行同步测试...")
            from auto_sync import AutoGitSync
            syncer = AutoGitSync()
            success = syncer.manual_sync()
            
            if success:
                print("✅ 同步测试成功！")
            else:
                print("❌ 同步测试失败！")
            break
            
        else:
            print("❓ 无效选择，请重新输入")
    
    print("\n👋 启动器退出")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        input("按Enter键退出...")
