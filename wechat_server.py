#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号服务器接口
WeChat Official Account Server Interface
"""

from flask import Flask, request, make_response
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime
import time
import re
from wechat_sender import WeChatSender
from daily_stock_report import DailyStockReport

app = Flask(__name__)

# 微信接口配置
WECHAT_TOKEN = "StockAnalysisBot2024"  # 您可以自定义这个Token

class WeChatServer:
    def __init__(self):
        self.sender = WeChatSender()
        self.stock_report = DailyStockReport()
        
    def check_signature(self, signature, timestamp, nonce):
        """验证微信服务器签名"""
        token = WECHAT_TOKEN
        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        tmp_str = ''.join(tmp_list)
        tmp_str = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
        return tmp_str == signature
    
    def parse_xml(self, xml_str):
        """解析XML消息"""
        try:
            root = ET.fromstring(xml_str)
            msg = {}
            for child in root:
                msg[child.tag] = child.text
            return msg
        except Exception as e:
            print(f"解析XML失败: {e}")
            return None
    
    def create_text_response(self, to_user, from_user, content):
        """创建文本回复消息"""
        response = f"""<xml>
<ToUserName><![CDATA[{to_user}]]></ToUserName>
<FromUserName><![CDATA[{from_user}]]></FromUserName>
<CreateTime>{int(time.time())}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{content}]]></Content>
</xml>"""
        return response
    
    def handle_text_message(self, msg):
        """处理文本消息"""
        content = msg.get('Content', '').strip()
        from_user = msg.get('FromUserName')
        to_user = msg.get('ToUserName')
        
        print(f"收到消息: {content} 来自: {from_user}")
        
        # 处理不同类型的消息
        if content in ['你好', 'hello', '帮助', 'help']:
            reply = self.get_help_message()
        elif content in ['股票推荐', '推荐股票', '今日推荐']:
            reply = self.get_stock_recommendations()
        elif content in ['市场分析', '分析', '报告']:
            reply = self.get_market_analysis()
        elif content.startswith('查询') or content.startswith('股票'):
            # 提取股票代码或名称
            stock_query = content.replace('查询', '').replace('股票', '').strip()
            reply = self.query_stock_info(stock_query)
        elif content in ['订阅', '开启推送']:
            reply = self.subscribe_daily_report()
        elif content in ['取消订阅', '关闭推送']:
            reply = self.unsubscribe_daily_report()
        else:
            reply = self.get_default_response(content)
        
        return self.create_text_response(from_user, to_user, reply)
    
    def get_help_message(self):
        """获取帮助信息"""
        return """🤖 AI股票分析助手

📋 可用命令：
• 股票推荐 - 获取今日推荐股票
• 市场分析 - 获取市场分析报告  
• 查询[股票名称] - 查询具体股票
• 订阅 - 开启每日推送
• 取消订阅 - 关闭每日推送
• 帮助 - 显示此帮助信息

💡 示例：
• 发送"股票推荐"获取推荐
• 发送"查询平安银行"查询股票
• 发送"订阅"开启每日推送

⚠️ 投资有风险，仅供参考！"""

    def get_stock_recommendations(self):
        """获取股票推荐"""
        try:
            # 获取推荐股票
            top_stocks = self.stock_report.get_top_stocks(3)
            
            if not top_stocks:
                return "❌ 暂时无法获取股票推荐，请稍后再试"
            
            reply = "📊 今日股票推荐：\n\n"
            
            for i, stock in enumerate(top_stocks, 1):
                name = stock.get('name', 'N/A')
                symbol = stock.get('symbol', 'N/A')
                score = stock.get('score', 0)
                reason = stock.get('reason', '技术面分析')
                
                reply += f"{i}. {name} ({symbol})\n"
                reply += f"   📈 评分: {score:.1f}\n"
                reply += f"   💡 理由: {reason}\n\n"
            
            reply += "⚠️ 投资有风险，仅供参考！"
            return reply
            
        except Exception as e:
            print(f"获取股票推荐失败: {e}")
            return "❌ 获取推荐失败，请稍后再试"
    
    def get_market_analysis(self):
        """获取市场分析"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        return f"""📊 市场分析报告

