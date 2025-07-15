# 🚀 GitHub云端部署与自动化交易计划

## 📋 目录
1. [GitHub云端存储方案](#github云端存储方案)
2. [自动化部署配置](#自动化部署配置)
3. [交易前分析自动化](#交易前分析自动化)
4. [微信公众号集成](#微信公众号集成)
5. [实施时间表](#实施时间表)

## 🌐 GitHub云端存储方案

### 1. 仓库结构设计
```
quantitative-trading-system/
├── .github/
│   ├── workflows/
│   │   ├── deploy.yml           # 自动部署
│   │   ├── daily-analysis.yml   # 每日分析
│   │   ├── pre-market.yml       # 盘前分析
│   │   └── post-market.yml      # 盘后分析
│   └── ISSUE_TEMPLATE/
├── app/                         # 主应用代码
├── data/                        # 数据文件
├── config/                      # 配置文件
├── scripts/                     # 自动化脚本
├── docs/                        # 文档
├── tests/                       # 测试文件
├── docker/                      # Docker配置
├── requirements.txt             # Python依赖
├── Dockerfile                   # Docker镜像
├── docker-compose.yml           # 容器编排
└── README.md                    # 项目说明
```

### 2. 环境配置管理
```yaml
# config/production.yml
database:
  url: ${DATABASE_URL}
  
api_keys:
  tushare: ${TUSHARE_TOKEN}
  wechat: ${WECHAT_APP_SECRET}
  dashscope: ${DASHSCOPE_API_KEY}
  
trading:
  pre_market_time: "08:30"
  market_open: "09:30"
  market_close: "15:00"
  post_market_time: "15:30"
  
notification:
  wechat_webhook: ${WECHAT_WEBHOOK}
  email_smtp: ${EMAIL_SMTP}
```

### 3. 敏感信息管理
- 使用GitHub Secrets存储API密钥
- 环境变量注入
- 配置文件加密

## ⚙️ 自动化部署配置

### 1. GitHub Actions工作流

#### 主部署流程 (.github/workflows/deploy.yml)
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # 每天凌晨2点更新

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/
    
    - name: Build Docker image
      run: |
        docker build -t quant-trading:latest .
    
    - name: Deploy to cloud
      env:
        DATABASE_URL: ${{ secrets.DATABASE_URL }}
        TUSHARE_TOKEN: ${{ secrets.TUSHARE_TOKEN }}
        WECHAT_APP_SECRET: ${{ secrets.WECHAT_APP_SECRET }}
      run: |
        docker-compose up -d
```

#### 每日分析流程 (.github/workflows/daily-analysis.yml)
```yaml
name: Daily Stock Analysis

on:
  schedule:
    - cron: '30 8 * * 1-5'  # 工作日早上8:30

jobs:
  daily-analysis:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Run daily analysis
      env:
        TUSHARE_TOKEN: ${{ secrets.TUSHARE_TOKEN }}
        DASHSCOPE_API_KEY: ${{ secrets.DASHSCOPE_API_KEY }}
      run: |
        python scripts/daily_analysis.py
    
    - name: Send WeChat notification
      env:
        WECHAT_WEBHOOK: ${{ secrets.WECHAT_WEBHOOK }}
      run: |
        python scripts/send_wechat_notification.py
```

### 2. Docker容器化

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:create_app()"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5001:5001"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - TUSHARE_TOKEN=${TUSHARE_TOKEN}
    depends_on:
      - db
      - redis
    
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=trading_db
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  redis:
    image: redis:6-alpine
    
  scheduler:
    build: .
    command: python scripts/scheduler.py
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
```

## 📈 交易前分析自动化

### 1. 盘前分析脚本 (scripts/pre_market_analysis.py)
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
盘前分析脚本 - 每个交易日早上8:30执行
"""

import asyncio
from datetime import datetime, timedelta
from app import create_app
from app.services.unified_decision_engine import UnifiedDecisionEngine
from app.services.notification_service import NotificationService

async def pre_market_analysis():
    """盘前分析主函数"""
    app = create_app()
    
    with app.app_context():
        print(f"🌅 开始盘前分析 - {datetime.now()}")
        
        # 1. 获取股票池
        stock_pool = get_active_stock_pool()
        
        # 2. 批量分析
        analysis_results = []
        decision_engine = UnifiedDecisionEngine()
        
        for stock_code in stock_pool:
            try:
                result = await decision_engine.comprehensive_analysis_async(stock_code)
                analysis_results.append(result)
                print(f"✅ {stock_code} 分析完成")
            except Exception as e:
                print(f"❌ {stock_code} 分析失败: {e}")
        
        # 3. 筛选推荐股票
        recommendations = filter_recommendations(analysis_results)
        
        # 4. 生成分析报告
        report = generate_pre_market_report(recommendations)
        
        # 5. 发送通知
        notification_service = NotificationService()
        await notification_service.send_pre_market_report(report)
        
        print(f"🎉 盘前分析完成，推荐 {len(recommendations)} 只股票")

def get_active_stock_pool():
    """获取活跃股票池"""
    # 从数据库获取活跃股票
    # 可以根据成交量、市值等条件筛选
    return ["000001.SZ", "000002.SZ", "600000.SH", "600036.SH", "000858.SZ"]

def filter_recommendations(analysis_results):
    """筛选推荐股票"""
    recommendations = []
    
    for result in analysis_results:
        if not result.get('success'):
            continue
            
        final_decision = result.get('final_decision', {})
        rating = final_decision.get('rating', 'HOLD')
        confidence = final_decision.get('confidence', 0)
        
        # 筛选条件：BUY或STRONG_BUY，且置信度>70%
        if rating in ['BUY', 'STRONG_BUY'] and confidence > 0.7:
            recommendations.append(result)
    
    # 按置信度排序
    recommendations.sort(key=lambda x: x['final_decision']['confidence'], reverse=True)
    
    return recommendations[:5]  # 返回前5只

def generate_pre_market_report(recommendations):
    """生成盘前报告"""
    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "title": "📈 今日盘前推荐",
        "summary": f"基于量化分析和AI智能体综合评估，今日推荐 {len(recommendations)} 只股票",
        "recommendations": [],
        "market_outlook": "谨慎乐观",
        "risk_warning": "投资有风险，入市需谨慎"
    }
    
    for i, rec in enumerate(recommendations, 1):
        stock_code = rec.get('stock_code', '')
        final_decision = rec.get('final_decision', {})
        
        report["recommendations"].append({
            "rank": i,
            "stock_code": stock_code,
            "stock_name": get_stock_name(stock_code),
            "rating": final_decision.get('rating', 'HOLD'),
            "confidence": f"{final_decision.get('confidence', 0):.1%}",
            "reasoning": final_decision.get('reasoning', ''),
            "target_price": rec.get('ai_analysis', {}).get('target_price', ''),
            "risk_level": get_risk_level_text(final_decision.get('risk_level', 0.5))
        })
    
    return report

if __name__ == "__main__":
    asyncio.run(pre_market_analysis())
```

### 2. 定时任务调度器 (scripts/scheduler.py)
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
定时任务调度器
"""

import schedule
import time
import asyncio
from datetime import datetime, timedelta
import subprocess
import os

def is_trading_day():
    """判断是否为交易日"""
    today = datetime.now()
    # 简单判断：周一到周五
    return today.weekday() < 5

def run_pre_market_analysis():
    """运行盘前分析"""
    if is_trading_day():
        print(f"🌅 开始执行盘前分析 - {datetime.now()}")
        subprocess.run(["python", "scripts/pre_market_analysis.py"])

def run_post_market_analysis():
    """运行盘后分析"""
    if is_trading_day():
        print(f"🌆 开始执行盘后分析 - {datetime.now()}")
        subprocess.run(["python", "scripts/post_market_analysis.py"])

def run_daily_data_update():
    """运行每日数据更新"""
    print(f"📊 开始执行数据更新 - {datetime.now()}")
    subprocess.run(["python", "scripts/update_daily_data.py"])

def main():
    """主调度函数"""
    print("🚀 启动定时任务调度器...")
    
    # 盘前分析：每个交易日 8:30
    schedule.every().monday.at("08:30").do(run_pre_market_analysis)
    schedule.every().tuesday.at("08:30").do(run_pre_market_analysis)
    schedule.every().wednesday.at("08:30").do(run_pre_market_analysis)
    schedule.every().thursday.at("08:30").do(run_pre_market_analysis)
    schedule.every().friday.at("08:30").do(run_pre_market_analysis)
    
    # 盘后分析：每个交易日 15:30
    schedule.every().monday.at("15:30").do(run_post_market_analysis)
    schedule.every().tuesday.at("15:30").do(run_post_market_analysis)
    schedule.every().wednesday.at("15:30").do(run_post_market_analysis)
    schedule.every().thursday.at("15:30").do(run_post_market_analysis)
    schedule.every().friday.at("15:30").do(run_post_market_analysis)
    
    # 数据更新：每天 18:00
    schedule.every().day.at("18:00").do(run_daily_data_update)
    
    print("⏰ 定时任务已设置：")
    print("  - 盘前分析：工作日 08:30")
    print("  - 盘后分析：工作日 15:30")
    print("  - 数据更新：每天 18:00")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

if __name__ == "__main__":
    main()
```

## 📱 微信公众号集成

### 1. 微信公众号服务 (app/services/wechat_service.py)
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
微信公众号服务
"""

import requests
import json
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Any
from loguru import logger

class WeChatService:
    """微信公众号服务"""
    
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.token_expires_at = 0
    
    def get_access_token(self) -> str:
        """获取访问令牌"""
        if self.access_token and time.time() < self.token_expires_at:
            return self.access_token
        
        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if "access_token" in data:
            self.access_token = data["access_token"]
            self.token_expires_at = time.time() + data["expires_in"] - 300  # 提前5分钟刷新
            return self.access_token
        else:
            raise Exception(f"获取access_token失败: {data}")
    
    def send_template_message(self, openid: str, template_id: str, data: Dict[str, Any]) -> bool:
        """发送模板消息"""
        try:
            access_token = self.get_access_token()
            url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"
            
            payload = {
                "touser": openid,
                "template_id": template_id,
                "data": data
            }
            
            response = requests.post(url, json=payload)
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
    
    def send_stock_recommendation(self, openid: str, recommendations: List[Dict[str, Any]]) -> bool:
        """发送股票推荐消息"""
        template_id = "YOUR_TEMPLATE_ID"  # 需要在微信公众平台申请模板
        
        # 构建推荐内容
        content = "📈 今日股票推荐\n\n"
        for i, rec in enumerate(recommendations[:3], 1):  # 最多显示3只
            content += f"{i}. {rec['stock_name']}({rec['stock_code']})\n"
            content += f"   评级: {rec['rating']} | 置信度: {rec['confidence']}\n"
            content += f"   理由: {rec['reasoning'][:50]}...\n\n"
        
        content += "⚠️ 投资有风险，仅供参考"
        
        data = {
            "first": {"value": "您的每日股票推荐已生成"},
            "keyword1": {"value": datetime.now().strftime("%Y-%m-%d")},
            "keyword2": {"value": f"推荐{len(recommendations)}只股票"},
            "keyword3": {"value": content},
            "remark": {"value": "点击查看详细分析报告"}
        }
        
        return self.send_template_message(openid, template_id, data)
    
    def broadcast_daily_report(self, subscribers: List[str], report: Dict[str, Any]) -> int:
        """群发每日报告"""
        success_count = 0
        
        for openid in subscribers:
            if self.send_stock_recommendation(openid, report.get("recommendations", [])):
                success_count += 1
            time.sleep(0.1)  # 避免频率限制
        
        logger.info(f"每日报告群发完成: {success_count}/{len(subscribers)}")
        return success_count

class NotificationService:
    """通知服务"""
    
    def __init__(self):
        self.wechat = WeChatService(
            app_id=os.getenv("WECHAT_APP_ID"),
            app_secret=os.getenv("WECHAT_APP_SECRET")
        )
    
    async def send_pre_market_report(self, report: Dict[str, Any]):
        """发送盘前报告"""
        try:
            # 获取订阅用户列表
            subscribers = self.get_subscribers()
            
            # 群发报告
            success_count = self.wechat.broadcast_daily_report(subscribers, report)
            
            logger.info(f"盘前报告发送完成: {success_count} 用户")
            
        except Exception as e:
            logger.error(f"发送盘前报告失败: {e}")
    
    def get_subscribers(self) -> List[str]:
        """获取订阅用户列表"""
        # 从数据库获取订阅用户的openid
        # 这里返回示例数据
        return ["user_openid_1", "user_openid_2"]
```

### 2. 微信公众号自动发送脚本 (scripts/send_wechat_notification.py)
```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
微信公众号自动发送脚本
"""

import os
import json
from datetime import datetime
from app import create_app
from app.services.wechat_service import NotificationService

def main():
    """主函数"""
    app = create_app()
    
    with app.app_context():
        print(f"📱 开始发送微信公众号通知 - {datetime.now()}")
        
        # 读取分析报告
        report_file = "daily_analysis_report.json"
        if not os.path.exists(report_file):
            print(f"❌ 报告文件不存在: {report_file}")
            return
        
        with open(report_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        # 发送通知
        notification_service = NotificationService()
        
        try:
            # 发送盘前报告
            notification_service.send_pre_market_report(report)
            print("✅ 微信公众号通知发送成功")
            
        except Exception as e:
            print(f"❌ 微信公众号通知发送失败: {e}")

if __name__ == "__main__":
    main()
```

## 📅 实施时间表

### 第一阶段：基础部署（1周）
- [x] 代码整理和文档完善
- [ ] GitHub仓库创建和配置
- [ ] Docker容器化
- [ ] 基础CI/CD流程

### 第二阶段：自动化分析（1-2周）
- [ ] 盘前分析脚本开发
- [ ] 定时任务调度器
- [ ] 数据更新自动化
- [ ] 分析报告生成

### 第三阶段：微信集成（1周）
- [ ] 微信公众号申请和配置
- [ ] 模板消息设计
- [ ] 用户订阅管理
- [ ] 自动推送功能

### 第四阶段：优化完善（持续）
- [ ] 性能优化
- [ ] 错误处理和监控
- [ ] 用户反馈收集
- [ ] 功能迭代升级

## 🎯 预期效果

1. **自动化程度**: 95%的分析和推送工作自动化
2. **时效性**: 盘前30分钟完成分析并推送
3. **准确性**: 多维度验证，提高推荐质量
4. **用户体验**: 微信一键订阅，及时获取推荐
5. **可扩展性**: 支持更多股票和分析维度

## 💡 使用建议

1. **API密钥管理**: 妥善保管各种API密钥
2. **服务器选择**: 建议使用云服务器确保稳定性
3. **备份策略**: 定期备份数据和配置
4. **监控告警**: 设置系统监控和异常告警
5. **合规性**: 确保符合相关法规要求
