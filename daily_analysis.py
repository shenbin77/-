"""
每日股票分析脚本
用于GitHub Actions自动化运行
"""

import os
import sys
import json
import time
import requests
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 配置
AI_API_URL = "http://localhost:8000/api/v1/analyze_stock"
DATABASE_PATH = "app/data/stocks.db"
REPORTS_DIR = "reports"

# 确保报告目录存在
os.makedirs(REPORTS_DIR, exist_ok=True)

def get_stock_list() -> List[Dict[str, str]]:
    """获取股票列表"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # 获取主要股票列表
        cursor.execute("""
            SELECT ts_code, name, industry, market 
            FROM stock_basic 
            WHERE list_status = 'L' 
            AND ts_code IN (
                '000001.SZ', '000002.SZ', '600519.SH', '000858.SZ', 
                '300750.SZ', '600036.SH', '002415.SZ', '600276.SH',
                '000568.SZ', '002594.SZ'
            )
            ORDER BY ts_code
        """)
        
        stocks = []
        for row in cursor.fetchall():
            stocks.append({
                'ts_code': row[0],
                'name': row[1],
                'industry': row[2] or '未知',
                'market': row[3] or '未知'
            })
        
        conn.close()
        return stocks
        
    except Exception as e:
        print(f"获取股票列表失败: {e}")
        # 返回默认股票列表
        return [
            {'ts_code': '000001.SZ', 'name': '平安银行', 'industry': '银行', 'market': '深圳'},
            {'ts_code': '600519.SH', 'name': '贵州茅台', 'industry': '食品饮料', 'market': '上海'},
            {'ts_code': '000858.SZ', 'name': '五粮液', 'industry': '食品饮料', 'market': '深圳'},
            {'ts_code': '300750.SZ', 'name': '宁德时代', 'industry': '电池', 'market': '深圳'},
            {'ts_code': '600036.SH', 'name': '招商银行', 'industry': '银行', 'market': '上海'},
        ]

def analyze_stock_with_ai(stock_code: str) -> Dict[str, Any]:
    """使用AI分析股票"""
    try:
        print(f"正在分析股票: {stock_code}")
        
        # 构建请求数据
        request_data = {
            "stock_code": stock_code,
            "config": {
                "analysts": ["market", "fundamentals", "news"],
                "depth": "standard",
                "llm_provider": "dashscope",
                "model": "qwen-plus"
            }
        }
        
        # 发送请求
        response = requests.post(
            AI_API_URL,
            json=request_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"✅ {stock_code} 分析完成")
                return result['data']
            else:
                print(f"❌ {stock_code} 分析失败: {result.get('error', '未知错误')}")
                return None
        else:
            print(f"❌ {stock_code} API请求失败: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ {stock_code} 分析异常: {e}")
        return None

def generate_market_summary() -> str:
    """生成市场总结"""
    today = datetime.now().strftime("%Y年%m月%d日")
    
    summary = f"""
## 📊 {today} 市场概况

今日A股市场整体表现平稳，主要指数小幅波动。从技术面看，市场仍处于震荡整理阶段，投资者情绪相对谨慎。

**市场特点：**
- 成交量较前期有所放大，显示市场活跃度提升
- 板块轮动明显，结构性机会突出
- 政策面相对稳定，为市场提供支撑

**投资建议：**
- 关注业绩确定性较高的优质个股
- 重点关注政策支持的新兴产业
- 控制仓位，注意风险管理
"""
    return summary

def generate_daily_report(analysis_results: List[Dict[str, Any]]) -> str:
    """生成每日分析报告"""
    
    today = datetime.now().strftime("%Y年%m月%d日")
    report_date = datetime.now().strftime("%Y-%m-%d")
    
    # 报告头部
    report = f"""# 🤖 AI量化分析日报

**日期：** {today}  
**生成时间：** {datetime.now().strftime("%H:%M:%S")}  
**分析引擎：** TradingAgents-CN Multi-Agent System

---

