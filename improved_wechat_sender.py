#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的微信推送系统
Improved WeChat Sender with Rate Limiting and Error Handling
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os

class ImprovedWeChatSender:
    """改进的微信推送器"""
    
    def __init__(self):
        # 微信配置
        self.app_id = "wxf030257b07285d5a"
        self.app_secret = "31ceaff31dc2a2e13a215e1f1b948998"
        self.openids = ["o3tOfvssF1ThFelhSLLX3P2Gfkvk"]
        
        # 访问令牌
        self.access_token = None
        self.token_expires_at = 0
        
        # 频率控制
        self.last_send_time = 0
        self.min_interval = 60  # 最小发送间隔60秒
        self.daily_send_count = 0
        self.daily_limit = 10  # 每日发送限制
        self.last_reset_date = datetime.now().date()
        
        # 错误处理
        self.retry_count = 3
        self.retry_delay = 30  # 重试延迟30秒
        
        print("🤖 改进的微信推送系统初始化完成")
        print(f"📱 配置的用户数: {len(self.openids)}")
        print(f"⏰ 发送间隔限制: {self.min_interval}秒")
        print(f"📊 每日发送限制: {self.daily_limit}条")
    
    def get_access_token(self) -> Optional[str]:
        """获取访问令牌"""
        # 检查令牌是否仍然有效
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        print("🔑 正在获取新的access_token...")
        
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
                # 提前5分钟过期，确保安全
                self.token_expires_at = time.time() + data["expires_in"] - 300
                print("✅ access_token获取成功")
                return self.access_token
            else:
                print(f"❌ 获取access_token失败: {data}")
                return None
                
        except Exception as e:
            print(f"❌ 获取access_token异常: {e}")
            return None
    
    def check_rate_limit(self) -> bool:
        """检查发送频率限制"""
        current_time = time.time()
        current_date = datetime.now().date()
        
        # 重置每日计数
        if current_date != self.last_reset_date:
            self.daily_send_count = 0
            self.last_reset_date = current_date
            print(f"📅 新的一天，重置发送计数")
        
        # 检查每日限制
        if self.daily_send_count >= self.daily_limit:
            print(f"❌ 已达到每日发送限制 ({self.daily_limit}条)")
            return False
        
        # 检查时间间隔
        time_since_last = current_time - self.last_send_time
        if time_since_last < self.min_interval:
            wait_time = self.min_interval - time_since_last
            print(f"⏰ 距离上次发送时间过短，需等待 {wait_time:.1f} 秒")
            return False
        
        return True
    
    def wait_for_rate_limit(self):
        """等待满足频率限制"""
        current_time = time.time()
        time_since_last = current_time - self.last_send_time
        
        if time_since_last < self.min_interval:
            wait_time = self.min_interval - time_since_last
            print(f"⏳ 等待 {wait_time:.1f} 秒以满足频率限制...")
            time.sleep(wait_time)
    
    def send_message_with_retry(self, message: str) -> bool:
        """带重试机制的消息发送"""
        if not self.check_rate_limit():
            print("❌ 发送频率限制，跳过本次发送")
            return False
        
        # 等待满足频率限制
        self.wait_for_rate_limit()
        
        for attempt in range(self.retry_count):
            try:
                print(f"📤 尝试发送消息 (第{attempt + 1}次)...")
                
                # 获取访问令牌
                access_token = self.get_access_token()
                if not access_token:
                    print("❌ 无法获取访问令牌")
                    continue
                
                # 发送消息
                success = self._send_single_message(access_token, message)
                
                if success:
                    # 更新发送记录
                    self.last_send_time = time.time()
                    self.daily_send_count += 1
                    print(f"✅ 消息发送成功！今日已发送: {self.daily_send_count}/{self.daily_limit}")
                    return True
                else:
                    print(f"❌ 第{attempt + 1}次发送失败")
                    
                    # 如果不是最后一次尝试，等待后重试
                    if attempt < self.retry_count - 1:
                        print(f"⏳ 等待 {self.retry_delay} 秒后重试...")
                        time.sleep(self.retry_delay)
                
            except Exception as e:
                print(f"❌ 发送异常 (第{attempt + 1}次): {e}")
                
                if attempt < self.retry_count - 1:
                    print(f"⏳ 等待 {self.retry_delay} 秒后重试...")
                    time.sleep(self.retry_delay)
        
        print(f"❌ 消息发送失败，已重试 {self.retry_count} 次")
        return False
    
    def _send_single_message(self, access_token: str, message: str) -> bool:
        """发送单条消息"""
        url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token={access_token}"
        
        # 清理消息内容
        safe_message = self._clean_message(message)
        
        success_count = 0
        total_count = len(self.openids)
        
        for i, openid in enumerate(self.openids):
            print(f"📱 发送给用户 {i+1}/{total_count}: {openid[:10]}...")
            
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
                    print(f"  ✅ 发送成功")
                    success_count += 1
                else:
                    error_code = result.get('errcode')
                    error_msg = result.get('errmsg')
                    print(f"  ❌ 发送失败: {error_code} - {error_msg}")
                    
                    # 处理特定错误
                    if error_code == 45047:  # 超出响应数量限制
                        print("  ⚠️ 检测到频率限制错误，建议稍后重试")
                        return False
                    elif error_code == 40001:  # access_token无效
                        print("  ⚠️ access_token无效，需要重新获取")
                        self.access_token = None
                        return False
                
                # 用户间发送间隔
                if i < total_count - 1:
                    time.sleep(1)
                
            except Exception as e:
                print(f"  ❌ 发送异常: {e}")
        
        return success_count > 0
    
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
    
    def send_stock_report(self, stocks: List[Dict[str, Any]]) -> bool:
        """发送股票报告"""
        print("📊 准备发送股票分析报告...")
        
        # 生成报告内容
        report = self._generate_stock_report(stocks)
        
        # 发送报告
        return self.send_message_with_retry(report)
    
    def _generate_stock_report(self, stocks: List[Dict[str, Any]]) -> str:
        """生成股票报告内容"""
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
        
        return self.send_message_with_retry(test_message)
    
    def get_status(self) -> Dict[str, Any]:
        """获取推送系统状态"""
        current_date = datetime.now().date()
        
        # 重置每日计数
        if current_date != self.last_reset_date:
            self.daily_send_count = 0
            self.last_reset_date = current_date
        
        return {
            "配置用户数": len(self.openids),
            "今日已发送": self.daily_send_count,
            "每日限制": self.daily_limit,
            "剩余额度": self.daily_limit - self.daily_send_count,
            "上次发送时间": datetime.fromtimestamp(self.last_send_time).strftime("%H:%M:%S") if self.last_send_time > 0 else "未发送",
            "令牌状态": "有效" if self.access_token and time.time() < self.token_expires_at else "需要刷新"
        }

