#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub自动同步系统
Auto GitHub Sync System
"""

import os
import time
import subprocess
import threading
from datetime import datetime
from pathlib import Path
import hashlib

class AutoGitSync:
    def __init__(self, repo_path=None, sync_interval=300):  # 5分钟检查一次
        self.repo_path = repo_path or os.getcwd()
        self.sync_interval = sync_interval
        self.last_sync_time = 0
        self.is_running = False
        self.sync_thread = None
        
        # 忽略的文件和目录
        self.ignore_patterns = {
            '__pycache__',
            '.git',
            '.vscode',
            'node_modules',
            '*.log',
            '*.tmp',
            '*.pyc',
            '.DS_Store',
            'Thumbs.db'
        }
        
        # 监控的文件扩展名
        self.watch_extensions = {'.py', '.md', '.yml', '.yaml', '.json', '.txt', '.html', '.css', '.js'}
        
    def should_ignore_file(self, file_path):
        """检查是否应该忽略文件"""
        file_path = Path(file_path)
        
        # 检查文件名模式
        for pattern in self.ignore_patterns:
            if pattern.startswith('*'):
                if file_path.name.endswith(pattern[1:]):
                    return True
            elif pattern in str(file_path):
                return True
                
        return False
    
    def get_repo_status(self):
        """获取仓库状态"""
        try:
            # 检查是否有未提交的更改
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                print(f"❌ Git状态检查失败: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"❌ 获取Git状态异常: {e}")
            return None
    
    def generate_commit_message(self, changed_files):
        """生成智能的提交消息"""
        if not changed_files:
            return "🔄 自动同步更新"
            
        # 分析变化类型
        added_files = [f for f in changed_files if f.startswith('A ')]
        modified_files = [f for f in changed_files if f.startswith('M ')]
        deleted_files = [f for f in changed_files if f.startswith('D ')]
        
        message_parts = []
        
        if added_files:
            message_parts.append(f"➕ 新增{len(added_files)}个文件")
        if modified_files:
            message_parts.append(f"📝 修改{len(modified_files)}个文件")
        if deleted_files:
            message_parts.append(f"🗑️ 删除{len(deleted_files)}个文件")
            
        if message_parts:
            message = "🔄 " + "，".join(message_parts)
        else:
            message = "🔄 自动同步更新"
            
        # 添加时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        message += f" ({timestamp})"
        
        return message
    
    def sync_to_github(self):
        """同步到GitHub"""
        try:
            print(f"🔍 检查仓库状态... ({datetime.now().strftime('%H:%M:%S')})")
            
            # 获取状态
            status = self.get_repo_status()
            if status is None:
                return False
                
            if not status:
                print("✅ 没有需要同步的更改")
                return True
                
            print(f"📝 发现更改:\n{status}")
            
            # 过滤需要忽略的文件
            lines = status.split('\n')
            filtered_lines = []
            
            for line in lines:
                if len(line) >= 3:
                    file_path = line[3:]  # 去掉状态前缀
                    if not self.should_ignore_file(file_path):
                        filtered_lines.append(line)
            
            if not filtered_lines:
                print("✅ 所有更改都被忽略，无需同步")
                return True
                
            print(f"📋 需要同步的文件: {len(filtered_lines)}个")
            
            # 添加文件
            print("📤 添加文件到Git...")
            add_result = subprocess.run(
                ['git', 'add', '.'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if add_result.returncode != 0:
                print(f"❌ Git add失败: {add_result.stderr}")
                return False
                
            # 生成提交消息
            commit_message = self.generate_commit_message(filtered_lines)
            print(f"💬 提交消息: {commit_message}")
            
            # 提交
            print("📝 提交更改...")
            commit_result = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if commit_result.returncode != 0:
                print(f"❌ Git commit失败: {commit_result.stderr}")
                return False
                
            # 推送
            print("🚀 推送到GitHub...")
            push_result = subprocess.run(
                ['git', 'push', 'origin', 'main'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if push_result.returncode != 0:
                print(f"❌ Git push失败: {push_result.stderr}")
                # 尝试推送到master分支
                print("🔄 尝试推送到master分支...")
                push_result = subprocess.run(
                    ['git', 'push', 'origin', 'master'],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if push_result.returncode != 0:
                    print(f"❌ 推送到master也失败: {push_result.stderr}")
                    return False
                    
            print("✅ 成功同步到GitHub!")
            self.last_sync_time = time.time()
            return True
            
        except Exception as e:
            print(f"❌ 同步过程异常: {e}")
            return False
    
    def sync_loop(self):
        """同步循环"""
        print(f"🔄 开始自动同步循环，检查间隔: {self.sync_interval}秒")
        
        while self.is_running:
            try:
                self.sync_to_github()
                
                # 等待下次检查
                for _ in range(self.sync_interval):
                    if not self.is_running:
                        break
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print("\n👋 用户中断，停止自动同步")
                break
            except Exception as e:
                print(f"❌ 同步循环异常: {e}")
                time.sleep(30)  # 出错后等待30秒再重试
    
    def start(self):
        """启动自动同步"""
        if self.is_running:
            print("⚠️ 自动同步已在运行中")
            return
            
        print("🚀 启动GitHub自动同步系统...")
        print(f"📁 监控目录: {self.repo_path}")
        print(f"⏰ 检查间隔: {self.sync_interval}秒")
        
        self.is_running = True
        self.sync_thread = threading.Thread(target=self.sync_loop, daemon=True)
        self.sync_thread.start()
        
        print("✅ 自动同步已启动!")
        
    def stop(self):
        """停止自动同步"""
        if not self.is_running:
            print("⚠️ 自动同步未在运行")
            return
            
        print("🛑 停止自动同步...")
        self.is_running = False
        
        if self.sync_thread:
            self.sync_thread.join(timeout=10)
            
        print("✅ 自动同步已停止")
    
    def manual_sync(self):
        """手动同步一次"""
        print("🔄 执行手动同步...")
        success = self.sync_to_github()
        if success:
            print("✅ 手动同步完成")
        else:
            print("❌ 手动同步失败")
        return success

def main():
    """主函数"""
    print("🤖 GitHub自动同步系统")
    print("=" * 50)
    
    # 创建同步器
    syncer = AutoGitSync(sync_interval=300)  # 5分钟检查一次
    
    try:
        # 先执行一次手动同步
        print("🧪 执行初始同步...")
        syncer.manual_sync()
        
        # 启动自动同步
        syncer.start()
        
        print("\n💡 自动同步已启动！")
        print("📋 功能说明:")
        print("   - 每5分钟自动检查代码变化")
        print("   - 发现变化后自动提交并推送到GitHub")
        print("   - 智能生成提交消息")
        print("   - 自动忽略临时文件和缓存")
        print("\n⌨️ 控制命令:")
        print("   - 按 Enter 手动同步一次")
        print("   - 输入 'stop' 停止自动同步")
        print("   - 输入 'quit' 退出程序")
        
        # 交互控制
        while syncer.is_running:
            try:
                command = input("\n请输入命令 (Enter=手动同步, stop=停止, quit=退出): ").strip().lower()
                
                if command == '':
                    syncer.manual_sync()
                elif command == 'stop':
                    syncer.stop()
                elif command == 'quit':
                    break
                else:
                    print("❓ 未知命令，请重新输入")
                    
            except KeyboardInterrupt:
                break
                
    except Exception as e:
        print(f"❌ 程序异常: {e}")
    finally:
        syncer.stop()
        print("👋 程序退出")

if __name__ == "__main__":
    main()
