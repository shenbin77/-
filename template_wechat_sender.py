#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于模板消息的微信推送系统
Template Message Based WeChat Sender
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

class TemplateWeChatSender:
    """基于模板消息的微信推送器"""
    
    def __init__(self):
        # 微信配置
        self.app_id = "wxf030257b07285d5a"
        self.app_secret = "31ceaff31dc2a2e13a215e1f1b948998"
        self.openids = ["o3tOfvssF1ThFelhSLLX3P2Gfkvk"]
        
        # 访问令牌
        self.access_token = None
        self.token_expires_at = 0
        
        # 模板ID（需要在微信公众平台配置）
        self.template_ids = {
            "stock_report": "",  # 股票报告模板ID
            "market_alert": "",  # 市场提醒模板ID
            "test_message": ""   # 测试消息模板ID
        }
        
        print("📱 基于模板消息的微信推送系统初始化完成")
        print(f"👥 配置用户数: {len(self.openids)}")
    
    def get_access_token(self) -> Optional[str]:
        """获取访问令牌"""
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
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
                self.access_token = data["access_token"]
                self.token_expires_at = time.time() + data["expires_in"] - 300
                print("✅ access_token获取成功")
                return self.access_token
            else:
                print(f"❌ 获取access_token失败: {data}")
                return None
                
        except Exception as e:
            print(f"❌ 获取access_token异常: {e}")
            return None
    
    def send_template_message(self, openid: str, template_id: str, data: Dict[str, Any], url: str = None) -> bool:
        """发送模板消息"""
        access_token = self.get_access_token()
        if not access_token:
            return False
        
        api_url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
        
        payload = {
            "touser": openid,
            "template_id": template_id,
            "data": data
        }
        
        if url:
            payload["url"] = url
        
        try:
            response = requests.post(api_url, json=payload, timeout=10)
            result = response.json()
            
            if result.get("errcode") == 0:
                print(f"✅ 模板消息发送成功: {openid[:10]}...")
                return True
            else:
                print(f"❌ 模板消息发送失败: {result}")
                return False
                
        except Exception as e:
            print(f"❌ 发送模板消息异常: {e}")
            return False
    
    def send_stock_report_template(self, stocks: List[Dict[str, Any]]) -> bool:
        """发送股票报告模板消息"""
        print("📊 发送股票报告模板消息...")
        
        # 如果没有配置模板ID，使用客服消息作为备用
        if not self.template_ids["stock_report"]:
            print("⚠️ 未配置股票报告模板ID，使用客服消息备用方案")
            return self.send_stock_report_text(stocks)
        
        # 准备模板数据
        template_data = self._prepare_stock_template_data(stocks)
        
        success_count = 0
        for openid in self.openids:
            if self.send_template_message(openid, self.template_ids["stock_report"], template_data):
                success_count += 1
        
        return success_count > 0
    
    def send_stock_report_text(self, stocks: List[Dict[str, Any]]) -> bool:
        """发送股票报告文本消息（备用方案）"""
        print("📝 使用文本消息发送股票报告...")
        
        # 生成报告内容
        report = self._generate_stock_report_text(stocks)
        
        # 使用客服消息发送
        return self.send_custom_message(report)
    
    def send_custom_message(self, message: str) -> bool:
        """发送客服消息"""
        access_token = self.get_access_token()
        if not access_token:
            return False
        
        url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
        
        # 清理消息内容
        safe_message = self._clean_message(message)
        
        success_count = 0
        for openid in self.openids:
            data = {
                "touser": openid,
                "msgtype": "text",
                "text": {
                    "content": safe_message
                }
            }
            
            try:
                response = requests.post(url, json=data, timeout=10)
                result = response.json()
                
                if result.get('errcode') == 0:
                    print(f"✅ 客服消息发送成功: {openid[:10]}...")
                    success_count += 1
                else:
                    error_code = result.get('errcode')
                    error_msg = result.get('errmsg')
                    print(f"❌ 客服消息发送失败: {error_code} - {error_msg}")
                    
                    # 如果是频率限制，直接返回失败
                    if error_code == 45047:
                        print("⚠️ 检测到API频率限制，建议稍后重试")
                        return False
                
            except Exception as e:
                print(f"❌ 发送客服消息异常: {e}")
        
        return success_count > 0
    
    def _prepare_stock_template_data(self, stocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """准备股票模板数据"""
        # 这里需要根据实际的模板格式来准备数据
        # 示例模板数据格式
        top_stock = stocks[0] if stocks else {}
        
        return {
            "first": {
                "value": "今日股票分析报告",
                "color": "#173177"
            },
            "keyword1": {
                "value": top_stock.get('name', '暂无推荐'),
                "color": "#173177"
            },
            "keyword2": {
                "value": f"{top_stock.get('score', 0):.1f}分",
                "color": "#173177"
            },
            "keyword3": {
                "value": top_stock.get('reason', '技术分析'),
                "color": "#173177"
            },
            "remark": {
                "value": f"共推荐{len(stocks)}只股票，投资有风险，决策需谨慎",
                "color": "#173177"
            }
        }
    
    def _generate_stock_report_text(self, stocks: List[Dict[str, Any]]) -> str:
        """生成股票报告文本"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        report = f"""[机器人] AI股票分析报告
[时间] {current_time}

[图表] 今日推荐股票 (共{len(stocks)}只):

"""
        
        for i, stock in enumerate(stocks, 1):
            name = stock.get('name', '未知')
            symbol = stock.get('symbol', '')
            score = stock.get('score', 0)
            reason = stock.get('reason', '无')
            
            report += f"{i}. {name} ({symbol})\n"
            report += f"   评分: {score:.1f}\n"
            report += f"   理由: {reason}\n\n"
        
        report += """[提示] 投资有风险，决策需谨慎
[机器人] 本报告仅供参考，不构成投资建议

---
AI股票分析助手"""
        
        return report
    
    def _clean_message(self, message: str) -> str:
        """清理消息内容"""
        # 替换emoji和特殊字符
        replacements = {
            '📊': '[图表]', '🕐': '[时间]', '🔥': '[热门]', '📈': '[上涨]',
            '💡': '[提示]', '⚠️': '[警告]', '🤖': '[机器人]', '✅': '[成功]',
            '❌': '[失败]', '📱': '[手机]', '🎯': '[目标]', '🚀': '[火箭]',
            '💰': '[金钱]', '📉': '[下跌]', '🔍': '[搜索]', '⭐': '[星星]'
        }
        
        safe_message = message
        for emoji, replacement in replacements.items():
            safe_message = safe_message.replace(emoji, replacement)
        
        # 限制消息长度
        if len(safe_message) > 2000:
            safe_message = safe_message[:1900] + "...\n[消息过长，已截断]"
        
        return safe_message
    
    def send_test_message(self) -> bool:
        """发送测试消息"""
        print("🧪 发送测试消息...")
        
        test_message = f"""[机器人] 微信推送测试
[时间] {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

[成功] 如果您收到这条消息，说明微信推送功能正常！

[提示] 系统功能:
- 每日股票分析报告
- 实时市场提醒
- 个股查询服务

[机器人] AI股票分析助手"""
        
        return self.send_custom_message(test_message)
    
    def check_template_status(self) -> Dict[str, Any]:
        """检查模板状态"""
        access_token = self.get_access_token()
        if not access_token:
            return {"error": "无法获取access_token"}
        
        # 获取模板列表
        url = f"https://api.weixin.qq.com/cgi-bin/template/get_all_private_template?access_token={access_token}"
        
        try:
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get('errcode') == 0:
                templates = data.get('template_list', [])
                print(f"📋 找到 {len(templates)} 个模板:")
                
                for template in templates:
                    print(f"  - {template.get('title', '未知标题')}")
                    print(f"    ID: {template.get('template_id', '未知ID')}")
                    print(f"    内容: {template.get('content', '未知内容')[:50]}...")
                    print()
                
                return {"templates": templates, "count": len(templates)}
            else:
                print(f"❌ 获取模板列表失败: {data}")
                return {"error": data}
                
        except Exception as e:
            print(f"❌ 检查模板状态异常: {e}")
            return {"error": str(e)}

def main():
    """主函数"""
    print("📱 基于模板消息的微信推送系统测试")
    print("=" * 50)
    
    sender = TemplateWeChatSender()
    
    # 检查模板状态
    print("\n📋 检查模板状态...")
    template_status = sender.check_template_status()
    
    # 发送测试消息
    print("\n🧪 发送测试消息...")
    test_success = sender.send_test_message()
    
    if test_success:
        print("✅ 测试消息发送成功！")
        
        # 发送股票报告
        print("\n📊 发送股票报告...")
        test_stocks = [
            {'name': '平安银行', 'symbol': '000001.SZ', 'score': 85.2, 'reason': '技术面强势，短期上涨趋势'},
            {'name': '万科A', 'symbol': '000002.SZ', 'score': 78.9, 'reason': '基本面稳健，估值合理'},
            {'name': '招商银行', 'symbol': '600036.SH', 'score': 76.5, 'reason': '行业前景好，成交量放大'}
        ]
        
        report_success = sender.send_stock_report_text(test_stocks)
        
        if report_success:
            print("✅ 股票报告发送成功！")
            print("\n🎉 微信推送系统测试完成！")
            print("📱 请检查您的微信是否收到了消息")
        else:
            print("❌ 股票报告发送失败")
    else:
        print("❌ 测试消息发送失败")
        print("💡 建议:")
        print("   1. 检查网络连接")
        print("   2. 确认微信配置正确")
        print("   3. 等待API频率限制解除")

if __name__ == "__main__":
    main()
