#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
微信公众号服务
"""

import requests
import json
import hashlib
import time
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from loguru import logger

class WeChatService:
    """微信公众号服务"""
    
    def __init__(self, app_id: str = None, app_secret: str = None):
        self.app_id = app_id or os.getenv("WECHAT_APP_ID")
        self.app_secret = app_secret or os.getenv("WECHAT_APP_SECRET")
        self.access_token = None
        self.token_expires_at = 0
        
        if not self.app_id or not self.app_secret:
            logger.warning("微信公众号配置不完整，部分功能将不可用")
    
    def get_access_token(self) -> Optional[str]:
        """获取访问令牌"""
        if not self.app_id or not self.app_secret:
            logger.error("微信公众号配置不完整")
            return None
            
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
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
                self.token_expires_at = time.time() + data["expires_in"] - 300  # 提前5分钟刷新
                logger.info("微信access_token获取成功")
                return self.access_token
            else:
                logger.error(f"获取access_token失败: {data}")
                return None
                
        except Exception as e:
            logger.error(f"获取access_token异常: {e}")
            return None
    
    def send_template_message(self, openid: str, template_id: str, data: Dict[str, Any], 
                            url: str = None) -> bool:
        """发送模板消息"""
        try:
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
            
            response = requests.post(api_url, json=payload, timeout=10)
            result = response.json()
            
            if result.get("errcode") == 0:
                logger.info(f"模板消息发送成功: {openid}")
                return True
            else:
                logger.error(f"模板消息发送失败: {result}")
                return False
                
        except Exception as e:
            logger.error(f"发送模板消息异常: {e}")
            return False
    
    def send_stock_recommendation(self, openid: str, recommendations: List[Dict[str, Any]], 
                                template_id: str = None) -> bool:
        """发送股票推荐消息"""
        if not template_id:
            template_id = os.getenv("WECHAT_STOCK_TEMPLATE_ID")
            
        if not template_id:
            logger.error("未配置股票推荐模板ID")
            return False
        
        try:
            # 构建推荐内容
            if not recommendations:
                content = "今日暂无推荐股票"
                summary = "市场观望"
            else:
                content = ""
                for i, rec in enumerate(recommendations[:5], 1):  # 最多显示5只
                    content += f"{i}. {rec['stock_name']}({rec['stock_code']})\n"
                    content += f"评级: {rec['rating']} | 置信度: {rec['confidence']}\n"
                    if rec.get('predicted_return'):
                        content += f"预测收益: {rec['predicted_return']}\n"
                    content += "\n"
                
                summary = f"推荐{len(recommendations)}只股票"
            
            # 模板数据
            template_data = {
                "first": {"value": "📈 您的每日股票推荐", "color": "#173177"},
                "keyword1": {"value": datetime.now().strftime("%Y年%m月%d日"), "color": "#173177"},
                "keyword2": {"value": summary, "color": "#173177"},
                "keyword3": {"value": content, "color": "#173177"},
                "remark": {"value": "💡 投资有风险，仅供参考\n点击查看详细分析", "color": "#FF6B6B"}
            }
            
            # 详情页面URL
            detail_url = f"https://your-domain.com/unified-analysis?date={datetime.now().strftime('%Y-%m-%d')}"
            
            return self.send_template_message(openid, template_id, template_data, detail_url)
            
        except Exception as e:
            logger.error(f"发送股票推荐异常: {e}")
            return False
    
    def send_market_alert(self, openid: str, alert_type: str, message: str, 
                         template_id: str = None) -> bool:
        """发送市场预警消息"""
        if not template_id:
            template_id = os.getenv("WECHAT_ALERT_TEMPLATE_ID")
            
        if not template_id:
            logger.error("未配置市场预警模板ID")
            return False
        
        try:
            alert_colors = {
                "warning": "#FF9500",
                "danger": "#FF3B30",
                "info": "#007AFF",
                "success": "#34C759"
            }
            
            color = alert_colors.get(alert_type, "#173177")
            
            template_data = {
                "first": {"value": "⚠️ 市场预警通知", "color": color},
                "keyword1": {"value": datetime.now().strftime("%Y-%m-%d %H:%M"), "color": "#173177"},
                "keyword2": {"value": alert_type.upper(), "color": color},
                "keyword3": {"value": message, "color": "#173177"},
                "remark": {"value": "请及时关注市场变化", "color": "#666666"}
            }
            
            return self.send_template_message(openid, template_id, template_data)
            
        except Exception as e:
            logger.error(f"发送市场预警异常: {e}")
            return False
    
    def broadcast_message(self, subscribers: List[str], message_func, *args, **kwargs) -> Dict[str, int]:
        """群发消息"""
        results = {"success": 0, "failed": 0, "total": len(subscribers)}
        
        for openid in subscribers:
            try:
                if message_func(openid, *args, **kwargs):
                    results["success"] += 1
                else:
                    results["failed"] += 1
                    
                # 避免频率限制
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"群发消息失败 {openid}: {e}")
                results["failed"] += 1
        
        logger.info(f"群发完成: 成功{results['success']}, 失败{results['failed']}, 总计{results['total']}")
        return results
    
    def get_user_info(self, openid: str) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return None
                
            url = f"https://api.weixin.qq.com/cgi-bin/user/info"
            params = {
                "access_token": access_token,
                "openid": openid,
                "lang": "zh_CN"
            }
            
            response = requests.get(url, params=params, timeout=10)
            result = response.json()
            
            if "errcode" not in result:
                return result
            else:
                logger.error(f"获取用户信息失败: {result}")
                return None
                
        except Exception as e:
            logger.error(f"获取用户信息异常: {e}")
            return None

class WeChatSubscriberManager:
    """微信订阅用户管理"""
    
    def __init__(self):
        self.subscribers_file = "data/wechat_subscribers.json"
        self.subscribers = self.load_subscribers()
    
    def load_subscribers(self) -> Dict[str, Dict[str, Any]]:
        """加载订阅用户"""
        try:
            if os.path.exists(self.subscribers_file):
                with open(self.subscribers_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"加载订阅用户失败: {e}")
            return {}
    
    def save_subscribers(self):
        """保存订阅用户"""
        try:
            os.makedirs(os.path.dirname(self.subscribers_file), exist_ok=True)
            with open(self.subscribers_file, 'w', encoding='utf-8') as f:
                json.dump(self.subscribers, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存订阅用户失败: {e}")
    
    def add_subscriber(self, openid: str, user_info: Dict[str, Any] = None):
        """添加订阅用户"""
        self.subscribers[openid] = {
            "openid": openid,
            "subscribe_time": datetime.now().isoformat(),
            "active": True,
            "user_info": user_info or {},
            "preferences": {
                "daily_report": True,
                "market_alert": True,
                "risk_warning": True
            }
        }
        self.save_subscribers()
        logger.info(f"新增订阅用户: {openid}")
    
    def remove_subscriber(self, openid: str):
        """移除订阅用户"""
        if openid in self.subscribers:
            del self.subscribers[openid]
            self.save_subscribers()
            logger.info(f"移除订阅用户: {openid}")
    
    def get_active_subscribers(self) -> List[str]:
        """获取活跃订阅用户"""
        return [openid for openid, info in self.subscribers.items() 
                if info.get("active", True)]
    
    def update_preferences(self, openid: str, preferences: Dict[str, bool]):
        """更新用户偏好"""
        if openid in self.subscribers:
            self.subscribers[openid]["preferences"].update(preferences)
            self.save_subscribers()

class NotificationService:
    """通知服务"""
    
    def __init__(self):
        self.wechat = WeChatService()
        self.subscriber_manager = WeChatSubscriberManager()
    
    def send_daily_report(self, report: Dict[str, Any]) -> Dict[str, int]:
        """发送每日报告"""
        try:
            subscribers = self.subscriber_manager.get_active_subscribers()
            
            if not subscribers:
                logger.warning("没有活跃的订阅用户")
                return {"success": 0, "failed": 0, "total": 0}
            
            recommendations = report.get("recommendations", [])
            
            results = self.wechat.broadcast_message(
                subscribers, 
                self.wechat.send_stock_recommendation,
                recommendations
            )
            
            logger.info(f"每日报告发送完成: {results}")
            return results
            
        except Exception as e:
            logger.error(f"发送每日报告失败: {e}")
            return {"success": 0, "failed": 1, "total": 1}
    
    def send_market_alert(self, alert_type: str, message: str) -> Dict[str, int]:
        """发送市场预警"""
        try:
            subscribers = self.subscriber_manager.get_active_subscribers()
            
            # 只发送给开启预警的用户
            alert_subscribers = [
                openid for openid in subscribers
                if self.subscriber_manager.subscribers[openid]
                .get("preferences", {}).get("market_alert", True)
            ]
            
            if not alert_subscribers:
                logger.warning("没有开启预警的订阅用户")
                return {"success": 0, "failed": 0, "total": 0}
            
            results = self.wechat.broadcast_message(
                alert_subscribers,
                self.wechat.send_market_alert,
                alert_type,
                message
            )
            
            logger.info(f"市场预警发送完成: {results}")
            return results
            
        except Exception as e:
            logger.error(f"发送市场预警失败: {e}")
            return {"success": 0, "failed": 1, "total": 1}

# 全局实例
notification_service = NotificationService()
