#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试阿里百炼API问题
Debug DashScope API Issues
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def debug_api_key():
    """调试API密钥问题"""
    print("🔍 调试阿里百炼API密钥问题")
    print("=" * 40)
    
    # 获取当前配置的密钥
    current_key = os.getenv('DASHSCOPE_API_KEY')
    print(f"当前配置的密钥: {current_key}")
    
    # 检查密钥格式
    if current_key:
        print(f"密钥长度: {len(current_key)}")
        print(f"是否以sk-开头: {current_key.startswith('sk-')}")
        print(f"密钥前15位: {current_key[:15]}")
        
        # 检查是否有特殊字符
        import re
        if re.search(r'[^\w-]', current_key):
            print("⚠️ 密钥包含特殊字符，可能有问题")
        else:
            print("✅ 密钥格式看起来正常")
    
    # 尝试使用原始密钥
    print("\n🧪 尝试使用原始密钥测试...")
    original_key = "sk-61f17f4d75fc45429a44977814eb8cf7"
    
    try:
        import dashscope
        from dashscope import Generation
        
        dashscope.api_key = original_key
        
        response = Generation.call(
            model='qwen-turbo',
            prompt='测试',
            max_tokens=10
        )
        
        if response.status_code == 200:
            print("✅ 原始密钥测试成功")
            print("💡 建议使用原始密钥")
            return original_key
        else:
            print(f"❌ 原始密钥也失败: {response}")
    except Exception as e:
        print(f"❌ 测试异常: {e}")
    
    # 尝试使用新密钥（清理特殊字符）
    print("\n🧪 尝试清理新密钥...")
    if current_key:
        # 移除可能的特殊字符
        cleaned_key = current_key.replace('Ж', '').replace('х', 'x')
        print(f"清理后的密钥: {cleaned_key}")
        
        try:
            dashscope.api_key = cleaned_key
            
            response = Generation.call(
                model='qwen-turbo',
                prompt='测试',
                max_tokens=10
            )
            
            if response.status_code == 200:
                print("✅ 清理后的密钥测试成功")
                return cleaned_key
            else:
                print(f"❌ 清理后的密钥也失败: {response}")
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    return None

def suggest_solution():
    """建议解决方案"""
    print("\n💡 解决方案建议:")
    print("=" * 30)
    
    print("1. 检查API密钥是否正确复制")
    print("   - 确保没有多余的空格或特殊字符")
    print("   - 确保完整复制了整个密钥")
    
    print("\n2. 重新获取API密钥")
    print("   - 访问: https://dashscope.aliyun.com/")
    print("   - 登录阿里云账号")
    print("   - 进入API密钥管理")
    print("   - 重新生成密钥")
    
    print("\n3. 检查账户状态")
    print("   - 确认已开通百炼服务")
    print("   - 检查账户余额")
    print("   - 确认API调用权限")
    
    print("\n4. 使用原始密钥作为备用")
    print("   - 原始密钥: sk-61f17f4d75fc45429a44977814eb8cf7")
    print("   - 如果原始密钥仍然有效，可以继续使用")

def main():
    """主函数"""
    print("🔧 阿里百炼API调试工具")
    print("=" * 50)
    
    # 调试API密钥
    working_key = debug_api_key()
    
    # 建议解决方案
    suggest_solution()
    
    # 总结
    print("\n📊 调试总结:")
    print("=" * 20)
    
    if working_key:
        print(f"✅ 找到可用的密钥: {working_key[:15]}...")
        print("💡 建议更新.env文件中的密钥配置")
    else:
        print("❌ 未找到可用的密钥")
        print("💡 建议重新获取API密钥")
    
    print(f"\n🎯 下一步行动:")
    if working_key:
        print("1. 更新.env文件中的DASHSCOPE_API_KEY")
        print("2. 重新运行complete_api_test.py")
        print("3. 开始使用TradingAgents功能")
    else:
        print("1. 访问 https://dashscope.aliyun.com/")
        print("2. 重新获取有效的API密钥")
        print("3. 更新配置并重新测试")

if __name__ == "__main__":
    main()