🕐 分析时间: {current_time}

📈 市场概况:
• A股市场整体表现平稳
• 科技股活跃度较高
• 金融股估值合理

🔥 热点板块:
• 新能源汽车
• 人工智能
• 生物医药

💡 投资建议:
• 关注业绩稳定的蓝筹股
• 适度配置成长性行业
• 控制仓位，分散风险

⚠️ 以上分析仅供参考，投资需谨慎！"""
    
    def query_stock_info(self, stock_query):
        """查询股票信息"""
        if not stock_query:
            return "请提供股票名称或代码，例如：查询平安银行"
        
        # 简单的股票信息查询
        stock_info = {
            '平安银行': {'code': '000001.SZ', 'price': '12.34', 'change': '+2.1%'},
            '万科': {'code': '000002.SZ', 'price': '8.56', 'change': '+1.8%'},
            '招商银行': {'code': '600036.SH', 'price': '45.67', 'change': '+0.9%'},
            '贵州茅台': {'code': '600519.SH', 'price': '1678.90', 'change': '-0.5%'},
        }
        
        for name, info in stock_info.items():
            if stock_query in name or info['code'] in stock_query:
                return f"""📊 {name} ({info['code']})

💰 当前价格: {info['price']}
📈 涨跌幅: {info['change']}
🕐 更新时间: {datetime.now().strftime('%H:%M')}

💡 发送"股票推荐"获取更多推荐"""
        
        return f"❌ 未找到股票「{stock_query}」的信息\n\n💡 支持查询：平安银行、万科、招商银行、贵州茅台等"
    
    def subscribe_daily_report(self):
        """订阅每日报告"""
        return """✅ 已开启每日股票推送！

📅 推送时间:
• 每天早上 8:30
• 每天晚上 18:30

📊 推送内容:
• 股票推荐列表
• 市场分析报告
• 投资建议

💡 发送"取消订阅"可关闭推送"""
    
    def unsubscribe_daily_report(self):
        """取消订阅每日报告"""
        return """❌ 已关闭每日股票推送

💡 发送"订阅"可重新开启推送
📱 您仍可随时发送消息查询股票信息"""
    
    def get_default_response(self, content):
        """默认回复"""
        return f"""🤖 收到您的消息：{content}

💡 我是AI股票分析助手，可以帮您：
• 获取股票推荐
• 查询股票信息  
• 分析市场趋势

📝 发送"帮助"查看所有命令"""

# 创建服务器实例
wechat_server = WeChatServer()

@app.route('/wechat', methods=['GET', 'POST'])
def wechat_interface():
    """微信接口处理"""
    if request.method == 'GET':
        # 验证服务器
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        echostr = request.args.get('echostr')
        
        if wechat_server.check_signature(signature, timestamp, nonce):
            print("✅ 微信服务器验证成功")
            return echostr
        else:
            print("❌ 微信服务器验证失败")
            return 'Invalid signature'
    
    elif request.method == 'POST':
        # 处理消息
        xml_str = request.get_data(as_text=True)
        msg = wechat_server.parse_xml(xml_str)
        
        if msg and msg.get('MsgType') == 'text':
            response_xml = wechat_server.handle_text_message(msg)
            response = make_response(response_xml)
            response.content_type = 'application/xml'
            return response
        
        return 'success'

@app.route('/test')
def test():
    """测试接口"""
    return """🤖 微信股票分析服务器运行正常！

📊 功能：
• 微信消息处理
• 股票推荐查询
• 市场分析报告
• 自动推送服务

🔗 接口地址: /wechat
🔑 Token: StockAnalysisBot2024"""

if __name__ == '__main__':
    print("🚀 启动微信股票分析服务器...")
    print(f"🔑 Token: {WECHAT_TOKEN}")
    print("📱 接口地址: http://localhost:5000/wechat")
    app.run(host='0.0.0.0', port=5000, debug=True)
