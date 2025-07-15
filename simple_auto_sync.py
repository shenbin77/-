#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版GitHub自动同步
Simple Auto GitHub Sync
"""

import os
import time
import subprocess
from datetime import datetime

def check_git_status():
    """检查Git状态"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception as e:
        print(f"❌ 检查Git状态失败: {e}")
        return None

def auto_commit_and_push():
    """自动提交和推送"""
    try:
        # 检查状态
        status = check_git_status()
        if not status:
            print("✅ 没有需要同步的更改")
            return True
            
        print(f"📝 发现更改:\n{status}")
        
        # 添加文件
        print("📤 添加文件...")
        subprocess.run(['git', 'add', '.'], check=True, encoding='utf-8', errors='ignore')
        
        # 提交
        commit_msg = f"🔄 自动同步更新 ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
        print(f"💬 提交: {commit_msg}")
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True, encoding='utf-8', errors='ignore')
        
        print("✅ 本地提交成功")
        print("💡 请手动执行 'git push' 来推送到GitHub")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git操作失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 同步异常: {e}")
        return False

def main():
    """主函数"""
    print("🔄 简化版自动同步系统")
    print("=" * 40)
    
    while True:
        print(f"\n🕐 {datetime.now().strftime('%H:%M:%S')} - 检查更改...")
        
        try:
            auto_commit_and_push()
            
            print("⏰ 等待5分钟后再次检查...")
            for i in range(300):  # 5分钟 = 300秒
                time.sleep(1)
                if i % 60 == 0:  # 每分钟显示一次
                    remaining = (300 - i) // 60
                    print(f"⏳ 还有 {remaining} 分钟...")
                    
        except KeyboardInterrupt:
            print("\n👋 用户中断，退出程序")
            break
        except Exception as e:
            print(f"❌ 程序异常: {e}")
            time.sleep(30)  # 出错后等待30秒

if __name__ == "__main__":
    main()
