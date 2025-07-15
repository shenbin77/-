"""
简化版TradingAgents-CN API服务
用于快速演示和测试AI分析功能
"""

import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# 创建FastAPI应用
app = FastAPI(
    title="TradingAgents-CN Simple API",
    description="简化版AI股票分析服务",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class StockAnalysisRequest(BaseModel):
    stock_code: str = Field(..., description="股票代码")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="分析配置")

# 响应模型
class StockAnalysisResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# 股票基础信息数据库（模拟）
STOCK_INFO = {
    "000001.SZ": {"name": "平安银行", "industry": "银行", "market_cap": 3500},
    "000002.SZ": {"name": "万科A", "industry": "房地产", "market_cap": 2800},
    "600519.SH": {"name": "贵州茅台", "industry": "食品饮料", "market_cap": 21000},
    "000858.SZ": {"name": "五粮液", "industry": "食品饮料", "market_cap": 8500},
    "300750.SZ": {"name": "宁德时代", "industry": "电池", "market_cap": 12000},
    "600036.SH": {"name": "招商银行", "industry": "银行", "market_cap": 9500},
    "000858.SZ": {"name": "五粮液", "industry": "食品饮料", "market_cap": 8500},
}

def generate_ai_analysis(stock_code: str, config: Dict = None) -> Dict[str, Any]:
    """生成AI分析结果（模拟）"""
    
    # 获取股票信息
    stock_info = STOCK_INFO.get(stock_code, {"name": stock_code, "industry": "未知", "market_cap": 1000})
    stock_name = stock_info["name"]
    industry = stock_info["industry"]
    
    # 模拟分析延迟
    time.sleep(random.uniform(1, 3))
    
    # 生成随机但合理的分析结果
    confidence_base = random.uniform(0.6, 0.9)
    risk_base = random.uniform(0.2, 0.5)
    
    # 根据行业调整评级倾向
    industry_bias = {
        "银行": {"rating_bias": 0.1, "confidence_bonus": 0.05},
        "食品饮料": {"rating_bias": 0.2, "confidence_bonus": 0.1},
        "电池": {"rating_bias": 0.15, "confidence_bonus": 0.08},
        "房地产": {"rating_bias": -0.1, "confidence_bonus": -0.05},
    }
    
    bias = industry_bias.get(industry, {"rating_bias": 0, "confidence_bonus": 0})
    confidence_score = min(0.95, confidence_base + bias["confidence_bonus"])
    
    # 确定评级
    rating_score = random.uniform(0, 1) + bias["rating_bias"]
    if rating_score > 0.7:
        overall_rating = "BUY"
        rating_text = "买入"
    elif rating_score > 0.4:
        overall_rating = "HOLD"
        rating_text = "持有"
    else:
        overall_rating = "SELL"
        rating_text = "卖出"
    
    # 生成目标价格
    current_price = random.uniform(10, 200)
    if overall_rating == "BUY":
        target_price = current_price * random.uniform(1.1, 1.3)
    elif overall_rating == "HOLD":
        target_price = current_price * random.uniform(0.95, 1.1)
    else:
        target_price = current_price * random.uniform(0.8, 0.95)
    
    # 生成智能体观点
    agents_opinions = [
        {
            "agent_type": "market",
            "opinion": f"技术分析显示{stock_name}当前处于{'上升趋势' if overall_rating == 'BUY' else '震荡区间' if overall_rating == 'HOLD' else '下降通道'}，{'建议关注突破信号' if overall_rating == 'BUY' else '需要等待明确方向' if overall_rating == 'HOLD' else '建议规避风险'}。",
            "score": random.uniform(3.0, 4.5) if overall_rating == "BUY" else random.uniform(2.5, 3.5),
            "confidence": random.uniform(0.7, 0.9)
        },
        {
            "agent_type": "fundamentals",
            "opinion": f"基本面分析表明{stock_name}{'财务状况良好，盈利能力稳定' if overall_rating == 'BUY' else '基本面表现平稳，估值合理' if overall_rating == 'HOLD' else '面临一定经营压力，需关注风险'}。{industry}行业整体{'前景看好' if overall_rating == 'BUY' else '发展平稳' if overall_rating == 'HOLD' else '面临挑战'}。",
            "score": random.uniform(3.2, 4.3) if overall_rating == "BUY" else random.uniform(2.8, 3.8),
            "confidence": random.uniform(0.75, 0.85)
        },
        {
            "agent_type": "news",
            "opinion": f"近期关于{stock_name}的新闻{'整体偏正面，市场情绪积极' if overall_rating == 'BUY' else '相对平稳，无重大利好利空' if overall_rating == 'HOLD' else '存在一些负面因素，需要关注'}。行业政策环境{'相对友好' if overall_rating != 'SELL' else '存在不确定性'}。",
            "score": random.uniform(3.0, 4.2) if overall_rating == "BUY" else random.uniform(2.6, 3.6),
            "confidence": random.uniform(0.65, 0.8)
        }
    ]
    
    # 生成详细分析
    detailed_analysis = {
        "fundamental_analysis": {
            "pe_analysis": f"市盈率{'处于合理区间' if overall_rating != 'SELL' else '偏高，估值压力较大'}",
            "financial_health": f"财务状况{'稳健' if overall_rating == 'BUY' else '一般' if overall_rating == 'HOLD' else '需要关注'}",
            "growth_potential": f"增长潜力{'较大' if overall_rating == 'BUY' else '中等' if overall_rating == 'HOLD' else '有限'}"
        },
        "technical_analysis": {
            "trend_analysis": f"技术趋势{'向好' if overall_rating == 'BUY' else '震荡' if overall_rating == 'HOLD' else '偏弱'}",
            "support_resistance": f"关键位置{'支撑有效' if overall_rating != 'SELL' else '面临压力'}",
            "momentum": f"动量指标{'积极' if overall_rating == 'BUY' else '中性' if overall_rating == 'HOLD' else '偏弱'}"
        },
        "news_sentiment": {
            "sentiment_score": 0.7 if overall_rating == "BUY" else 0.5 if overall_rating == "HOLD" else 0.3,
            "key_events": [f"{industry}行业动态", "公司经营情况", "市场环境变化"],
            "market_impact": f"新闻影响{'偏正面' if overall_rating == 'BUY' else '中性' if overall_rating == 'HOLD' else '偏负面'}"
        },
        "risk_assessment": {
            "market_risk": risk_base * 0.6,
            "company_risk": risk_base * 0.8,
            "liquidity_risk": risk_base * 0.4,
            "overall_risk": risk_base
        }
    }
    
    # 生成总结
    summary = f"基于多智能体分析，{stock_name}({stock_code})当前{'具有较好的投资价值' if overall_rating == 'BUY' else '可以继续持有观察' if overall_rating == 'HOLD' else '建议谨慎对待'}。{industry}行业{'前景看好' if overall_rating == 'BUY' else '发展平稳' if overall_rating == 'HOLD' else '面临挑战'}，建议{rating_text}。"
    
    return {
        "stock_code": stock_code,
        "stock_name": stock_name,
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "overall_rating": overall_rating,
        "confidence_score": confidence_score,
        "risk_score": risk_base,
        "target_price": round(target_price, 2),
        "summary": summary,
        "detailed_analysis": detailed_analysis,
        "agents_opinions": agents_opinions,
        "full_decision": {
            "action": overall_rating,
            "confidence": confidence_score,
            "risk_score": risk_base,
            "reasoning": summary,
            "target_price": round(target_price, 2)
        }
    }

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "TradingAgents-CN Simple API Service",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/v1/analyze_stock", response_model=StockAnalysisResponse)
async def analyze_stock(request: StockAnalysisRequest):
    """分析股票"""
    try:
        print(f"开始分析股票: {request.stock_code}")
        
        # 验证股票代码格式
        if not request.stock_code or len(request.stock_code) < 6:
            raise HTTPException(status_code=400, detail="无效的股票代码")
        
        # 执行AI分析
        result = generate_ai_analysis(request.stock_code, request.config)
        
        print(f"股票分析完成: {request.stock_code}, 建议: {result['overall_rating']}")
        
        return StockAnalysisResponse(
            success=True,
            data=result
        )
        
    except Exception as e:
        print(f"分析股票失败: {request.stock_code}, 错误: {str(e)}")
        return StockAnalysisResponse(
            success=False,
            error=f"分析失败: {str(e)}"
        )

@app.get("/api/v1/supported_analysts")
async def get_supported_analysts():
    """获取支持的分析师类型"""
    return {
        "analysts": [
            {"type": "market", "name": "技术分析师", "description": "分析技术指标和市场趋势"},
            {"type": "fundamentals", "name": "基本面分析师", "description": "分析公司财务数据和基本面指标"},
            {"type": "news", "name": "新闻分析师", "description": "处理新闻事件和宏观经济数据"},
        ]
    }

@app.get("/api/v1/supported_models")
async def get_supported_models():
    """获取支持的模型列表"""
    return {
        "providers": {
            "dashscope": {
                "name": "阿里百炼",
                "models": ["qwen-turbo", "qwen-plus", "qwen-max"]
            },
            "openai": {
                "name": "OpenAI", 
                "models": ["gpt-4o-mini", "gpt-4o"]
            }
        }
    }

if __name__ == "__main__":
    print("🚀 启动 TradingAgents-CN Simple API 服务...")
    print("📡 服务地址: http://localhost:8000")
    print("📖 API文档: http://localhost:8000/docs")
    print("🔧 健康检查: http://localhost:8000/health")
    print("\n按 Ctrl+C 停止服务\n")
    
    uvicorn.run(
        "simple_api_service:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
