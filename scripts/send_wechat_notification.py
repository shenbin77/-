#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
微信公众号自动发送脚本
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.services.wechat_service import notification_service

def load_report(report_file: str) -> dict:
    """加载分析报告"""
    try:
        if not os.path.exists(report_file):
            print(f"❌ 报告文件不存在: {report_file}")
            return None
        
        with open(report_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        print(f"✅ 成功加载报告: {report_file}")
        print(f"📊 报告包含 {len(report.get('recommendations', []))} 个推荐")
        
        return report
        
    except Exception as e:
        print(f"❌ 加载报告失败: {e}")
        return None

def send_daily_report(report_file: str = "daily_analysis_report.json"):
    """发送每日报告"""
    print(f"📱 开始发送每日报告 - {datetime.now()}")
    
    # 加载报告
    report = load_report(report_file)
    if not report:
        return False
    
    try:
        # 发送报告
        results = notification_service.send_daily_report(report)
        
        print(f"📊 发送结果:")
        print(f"  - 成功: {results['success']} 用户")
        print(f"  - 失败: {results['failed']} 用户")
        print(f"  - 总计: {results['total']} 用户")
        
        if results['success'] > 0:
            print("✅ 每日报告发送成功")
            return True
        else:
            print("⚠️ 没有成功发送给任何用户")
            return False
            
    except Exception as e:
        print(f"❌ 发送每日报告失败: {e}")
        return False

def send_market_alert(alert_type: str, message: str):
    """发送市场预警"""
    print(f"⚠️ 发送市场预警 - {datetime.now()}")
    print(f"预警类型: {alert_type}")
    print(f"预警内容: {message}")
    
    try:
        results = notification_service.send_market_alert(alert_type, message)
        
        print(f"📊 发送结果:")
        print(f"  - 成功: {results['success']} 用户")
        print(f"  - 失败: {results['failed']} 用户")
        print(f"  - 总计: {results['total']} 用户")
        
        if results['success'] > 0:
            print("✅ 市场预警发送成功")
            return True
        else:
            print("⚠️ 没有成功发送给任何用户")
            return False
            
    except Exception as e:
        print(f"❌ 发送市场预警失败: {e}")
        return False

def test_wechat_service():
    """测试微信服务"""
    print("🧪 测试微信服务...")
    
    # 检查配置
    app_id = os.getenv("WECHAT_APP_ID")
    app_secret = os.getenv("WECHAT_APP_SECRET")
    
    if not app_id or not app_secret:
        print("⚠️ 微信公众号配置不完整")
        print("请设置环境变量:")
        print("  - WECHAT_APP_ID: 微信公众号AppID")
        print("  - WECHAT_APP_SECRET: 微信公众号AppSecret")
        print("  - WECHAT_STOCK_TEMPLATE_ID: 股票推荐模板ID")
        print("  - WECHAT_ALERT_TEMPLATE_ID: 市场预警模板ID")
        return False
    
    # 测试获取access_token
    try:
        access_token = notification_service.wechat.get_access_token()
        if access_token:
            print("✅ 微信access_token获取成功")
            print(f"Token: {access_token[:20]}...")
        else:
            print("❌ 微信access_token获取失败")
            return False
    except Exception as e:
        print(f"❌ 测试微信服务失败: {e}")
        return False
    
    # 检查订阅用户
    subscribers = notification_service.subscriber_manager.get_active_subscribers()
    print(f"📱 活跃订阅用户: {len(subscribers)} 个")
    
    if len(subscribers) == 0:
        print("⚠️ 没有订阅用户，可以手动添加测试用户:")
        print("notification_service.subscriber_manager.add_subscriber('test_openid')")
    
    return True

def add_test_subscriber(openid: str = None):
    """添加测试订阅用户"""
    if not openid:
        openid = input("请输入测试用户的OpenID: ").strip()
    
    if not openid:
        print("❌ OpenID不能为空")
        return False
    
    try:
        notification_service.subscriber_manager.add_subscriber(openid, {
            "nickname": "测试用户",
            "source": "manual_add"
        })
        print(f"✅ 成功添加测试订阅用户: {openid}")
        return True
    except Exception as e:
        print(f"❌ 添加测试用户失败: {e}")
        return False

def list_subscribers():
    """列出所有订阅用户"""
    subscribers = notification_service.subscriber_manager.subscribers
    
    print(f"📱 订阅用户列表 (共 {len(subscribers)} 个):")
    print("-" * 60)
    
    for openid, info in subscribers.items():
        status = "✅ 活跃" if info.get("active", True) else "❌ 非活跃"
        subscribe_time = info.get("subscribe_time", "未知")
        nickname = info.get("user_info", {}).get("nickname", "未知")
        
        print(f"OpenID: {openid}")
        print(f"昵称: {nickname}")
        print(f"状态: {status}")
        print(f"订阅时间: {subscribe_time}")
        print(f"偏好设置: {info.get('preferences', {})}")
        print("-" * 60)

def create_sample_report():
    """创建示例报告用于测试"""
    sample_report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "title": "📈 测试股票推荐",
        "summary": "这是一个测试报告",
        "recommendations": [
            {
                "rank": 1,
                "stock_code": "000001.SZ",
                "stock_name": "平安银行",
                "rating": "BUY",
                "confidence": "85.2%",
                "reasoning": "技术面突破，基本面良好",
                "risk_level": "中等风险",
                "predicted_return": "3.5%",
                "momentum_score": "0.75"
            },
            {
                "rank": 2,
                "stock_code": "600036.SH",
                "stock_name": "招商银行",
                "rating": "STRONG_BUY",
                "confidence": "92.1%",
                "reasoning": "多因子模型显示强烈买入信号",
                "risk_level": "低风险",
                "predicted_return": "5.2%",
                "momentum_score": "0.88"
            }
        ]
    }
    
    filename = "test_report.json"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(sample_report, f, indent=2, ensure_ascii=False)
        print(f"✅ 示例报告已创建: {filename}")
        return filename
    except Exception as e:
        print(f"❌ 创建示例报告失败: {e}")
        return None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="微信公众号自动发送脚本")
    parser.add_argument("action", choices=[
        "send-daily", "send-alert", "test", "add-user", "list-users", "create-sample"
    ], help="执行的操作")
    parser.add_argument("--report", default="daily_analysis_report.json", help="报告文件路径")
    parser.add_argument("--alert-type", choices=["warning", "danger", "info", "success"], 
                       default="warning", help="预警类型")
    parser.add_argument("--message", help="预警消息内容")
    parser.add_argument("--openid", help="用户OpenID")
    
    args = parser.parse_args()
    
    # 创建Flask应用上下文
    app = create_app()
    
    with app.app_context():
        if args.action == "send-daily":
            success = send_daily_report(args.report)
            
        elif args.action == "send-alert":
            if not args.message:
                print("❌ 请提供预警消息内容 --message")
                return False
            success = send_market_alert(args.alert_type, args.message)
            
        elif args.action == "test":
            success = test_wechat_service()
            
        elif args.action == "add-user":
            success = add_test_subscriber(args.openid)
            
        elif args.action == "list-users":
            list_subscribers()
            success = True
            
        elif args.action == "create-sample":
            filename = create_sample_report()
            if filename:
                print(f"💡 可以使用以下命令测试发送:")
                print(f"python scripts/send_wechat_notification.py send-daily --report {filename}")
            success = filename is not None
            
        else:
            print(f"❌ 未知操作: {args.action}")
            success = False
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断操作")
        exit(1)
    except Exception as e:
        print(f"❌ 程序异常: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
