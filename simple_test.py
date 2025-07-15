#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("🧪 测试Python环境...")

try:
    from flask import Flask
    print("✅ Flask 导入成功")
except ImportError as e:
    print(f"❌ Flask 导入失败: {e}")

try:
    from wechat_sender import WeChatSender
    print("✅ WeChatSender 导入成功")
    
    sender = WeChatSender()
    token = sender.get_access_token()
    if token:
        print("✅ 微信配置正常")
    else:
        print("❌ 微信配置有问题")
        
except Exception as e:
    print(f"❌ WeChatSender 测试失败: {e}")

print("🎉 测试完成！")
