#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号机器人服务
WeChat Official Account Bot Service
"""

import os
import hashlib
import json
from flask import Flask, request, make_response
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from datetime import datetime

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 微信配置
WECHAT_TOKEN = "TradingAgents2025"  # 与微信后台配置的Token一致
WECHAT_APPID = "wxf030257b07285d5a"
WECHAT_APPSECRET = "31ceaff31dc2a2e13a215e1f1b948998"

def verify_signature(signature, timestamp, nonce):
    """验证微信签名"""
    token = WECHAT_TOKEN
    tmp_list = [token, timestamp, nonce]
    tmp_list.sort()
    tmp_str = ''.join(tmp_list)
    tmp_str = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
    return tmp_str == signature

def parse_xml(xml_str):
    """解析XML消息"""
    root = ET.fromstring(xml_str)
    msg = {}
    for child in root:
        msg[child.tag] = child.text
    return msg

def create_text_response(to_user, from_user, content):
    """创建文本回复消息"""
    response = f"""
    <xml>
        <ToUserName><![CDATA[{to_user}]]></ToUserName>
        <FromUserName><![CDATA[{from_user}]]></FromUserName>
        <CreateTime>{int(datetime.now().timestamp())}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{content}]]></Content>
    </xml>
    """
    return response.strip()

def analyze_stock_with_ai(stock_code):
    """使用AI分析股票"""
    try:
        import dashscope
        from dashscope import Generation
        
        # 配置API
        dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')
        
        # 构建分析Prompt
        prompt = f"""
请对股票代码 {stock_code} 进行简要技术分析。

要求：
1. 分析内容要简洁明了，适合微信消息
2. 包含趋势判断、风险评估、操作建议
3. 字数控制在200字以内
4. 语言要通俗易懂

请直接输出分析结果，不要包含其他格式。
"""
        
        response = Generation.call(
            model='qwen-turbo',
            prompt=prompt,
            max_tokens=300
        )
        
        if response.status_code == 200:
            return response.output.text
        else:
            return f"抱歉，{stock_code} 分析服务暂时不可用，请稍后再试。"
            
    except Exception as e:
        return f"分析 {stock_code} 时出现错误，请检查股票代码是否正确。"

def get_help_message():
    """获取帮助信息"""
    help_text = """
🤖 TradingAgents股票分析助手

📊 使用方法：
• 发送股票代码获取分析 (如：000001)
• 发送"帮助"查看使用说明
• 发送"功能"了解更多功能

💡 示例：
• 000001 - 分析平安银行
• 600036 - 分析招商银行
• AAPL - 分析苹果公司

⚠️ 风险提示：
投资有风险，分析仅供参考，请谨慎决策。

Powered by TradingAgents-CN 🚀
"""
    return help_text

def get_features_message():
    """获取功能介绍"""
    features_text = """
🚀 TradingAgents功能介绍

🤖 多智能体分析：
• 13个专业AI机器人协作
• 技术分析 + 基本面分析
• 风险评估 + 概率预测

📊 支持市场：
• A股市场 (000001, 600036等)
• 美股市场 (AAPL, TSLA等)
• 实时数据更新

🧠 AI技术：
• 阿里百炼大模型
• 中文优化分析
• 概率化风险评估

💰 成本优势：
• 每次分析约0.1-0.3元
• 比传统方案便宜80%+

发送股票代码开始体验！
"""
    return features_text

@app.route('/wechat', methods=['GET', 'POST'])
def wechat():
    """微信接口处理"""
    
    if request.method == 'GET':
        # 验证服务器配置
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')
        
        if verify_signature(signature, timestamp, nonce):
            return echostr
        else:
            return 'Invalid signature'
    
    elif request.method == 'POST':
        # 处理用户消息
        xml_str = request.get_data(as_text=True)
        msg = parse_xml(xml_str)
        
        to_user = msg.get('FromUserName')
        from_user = msg.get('ToUserName')
        msg_type = msg.get('MsgType')
        
        if msg_type == 'text':
            content = msg.get('Content', '').strip()
            
            # 处理不同类型的消息
            if content.lower() in ['帮助', 'help', '?', '？']:
                reply_content = get_help_message()
            
            elif content.lower() in ['功能', 'features', '介绍']:
                reply_content = get_features_message()
            
            elif content.lower() in ['你好', 'hello', 'hi']:
                reply_content = """
👋 欢迎使用TradingAgents股票分析助手！

我是您的专业AI投资顾问，可以为您提供：
• 实时股票技术分析
• 多智能体协作分析
• 概率化风险评估

发送股票代码开始分析，或发送"帮助"了解更多功能。
"""
            
            else:
                # 尝试作为股票代码处理
                stock_code = content.upper()
                
                # 简单验证股票代码格式
                if len(stock_code) >= 4 and (stock_code.isdigit() or stock_code.isalpha()):
                    reply_content = f"🔍 正在分析 {stock_code}，请稍候...\n\n"
                    analysis_result = analyze_stock_with_ai(stock_code)
                    reply_content += analysis_result
                else:
                    reply_content = """
❓ 未识别的指令

请发送：
• 股票代码 (如：000001, AAPL)
• "帮助" 查看使用说明
• "功能" 了解更多功能
"""
            
            # 创建回复消息
            response_xml = create_text_response(to_user, from_user, reply_content)
            response = make_response(response_xml)
            response.content_type = 'application/xml'
            return response
        
        else:
            # 处理其他类型消息
            reply_content = "抱歉，我目前只支持文本消息。请发送股票代码或"帮助"获取使用说明。"
            response_xml = create_text_response(to_user, from_user, reply_content)
            response = make_response(response_xml)
            response.content_type = 'application/xml'
            return response

@app.route('/health')
def health():
    """健康检查接口"""
    return {
        "status": "ok",
        "service": "TradingAgents WeChat Bot",
        "timestamp": datetime.now().isoformat()
    }

@app.route('/')
def index():
    """首页"""
    return """
    <h1>🤖 TradingAgents微信机器人</h1>
    <p>服务状态: 正常运行</p>
    <p>配置信息:</p>
    <ul>
        <li>微信Token: TradingAgents2025</li>
        <li>接口地址: /wechat</li>
        <li>健康检查: /health</li>
    </ul>
    <p>请在微信公众号后台配置此URL</p>
    """

if __name__ == '__main__':
    print("🚀 启动TradingAgents微信机器人服务...")
    print(f"📱 微信Token: {WECHAT_TOKEN}")
    print(f"🔗 接口地址: /wechat")
    print(f"💊 健康检查: /health")
    
    # 检查API配置
    if os.getenv('DASHSCOPE_API_KEY'):
        print("✅ 阿里百炼API已配置")
    else:
        print("⚠️ 阿里百炼API未配置")
    
    app.run(host='0.0.0.0', port=8000, debug=True)