def main():
    """主函数 - 测试改进的微信推送系统"""
    print("🚀 改进的微信推送系统测试")
    print("=" * 50)
    
    sender = ImprovedWeChatSender()
    
    # 显示状态
    print("\n📊 系统状态:")
    status = sender.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # 测试消息发送
    print("\n🧪 开始测试...")
    
    # 1. 发送测试消息
    print("\n1️⃣ 发送测试消息:")
    test_success = sender.send_test_message()
    
    if test_success:
        print("✅ 测试消息发送成功！")
        
        # 2. 发送股票报告
        print("\n2️⃣ 发送股票报告:")
        test_stocks = [
            {'name': '平安银行', 'symbol': '000001.SZ', 'score': 85.2, 'reason': '技术面强势，短期上涨趋势'},
            {'name': '万科A', 'symbol': '000002.SZ', 'score': 78.9, 'reason': '基本面稳健，估值合理'},
            {'name': '招商银行', 'symbol': '600036.SH', 'score': 76.5, 'reason': '行业前景好，成交量放大'}
        ]
        
        report_success = sender.send_stock_report(test_stocks)
        
        if report_success:
            print("✅ 股票报告发送成功！")
            print("\n🎉 微信推送系统测试完成！")
            print("📱 请检查您的微信是否收到了消息")
        else:
            print("❌ 股票报告发送失败")
    else:
        print("❌ 测试消息发送失败")
    
    # 显示最终状态
    print("\n📊 最终状态:")
    final_status = sender.get_status()
    for key, value in final_status.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
