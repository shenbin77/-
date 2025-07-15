#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub认证修复工具
GitHub Authentication Fix Tool
"""

import subprocess
import getpass
import os

def check_current_remote():
    """检查当前远程仓库配置"""
    try:
        result = subprocess.run(['git', 'remote', '-v'], 
                              capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            print("📍 当前远程仓库配置:")
            print(result.stdout)
            return result.stdout
        else:
            print("❌ 无法获取远程仓库信息")
            return None
    except Exception as e:
        print(f"❌ 检查远程仓库失败: {e}")
        return None

def test_current_auth():
    """测试当前认证状态"""
    print("🧪 测试当前GitHub认证...")
    try:
        result = subprocess.run(['git', 'ls-remote', 'origin'], 
                              capture_output=True, text=True, 
                              encoding='utf-8', timeout=30)
        if result.returncode == 0:
            print("✅ 当前认证正常")
            return True
        else:
            print(f"❌ 认证失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ 连接超时")
        return False
    except Exception as e:
        print(f"❌ 测试认证异常: {e}")
        return False

def fix_with_token():
    """使用Token修复认证"""
    print("\n🔑 使用Personal Access Token修复认证")
    print("=" * 40)
    
    print("💡 如何获取GitHub Token:")
    print("   1. 登录GitHub → Settings → Developer settings")
    print("   2. Personal access tokens → Tokens (classic)")
    print("   3. Generate new token → 勾选 'repo' 权限")
    print("   4. 复制生成的Token")
    
    token = getpass.getpass("\n请输入您的GitHub Personal Access Token: ")
    
    if not token:
        print("❌ Token不能为空")
        return False
    
    try:
        # 更新远程URL
        new_url = f"https://{token}@github.com/shenbin77/-.git"
        print(f"🔄 更新远程URL...")
        
        subprocess.run(['git', 'remote', 'set-url', 'origin', new_url], 
                      check=True, encoding='utf-8')
        
        print("✅ 远程URL更新成功")
        
        # 测试新配置
        print("🧪 测试新的认证配置...")
        if test_current_auth():
            print("🎉 Token认证配置成功！")
            return True
        else:
            print("❌ Token认证测试失败")
            return False
            
    except Exception as e:
        print(f"❌ Token配置失败: {e}")
        return False

def fix_with_credentials():
    """使用用户名密码修复认证"""
    print("\n👤 使用用户名和密码修复认证")
    print("=" * 40)
    print("⚠️ 注意: GitHub已不支持密码认证，建议使用Token")
    
    username = input("GitHub用户名: ")
    password = getpass.getpass("GitHub密码或Token: ")
    
    if not username or not password:
        print("❌ 用户名和密码不能为空")
        return False
    
    try:
        new_url = f"https://{username}:{password}@github.com/shenbin77/-.git"
        subprocess.run(['git', 'remote', 'set-url', 'origin', new_url], 
                      check=True, encoding='utf-8')
        
        print("✅ 认证信息更新成功")
        
        if test_current_auth():
            print("🎉 用户名密码认证配置成功！")
            return True
        else:
            print("❌ 用户名密码认证测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 用户名密码配置失败: {e}")
        return False

def setup_ssh():
    """设置SSH认证"""
    print("\n🔐 设置SSH密钥认证")
    print("=" * 40)
    print("💡 SSH认证步骤:")
    print("   1. 生成SSH密钥: ssh-keygen -t ed25519 -C 'your.email@example.com'")
    print("   2. 添加到SSH代理: ssh-add ~/.ssh/id_ed25519")
    print("   3. 复制公钥: cat ~/.ssh/id_ed25519.pub")
    print("   4. 在GitHub Settings → SSH keys 中添加公钥")
    
    choice = input("\n是否已完成SSH密钥配置？(y/n): ").lower()
    
    if choice == 'y':
        try:
            # 更新为SSH URL
            ssh_url = "git@github.com:shenbin77/-.git"
            subprocess.run(['git', 'remote', 'set-url', 'origin', ssh_url], 
                          check=True, encoding='utf-8')
            
            print("✅ 远程URL更新为SSH")
            
            if test_current_auth():
                print("🎉 SSH认证配置成功！")
                return True
            else:
                print("❌ SSH认证测试失败")
                return False
                
        except Exception as e:
            print(f"❌ SSH配置失败: {e}")
            return False
    else:
        print("💡 请先完成SSH密钥配置，然后重新运行此工具")
        return False

def test_push():
    """测试推送功能"""
    print("\n🚀 测试推送功能...")
    
    try:
        # 检查是否有需要推送的提交
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if result.stdout.strip():
            print("📝 发现未提交的更改，先提交...")
            subprocess.run(['git', 'add', '.'], check=True)
            subprocess.run(['git', 'commit', '-m', '🔧 修复GitHub认证配置'], check=True)
        
        # 尝试推送
        print("🚀 尝试推送到GitHub...")
        result = subprocess.run(['git', 'push', 'origin', 'main'], 
                              capture_output=True, text=True, 
                              encoding='utf-8', timeout=60)
        
        if result.returncode == 0:
            print("✅ 推送成功！GitHub认证配置正确")
            return True
        else:
            print(f"❌ 推送失败: {result.stderr}")
            # 尝试推送到master分支
            print("🔄 尝试推送到master分支...")
            result = subprocess.run(['git', 'push', 'origin', 'master'], 
                                  capture_output=True, text=True, 
                                  encoding='utf-8', timeout=60)
            if result.returncode == 0:
                print("✅ 推送到master分支成功！")
                return True
            else:
                print(f"❌ 推送到master也失败: {result.stderr}")
                return False
                
    except subprocess.TimeoutExpired:
        print("❌ 推送超时")
        return False
    except Exception as e:
        print(f"❌ 推送测试异常: {e}")
        return False

def main():
    """主函数"""
    print("🔐 GitHub认证修复工具")
    print("=" * 50)
    
    # 检查当前状态
    check_current_remote()
    
    # 测试当前认证
    if test_current_auth():
        print("✅ 当前认证正常，无需修复")
        
        # 测试推送
        if test_push():
            print("🎉 GitHub认证完全正常！")
            return
        else:
            print("⚠️ 认证正常但推送失败，可能是权限问题")
    
    print("\n🛠️ 选择修复方式:")
    print("   1. 使用Personal Access Token（推荐）")
    print("   2. 使用用户名和密码/Token")
    print("   3. 设置SSH密钥认证")
    print("   4. 退出")
    
    while True:
        choice = input("\n请选择修复方式 (1-4): ").strip()
        
        if choice == '1':
            if fix_with_token():
                test_push()
            break
        elif choice == '2':
            if fix_with_credentials():
                test_push()
            break
        elif choice == '3':
            if setup_ssh():
                test_push()
            break
        elif choice == '4':
            print("👋 退出修复工具")
            break
        else:
            print("❓ 无效选择，请重新输入")
    
    print("\n💡 修复完成后，您可以:")
    print("   - 运行 'python simple_auto_sync.py' 启动自动同步")
    print("   - 运行 'git push' 手动推送代码")
    print("   - 修改代码后自动提交到本地仓库")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 用户中断，退出程序")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        input("按Enter键退出...")
