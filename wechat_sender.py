#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号消息推送模块
WeChat Official Account Message Sender
"""

import requests
import json
import time
import re
from datetime import datetime
from wechat_config import WECHAT_APP_ID, WECHAT_APP_SECRET, SUBSCRIBER_OPENIDS

class WeChatSender:
    def __init__(self):
        self.app_id = WECHAT_APP_ID
        self.app_secret = WECHAT_APP_SECRET
        self.access_token = None
        self.token_expires_at = 0
        
    def get_access_token(self):
        """获取访问令牌"""
        current_time = time.time()
        
        # 如果token还没过期，直接返回
        if self.access_token and current_time < self.token_expires_at:
            return self.access_token
            
        # 获取新的access_token
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
                # token有效期7200秒，提前5分钟过期
                self.token_expires_at = current_time + data['expires_in'] - 300
                print(f"✅ 获取access_token成功: {self.access_token[:20]}...")
                return self.access_token
            else:
                print(f"❌ 获取access_token失败: {data}")
                return None
                
        except Exception as e:
            print(f"❌ 获取access_token异常: {e}")
            return None
    
    def send_text_message(self, message, openids=None):
        """发送文本消息"""
        if openids is None:
            openids = SUBSCRIBER_OPENIDS

        access_token = self.get_access_token()
        if not access_token:
            return False

        url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"

        # 替换可能导致乱码的字符
        safe_message = message
        # 替换表情符号
        emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F700-\U0001F77F"  # alchemical symbols
                               u"\U0001F780-\U0001F7FF"  # Geometric Shapes
                               u"\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
                               u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
                               u"\U0001FA00-\U0001FA6F"  # Chess Symbols
                               u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
                               u"\U00002702-\U000027B0"  # Dingbats
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
        safe_message = emoji_pattern.sub(r'', safe_message)

        # 替换特殊符号
        safe_message = safe_message.replace('📊', '[图表]')
        safe_message = safe_message.replace('🕐', '[时间]')
        safe_message = safe_message.replace('🔥', '[热门]')
        safe_message = safe_message.replace('📈', '[上涨]')
        safe_message = safe_message.replace('💡', '[提示]')
        safe_message = safe_message.replace('⚠️', '[警告]')
        safe_message = safe_message.replace('🤖', '[机器人]')

        success_count = 0
        for openid in openids:
            data = {
                "touser": openid,
                "msgtype": "text",
                "text": {
                    "content": safe_message
                }
            }

            try:
                response = requests.post(url, json=data)
                result = response.json()

                if result.get('errcode') == 0:
                    print(f"✅ 消息发送成功到: {openid[:10]}...")
                    success_count += 1
                else:
                    print(f"❌ 消息发送失败到: {openid[:10]}..., 错误: {result}")

            except Exception as e:
                print(f"❌ 发送消息异常: {e}")

        return success_count > 0
    
    def send_stock_report(self, stock_data):
        """发送股票分析报告"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        message = f"""股票分析日报
时间: {current_time}

今日推荐股票:
"""
        
        if isinstance(stock_data, list) and len(stock_data) > 0:
            for i, stock in enumerate(stock_data[:5], 1):  # 最多显示5只股票
                if isinstance(stock, dict):
                    symbol = stock.get('symbol', 'N/A')
                    name = stock.get('name', 'N/A')
                    score = stock.get('score', 0)
                    reason = stock.get('reason', '基于AI模型分析')
                    
                    message += f"""
{i}. {name} ({symbol})
   评分: {score:.2f}
   理由: {reason}
"""
                else:
                    message += f"\n{i}. {stock}"
        else:
            message += "\n暂无推荐股票数据"
            
        message += f"""

风险提示:
投资有风险，入市需谨慎。
本分析仅供参考，不构成投资建议。

由AI量化分析系统自动生成
"""
        
        return self.send_text_message(message)

def test_wechat_sender():
    """测试微信发送功能"""
    print("🧪 开始测试微信消息发送...")
    
    sender = WeChatSender()
    
    # 测试发送简单消息
    test_message = f"""微信推送测试成功

测试时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

股票分析系统已连接微信公众号
每日股票推荐将自动推送到您的微信

系统功能:
- 股票数据分析
- AI模型预测
- 自动推送报告
- 微信消息通知

接下来您将收到每日股票分析报告"""
    
    success = sender.send_text_message(test_message)
    
    if success:
        print("✅ 微信测试消息发送成功！")
        return True
    else:
        print("❌ 微信测试消息发送失败！")
        return False

if __name__ == "__main__":
    test_wechat_sender()
