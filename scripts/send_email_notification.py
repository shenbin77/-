#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发送邮件通知脚本
"""

import os
import sys
import json
import logging
import smtplib
import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models import AnalysisResult

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def send_daily_email():
    """发送每日分析邮件"""
    try:
        # 获取环境变量
        email_host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        email_user = os.getenv('EMAIL_USER')
        email_password = os.getenv('EMAIL_PASSWORD')
        
        if not all([email_user, email_password]):
            logger.warning("邮件配置不完整，跳过邮件发送")
            return True
        
        # 获取今日分析结果
        app = create_app()
        with app.app_context():
            today = datetime.date.today()
            results = AnalysisResult.query.filter_by(analysis_date=today).all()
            
            if not results:
                logger.warning("今日没有分析结果，跳过邮件发送")
                return True
            
            # 准备邮件内容
            subject = f"每日股票分析报告 - {today.isoformat()}"
            
            # 统计数据
            buy_count = len([r for r in results if r.recommendation == 'BUY'])
            sell_count = len([r for r in results if r.recommendation == 'SELL'])
            hold_count = len([r for r in results if r.recommendation == 'HOLD'])
            
            # 生成邮件正文
            body = f"""
每日股票分析报告

分析日期: {today.isoformat()}
分析股票总数: {len(results)}

推荐统计:
- 买入推荐: {buy_count} 只
- 卖出推荐: {sell_count} 只  
- 持有推荐: {hold_count} 只

详细推荐:

买入推荐 ({buy_count}只):
"""
            
            # 添加买入推荐
            buy_stocks = [r for r in results if r.recommendation == 'BUY']
            for stock in buy_stocks[:5]:  # 只显示前5只
                body += f"- {stock.stock_code} (置信度: {stock.confidence:.2f})\n"
            
            body += f"\n卖出推荐 ({sell_count}只):\n"
            
            # 添加卖出推荐
            sell_stocks = [r for r in results if r.recommendation == 'SELL']
            for stock in sell_stocks[:5]:  # 只显示前5只
                body += f"- {stock.stock_code} (置信度: {stock.confidence:.2f})\n"
            
            body += """

注意: 本报告由AI自动生成，仅供参考，不构成投资建议。
请在投资前进行充分的研究和风险评估。

祝投资顺利！
AI股票分析系统
"""
            
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = email_user  # 发送给自己
            msg['Subject'] = subject
            
            # 添加正文
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 添加HTML报告附件
            html_file = Path('reports') / f'daily_report_{today.isoformat()}.html'
            if html_file.exists():
                with open(html_file, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= daily_report_{today.isoformat()}.html'
                    )
                    msg.attach(part)
            
            # 发送邮件
            server = smtplib.SMTP(email_host, 587)
            server.starttls()
            server.login(email_user, email_password)
            text = msg.as_string()
            server.sendmail(email_user, email_user, text)
            server.quit()
            
            logger.info(f"邮件发送成功: {subject}")
            return True
            
    except Exception as e:
        logger.error(f"发送邮件失败: {e}")
        return False

def send_webhook_notification():
    """发送Webhook通知"""
    try:
        import requests
        
        webhook_url = os.getenv('WEBHOOK_URL')
        if not webhook_url or webhook_url == 'https://your-webhook-url.com/notify':
            logger.info("Webhook URL未配置，跳过Webhook通知")
            return True
        
        # 获取今日分析结果
        app = create_app()
        with app.app_context():
            today = datetime.date.today()
            results = AnalysisResult.query.filter_by(analysis_date=today).all()
            
            if not results:
                logger.warning("今日没有分析结果，跳过Webhook通知")
                return True
            
            # 准备通知数据
            buy_count = len([r for r in results if r.recommendation == 'BUY'])
            sell_count = len([r for r in results if r.recommendation == 'SELL'])
            hold_count = len([r for r in results if r.recommendation == 'HOLD'])
            
            payload = {
                'type': 'daily_analysis',
                'date': today.isoformat(),
                'summary': {
                    'total': len(results),
                    'buy': buy_count,
                    'sell': sell_count,
                    'hold': hold_count
                },
                'message': f'每日分析完成: 共分析{len(results)}只股票，买入{buy_count}只，卖出{sell_count}只，持有{hold_count}只'
            }
            
            # 发送Webhook
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info("Webhook通知发送成功")
            return True
            
    except Exception as e:
        logger.error(f"发送Webhook通知失败: {e}")
        return False

def main():
    """主函数"""
    try:
        # 发送邮件通知
        email_success = send_daily_email()
        
        # 发送Webhook通知
        webhook_success = send_webhook_notification()
        
        if email_success and webhook_success:
            logger.info("所有通知发送成功")
            sys.exit(0)
        else:
            logger.warning("部分通知发送失败")
            sys.exit(0)  # 不因为通知失败而中断流程
            
    except Exception as e:
        logger.error(f"脚本执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
