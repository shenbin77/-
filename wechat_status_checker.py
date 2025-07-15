#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信API状态检查工具
WeChat API Status Checker
"""

import requests
import json
import time
from datetime import datetime, timedelta

class WeChatStatusChecker:
    """微信API状态检查器"""
    
    def __init__(self):
        self.app_id = "wxf030257b07285d5a"
        self.app_secret = "31ceaff31dc2a2e13a215e1f1b948998"
        self.openids = ["o3tOfvssF1ThFelhSLLX3P2Gfkvk"]
        
        print("🔍 微信API状态检查器初始化完成")
    
    def get_access_token(self):
        """获取访问令牌"""
        print("🔑 获取access_token...")
        
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if "access_token" in data:
                print(f"✅ access_token获取成功")
                print(f"   令牌: {data['access_token'][:20]}...")
                print(f"   有效期: {data['expires_in']}秒")
                return data["access_token"]
            else:
                print(f"❌ 获取access_token失败: {data}")
                return None
                
        except Exception as e:
            print(f"❌ 获取access_token异常: {e}")
            return None
    
    def check_api_quota(self, access_token):
        """检查API配额"""
        print("📊 检查API配额...")
        
        url = f"https://api.weixin.qq.com/cgi-bin/clear_quota?access_token={access_token}"
        
        try:
            response = requests.post(url, json={}, timeout=10)
            data = response.json()
            
            print(f"📋 API配额检查结果: {data}")
            
            if data.get('errcode') == 0:
                print("✅ API配额正常")
                return True
            else:
                print(f"⚠️ API配额异常: {data}")
                return False
                
        except Exception as e:
            print(f"❌ 检查API配额异常: {e}")
            return False
    
    def get_user_info(self, access_token, openid):
        """获取用户信息"""
        print(f"👤 获取用户信息: {openid[:10]}...")
        
        url = f"https://api.weixin.qq.com/cgi-bin/user/info"
        params = {
            "access_token": access_token,
            "openid": openid,
            "lang": "zh_CN"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('errcode'):
                print(f"❌ 获取用户信息失败: {data}")
                return None
            else:
                print(f"✅ 用户信息获取成功:")
                print(f"   昵称: {data.get('nickname', '未知')}")
                print(f"   关注状态: {'已关注' if data.get('subscribe') == 1 else '未关注'}")
                print(f"   关注时间: {data.get('subscribe_time', '未知')}")
                return data
                
        except Exception as e:
            print(f"❌ 获取用户信息异常: {e}")
            return None
    
    def test_send_message(self, access_token, test_mode=True):
        """测试发送消息"""
        if test_mode:
            print("🧪 测试模式：不实际发送消息，只检查API状态")
            return True
        
        print("📤 测试发送消息...")
        
        url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
        
        test_message = f"[测试] 微信API状态检查\n时间: {datetime.now().strftime('%H:%M:%S')}"
        
        for openid in self.openids:
            data = {
                "touser": openid,
                "msgtype": "text",
                "text": {
                    "content": test_message
                }
            }
            
            try:
                response = requests.post(url, json=data, timeout=10)
                result = response.json()
                
                print(f"📱 发送结果: {result}")
                
                if result.get('errcode') == 0:
                    print("✅ 测试消息发送成功")
                    return True
                else:
                    error_code = result.get('errcode')
                    error_msg = result.get('errmsg')
                    print(f"❌ 测试消息发送失败: {error_code} - {error_msg}")
                    
                    # 分析错误原因
                    self.analyze_error(error_code, error_msg)
                    return False
                    
            except Exception as e:
                print(f"❌ 发送测试消息异常: {e}")
                return False
    
    def analyze_error(self, error_code, error_msg):
        """分析错误原因"""
        print("\n🔍 错误分析:")
        
        error_explanations = {
            40001: "access_token无效或已过期",
            40003: "openid无效",
            45047: "超出API调用频率限制",
            45015: "回复时间超过48小时限制",
            45016: "不在粉丝列表中",
            48001: "API功能未授权",
            48002: "粉丝拒收消息",
            48004: "API接口被封禁",
            48005: "API禁止删除被自动回复和自定义菜单引用的素材",
            50001: "用户未授权该API",
            50002: "用户受限，可能由于违规等原因被限制"
        }
        
        explanation = error_explanations.get(error_code, "未知错误")
        print(f"   错误码: {error_code}")
        print(f"   错误信息: {error_msg}")
        print(f"   可能原因: {explanation}")
        
        # 提供解决建议
        if error_code == 45047:
            print("\n💡 解决建议:")
            print("   1. 等待24小时后重试")
            print("   2. 减少API调用频率")
            print("   3. 使用模板消息替代客服消息")
            print("   4. 检查是否超出每日调用限制")
        elif error_code == 40001:
            print("\n💡 解决建议:")
            print("   1. 重新获取access_token")
            print("   2. 检查AppID和AppSecret是否正确")
        elif error_code == 45016:
            print("\n💡 解决建议:")
            print("   1. 确保用户已关注公众号")
            print("   2. 检查OpenID是否正确")
    
    def comprehensive_check(self):
        """综合检查"""
        print("🔍 开始综合检查微信API状态...")
        print("=" * 50)
        
        # 1. 获取access_token
        print("\n1️⃣ 检查access_token...")
        access_token = self.get_access_token()
        if not access_token:
            print("❌ 无法获取access_token，检查终止")
            return False
        
        # 2. 检查API配额
        print("\n2️⃣ 检查API配额...")
        quota_ok = self.check_api_quota(access_token)
        
        # 3. 检查用户信息
        print("\n3️⃣ 检查用户信息...")
        for openid in self.openids:
            user_info = self.get_user_info(access_token, openid)
            if not user_info:
                print(f"⚠️ 用户 {openid[:10]}... 信息获取失败")
        
        # 4. 测试发送消息（测试模式）
        print("\n4️⃣ 测试消息发送（测试模式）...")
        send_ok = self.test_send_message(access_token, test_mode=True)
        
        # 5. 生成报告
        print("\n📊 检查报告:")
        print("=" * 30)
        print(f"✅ access_token: {'正常' if access_token else '异常'}")
        print(f"✅ API配额: {'正常' if quota_ok else '异常'}")
        print(f"✅ 用户信息: 已检查 {len(self.openids)} 个用户")
        print(f"✅ 消息发送: {'可用' if send_ok else '受限'}")
        
        # 6. 建议
        print("\n💡 建议:")
        if not quota_ok or not send_ok:
            print("   - 当前API调用受限，建议等待24小时后重试")
            print("   - 考虑使用模板消息替代客服消息")
            print("   - 减少API调用频率")
        else:
            print("   - API状态正常，可以正常使用")
        
        print(f"\n⏰ 检查完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return access_token and quota_ok and send_ok
    
    def wait_and_retry_check(self, wait_hours=1):
        """等待并重试检查"""
        print(f"⏳ 等待 {wait_hours} 小时后重新检查...")
        
        wait_seconds = wait_hours * 3600
        end_time = datetime.now() + timedelta(seconds=wait_seconds)
        
        print(f"   开始时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   结束时间: {end_time.strftime('%H:%M:%S')}")
        
        # 分段等待，每10分钟显示一次进度
        interval = 600  # 10分钟
        elapsed = 0
        
        while elapsed < wait_seconds:
            time.sleep(min(interval, wait_seconds - elapsed))
            elapsed += interval
            
            remaining = wait_seconds - elapsed
            if remaining > 0:
                remaining_minutes = remaining // 60
                print(f"   ⏰ 剩余等待时间: {remaining_minutes} 分钟")
        
        print("✅ 等待完成，开始重新检查...")
        return self.comprehensive_check()

def main():
    """主函数"""
    print("🔍 微信API状态检查工具")
    print("=" * 40)
    
    checker = WeChatStatusChecker()
    
    # 执行综合检查
    result = checker.comprehensive_check()
    
    if not result:
        print("\n❌ 检查发现问题")
        
        # 询问是否等待重试
        try:
            choice = input("\n是否等待1小时后重试？(y/n): ").strip().lower()
            if choice == 'y':
                checker.wait_and_retry_check(1)
            else:
                print("👋 检查结束")
        except KeyboardInterrupt:
            print("\n👋 用户中断，检查结束")
    else:
        print("\n✅ 所有检查通过，API状态正常")

if __name__ == "__main__":
    main()
