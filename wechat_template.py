#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信模板消息推送
WeChat Template Message Sender
"""

import requests
import json
from datetime import datetime
from wechat_config import WECHAT_APP_ID, WECHAT_APP_SECRET, SUBSCRIBER_OPENIDS

class WeChatTemplate:
    def __init__(self):
        self.app_id = WECHAT_APP_ID
        self.app_secret = WECHAT_APP_SECRET
        
    def get_access_token(self):
        """获取访问令牌"""
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
                return data['access_token']
            else:
                print(f"❌ 获取access_token失败: {data}")
                return None
                
        except Exception as e:
            print(f"❌ 获取access_token异常: {e}")
            return None
    
    def create_template(self):
        """创建消息模板"""
        access_token = self.get_access_token()
        if not access_token:
            return None
            
        url = f"https://api.weixin.qq.com/cgi-bin/template/api_add_template?access_token={access_token}"
        
        # 股票分析报告模板
        template_data = {
            "template_id_short": "TM00015"  # 这是一个通用的模板ID
        }
        
        try:
            response = requests.post(url, json=template_data)
            result = response.json()
            print(f"创建模板结果: {result}")
            return result
            
        except Exception as e:
            print(f"❌ 创建模板异常: {e}")
            return None

def check_interaction_status():
    """检查用户互动状态"""
    print("🔍 检查微信互动状态...")
    print("""
📱 微信公众号消息推送规则：

1. ✅ 用户关注公众号后，可以立即推送消息
2. ⚠️  如果用户超过48小时没有与公众号互动，就不能主动推送消息
3. 🔄 用户发送任意消息给公众号后，重新激活48小时推送窗口

💡 解决方案：
请您打开微信，给测试号发送一条消息（任意内容都可以），
然后我们就可以正常推送股票分析报告了！

📝 建议发送内容：
- "你好"
- "测试"  
- "开始推送"
- 任意文字都可以

发送完消息后，请告诉我，我立即重新测试推送功能！
""")

if __name__ == "__main__":
    check_interaction_status()
    
    # 可选：尝试创建模板
    template = WeChatTemplate()
    template.create_template()
