#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版微信消息推送
Simple WeChat Message Sender
"""

import requests
import json
import time
from datetime import datetime
from wechat_config import WECHAT_APP_ID, WECHAT_APP_SECRET, SUBSCRIBER_OPENIDS

class SimpleWeChatSender:
    def __init__(self):
        self.app_id = WECHAT_APP_ID
        self.app_secret = WECHAT_APP_SECRET
        self.access_token = None
        self.token_expires_at = 0
        
    def get_access_token(self):
        """获取访问令牌"""
        current_time = time.time()
        
        if self.access_token and current_time < self.token_expires_at:
            return self.access_token
            
        url = f"https://api.weixin.qq.com/cgi-bin/token"
        params = {
            'grant_type': 'client_credential',
            'appid': self.app_id,
            'secret': self.app_secret
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if 'access_token' in data:
                self.access_token = data['access_token']
                self.token_expires_at = current_time + data['expires_in'] - 300
                print(f"✅ 获取access_token成功")
                return self.access_token
            else:
                print(f"❌ 获取access_token失败: {data}")
                return None
                
        except Exception as e:
            print(f"❌ 获取access_token异常: {e}")
            return None
    
    def send_simple_message(self, message, openids=None):
        """发送简单消息（避免乱码）"""
        if openids is None:
            openids = SUBSCRIBER_OPENIDS
            
        access_token = self.get_access_token()
        if not access_token:
            return False
            
        url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
        
        # 确保消息是纯文本，没有特殊字符
        clean_message = str(message).encode('utf-8', errors='ignore').decode('utf-8')
        
        success_count = 0
        for openid in openids:
            data = {
                "touser": openid,
                "msgtype": "text",
                "text": {
                    "content": clean_message
                }
            }
            
            try:
                # 设置正确的编码
                headers = {
                    'Content-Type': 'application/json; charset=utf-8'
                }
                
                response = requests.post(url, json=data, headers=headers)
                result = response.json()
                
                if result.get('errcode') == 0:
                    print(f"✅ 消息发送成功")
                    success_count += 1
                else:
                    print(f"❌ 消息发送失败: {result}")
                    
            except Exception as e:
                print(f"❌ 发送消息异常: {e}")
                
        return success_count > 0
    
    def send_stock_report_simple(self, stock_data):
        """发送简化的股票报告"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # 使用最简单的格式
        message = f"股票分析报告\n时间: {current_time}\n\n"
        
        if isinstance(stock_data, list) and len(stock_data) > 0:
            message += "推荐股票:\n"
            for i, stock in enumerate(stock_data[:3], 1):  # 只显示前3只
                if isinstance(stock, dict):
                    name = stock.get('name', 'N/A')
                    symbol = stock.get('symbol', 'N/A')
                    score = stock.get('score', 0)
                    
                    message += f"{i}. {name}\n"
                    message += f"   代码: {symbol}\n"
                    message += f"   评分: {score:.1f}\n\n"
        else:
            message += "暂无推荐数据\n\n"
            
        message += "风险提示:\n投资有风险 请谨慎决策\n\n"
        message += "AI系统自动生成"
        
        return self.send_simple_message(message)

def test_simple_sender():
    """测试简化版发送器"""
    print("🧪 测试简化版微信发送器...")
    
    sender = SimpleWeChatSender()
    
    # 测试1：纯英文
    print("\n📋 测试1：纯英文消息")
    success1 = sender.send_simple_message("Test Message\nTime: 2025-07-15 15:20\nStatus: Testing simple sender")
    
    # 测试2：简单中文
    print("\n📋 测试2：简单中文消息")
    success2 = sender.send_simple_message("测试消息\n时间: 2025-07-15 15:20\n状态: 测试简化发送器")
    
    # 测试3：股票报告
    print("\n📋 测试3：简化股票报告")
    test_stocks = [
        {'name': '平安银行', 'symbol': '000001.SZ', 'score': 85.2},
        {'name': '万科A', 'symbol': '000002.SZ', 'score': 78.9},
        {'name': '招商银行', 'symbol': '600036.SH', 'score': 76.5}
    ]
    success3 = sender.send_stock_report_simple(test_stocks)
    
    if success1 and success2 and success3:
        print("\n✅ 所有测试消息发送成功！")
        print("📱 请检查您的微信是否收到了3条测试消息")
        return True
    else:
        print("\n❌ 部分测试消息发送失败")
        return False

if __name__ == "__main__":
    test_simple_sender()
