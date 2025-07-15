#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取微信测试号用户列表
Get WeChat Test Account User List
"""

import requests
from wechat_config import WECHAT_APP_ID, WECHAT_APP_SECRET

def get_access_token():
    """获取访问令牌"""
    url = f"https://api.weixin.qq.com/cgi-bin/token"
    params = {
        'grant_type': 'client_credential',
        'appid': WECHAT_APP_ID,
        'secret': WECHAT_APP_SECRET
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'access_token' in data:
            print(f"✅ 获取access_token成功")
            return data['access_token']
        else:
            print(f"❌ 获取access_token失败: {data}")
            return None
            
    except Exception as e:
        print(f"❌ 获取access_token异常: {e}")
        return None

def get_user_list():
    """获取用户列表"""
    access_token = get_access_token()
    if not access_token:
        return None
        
    url = f"https://api.weixin.qq.com/cgi-bin/user/get?access_token={access_token}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        print("📋 用户列表信息:")
        print(f"原始响应: {data}")
        
        if data.get('errcode') == 0 or 'data' in data:
            if 'data' in data and 'openid' in data['data']:
                openids = data['data']['openid']
                print(f"✅ 找到 {len(openids)} 个用户:")
                for i, openid in enumerate(openids, 1):
                    print(f"  {i}. {openid}")
                return openids
            else:
                print("📝 暂无关注用户")
                return []
        else:
            print(f"❌ 获取用户列表失败: {data}")
            return None
            
    except Exception as e:
        print(f"❌ 获取用户列表异常: {e}")
        return None

if __name__ == "__main__":
    print("🔍 正在获取微信测试号用户列表...")
    users = get_user_list()
    
    if users:
        print(f"\n✅ 成功获取到 {len(users)} 个用户的OpenID")
        print("请将这些OpenID更新到 wechat_config.py 文件中")
    else:
        print("\n❌ 未能获取到用户列表")
        print("请确认：")
        print("1. 已经扫码关注了测试号")
        print("2. AppID和AppSecret配置正确")