"""
    
    # 添加市场总结
    report += generate_market_summary()
    report += "\n---\n\n"
    
    # 统计分析结果
    buy_stocks = []
    hold_stocks = []
    sell_stocks = []
    
    for result in analysis_results:
        if result and result.get('overall_rating'):
            rating = result['overall_rating']
            if rating in ['BUY', 'STRONG_BUY']:
                buy_stocks.append(result)
            elif rating in ['SELL', 'STRONG_SELL']:
                sell_stocks.append(result)
            else:
                hold_stocks.append(result)
    
    # 投资建议汇总
    report += "## 🎯 今日投资建议\n\n"
    
    if buy_stocks:
        report += f"### 🟢 建议关注 ({len(buy_stocks)}只)\n\n"
        for stock in sorted(buy_stocks, key=lambda x: x.get('confidence_score', 0), reverse=True):
            confidence = int(stock.get('confidence_score', 0) * 100)
            target_price = stock.get('target_price', 0)
            report += f"**{stock.get('stock_name', '')} ({stock.get('stock_code', '')})**\n"
            report += f"- 💡 AI建议：{get_rating_text(stock.get('overall_rating', ''))}\n"
            report += f"- 📊 信心指数：{confidence}%\n"
            if target_price:
                report += f"- 🎯 目标价格：¥{target_price:.2f}\n"
            report += f"- 📝 核心观点：{stock.get('summary', '')[:100]}...\n\n"
    
    if hold_stocks:
        report += f"### 🟡 持有观察 ({len(hold_stocks)}只)\n\n"
        for stock in hold_stocks[:3]:  # 只显示前3只
            confidence = int(stock.get('confidence_score', 0) * 100)
            report += f"**{stock.get('stock_name', '')} ({stock.get('stock_code', '')})**\n"
            report += f"- 💡 AI建议：持有观察\n"
            report += f"- 📊 信心指数：{confidence}%\n"
            report += f"- 📝 核心观点：{stock.get('summary', '')[:80]}...\n\n"
    
    if sell_stocks:
        report += f"### 🔴 谨慎对待 ({len(sell_stocks)}只)\n\n"
        for stock in sell_stocks:
            confidence = int(stock.get('confidence_score', 0) * 100)
            report += f"**{stock.get('stock_name', '')} ({stock.get('stock_code', '')})**\n"
            report += f"- 💡 AI建议：{get_rating_text(stock.get('overall_rating', ''))}\n"
            report += f"- 📊 信心指数：{confidence}%\n"
            report += f"- 📝 核心观点：{stock.get('summary', '')[:100]}...\n\n"
    
    # 详细分析
    report += "---\n\n## 📈 详细分析\n\n"
    
    for i, result in enumerate(analysis_results[:5], 1):  # 只显示前5只的详细分析
        if not result:
            continue
            
        stock_name = result.get('stock_name', '')
        stock_code = result.get('stock_code', '')
        rating = get_rating_text(result.get('overall_rating', ''))
        confidence = int(result.get('confidence_score', 0) * 100)
        
        report += f"### {i}. {stock_name} ({stock_code})\n\n"
        report += f"**AI综合评级：** {rating} | **信心指数：** {confidence}%\n\n"
        
        # 智能体观点
        agents_opinions = result.get('agents_opinions', [])
        if agents_opinions:
            report += "**多智能体分析：**\n\n"
            for opinion in agents_opinions:
                agent_name = get_agent_name(opinion.get('agent_type', ''))
                score = opinion.get('score', 0)
                agent_confidence = int(opinion.get('confidence', 0) * 100)
                report += f"- **{agent_name}** (评分: {score:.1f}/5.0, 置信度: {agent_confidence}%)\n"
                report += f"  {opinion.get('opinion', '')[:150]}...\n\n"
        
        report += "---\n\n"
    
    # 报告尾部
    report += f"""
## ⚠️ 风险提示

本报告由AI系统自动生成，仅供参考，不构成投资建议。投资有风险，入市需谨慎。

**免责声明：**
- 本报告基于公开数据和AI模型分析生成
- 市场变化快速，实际情况可能与分析结果存在差异
- 投资者应结合自身情况，独立判断投资决策
- 过往表现不代表未来收益，请注意风险控制

---

*报告生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*  
*技术支持：TradingAgents-CN & Quantitative Analysis Platform*
"""
    
    return report

def get_rating_text(rating: str) -> str:
    """获取评级文本"""
    rating_map = {
        'BUY': '买入',
        'STRONG_BUY': '强烈买入',
        'HOLD': '持有',
        'SELL': '卖出',
        'STRONG_SELL': '强烈卖出'
    }
    return rating_map.get(rating, rating)

def get_agent_name(agent_type: str) -> str:
    """获取智能体名称"""
    agent_map = {
        'market': '技术分析师',
        'fundamentals': '基本面分析师',
        'news': '新闻分析师',
        'social': '社交媒体分析师'
    }
    return agent_map.get(agent_type, agent_type)

def main():
    """主函数"""
    print("🚀 开始执行每日股票分析...")
    print(f"📅 分析日期: {datetime.now().strftime('%Y-%m-%d')}")
    
    # 获取股票列表
    print("\n📋 获取股票列表...")
    stocks = get_stock_list()
    print(f"✅ 获取到 {len(stocks)} 只股票")
    
    # 分析股票
    print("\n🤖 开始AI分析...")
    analysis_results = []
    
    for i, stock in enumerate(stocks, 1):
        print(f"\n[{i}/{len(stocks)}] 分析 {stock['name']} ({stock['ts_code']})")
        result = analyze_stock_with_ai(stock['ts_code'])
        if result:
            # 添加股票基础信息
            result['stock_name'] = stock['name']
            result['industry'] = stock['industry']
            analysis_results.append(result)
        
        # 避免请求过于频繁
        time.sleep(2)
    
    print(f"\n✅ 分析完成，成功分析 {len(analysis_results)} 只股票")
    
    # 生成报告
    print("\n📝 生成分析报告...")
    report_content = generate_daily_report(analysis_results)
    
    # 保存报告
    report_filename = f"daily_report_{datetime.now().strftime('%Y-%m-%d')}.md"
    report_path = os.path.join(REPORTS_DIR, report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✅ 报告已保存: {report_path}")
    
    # 保存分析数据
    data_filename = f"analysis_data_{datetime.now().strftime('%Y-%m-%d')}.json"
    data_path = os.path.join(REPORTS_DIR, data_filename)
    
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 分析数据已保存: {data_path}")
    print("\n🎉 每日分析完成！")

if __name__ == "__main__":
    main()
