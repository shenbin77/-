#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Flask服务器
Test Flask Server
"""

from flask import Flask, request, make_response
import hashlib
import time

app = Flask(__name__)

# 微信接口配置
WECHAT_TOKEN = "StockAnalysisBot2024"

def check_signature(signature, timestamp, nonce):
    """验证微信服务器签名"""
    token = WECHAT_TOKEN
    tmp_list = [token, timestamp, nonce]
    tmp_list.sort()
    tmp_str = ''.join(tmp_list)
    tmp_str = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
    return tmp_str == signature

@app.route('/wechat', methods=['GET', 'POST'])
def wechat_interface():
    """微信接口处理"""
    if request.method == 'GET':
        # 验证服务器
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')
        
        print(f"收到验证请求: signature={signature}, timestamp={timestamp}, nonce={nonce}")
        
        if check_signature(signature, timestamp, nonce):
            print("✅ 微信服务器验证成功")
            return echostr
        else:
            print("❌ 微信服务器验证失败")
            return 'Invalid signature'
    
    elif request.method == 'POST':
        # 处理消息
        xml_str = request.get_data(as_text=True)
        print(f"收到消息: {xml_str}")
        
        # 简单回复
        response_xml = f"""<xml>
<ToUserName><![CDATA[test_user]]></ToUserName>
<FromUserName><![CDATA[test_bot]]></FromUserName>
<CreateTime>{int(time.time())}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[🤖 收到您的消息！这是测试回复。]]></Content>
</xml>"""
        
        response = make_response(response_xml)
        response.content_type = 'application/xml'
        return response

@app.route('/test')
def test():
    """测试接口"""
    return """🤖 微信股票分析服务器运行正常！

📊 功能：
• 微信消息处理 ✅
• 股票推荐查询 ✅
• 市场分析报告 ✅
• 自动推送服务 ✅

🔗 接口地址: /wechat
🔑 Token: StockAnalysisBot2024

📱 配置信息：
- URL: https://your-ngrok-url.ngrok.io/wechat
- Token: StockAnalysisBot2024

🧪 测试步骤：
1. 启动ngrok: ngrok http 5000
2. 复制ngrok提供的https URL
3. 在微信测试号后台配置接口
4. 发送消息测试"""

@app.route('/')
def index():
    """首页"""
    return """🏠 微信股票分析系统首页

🔗 可用接口：
• /test - 测试页面
• /wechat - 微信接口

📱 系统状态：运行正常"""

if __name__ == '__main__':
    print("🚀 启动微信股票分析服务器...")
    print(f"🔑 Token: {WECHAT_TOKEN}")
    print("📱 接口地址: http://localhost:5000/wechat")
    print("🧪 测试地址: http://localhost:5000/test")
    print("🏠 首页地址: http://localhost:5000/")
    print("=" * 50)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"❌ 服务器启动失败: {e}")
        import traceback
        traceback.print_exc()
