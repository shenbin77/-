# TradingAgents-CN API 接口文档

## 概述

TradingAgents-CN API 提供基于多智能体大语言模型的股票分析服务，支持A股和海外股票的深度分析。

## 基础信息

- **服务地址**: `http://localhost:8000`
- **API版本**: v1
- **文档地址**: `http://localhost:8000/docs`
- **健康检查**: `http://localhost:8000/health`

## 认证

当前版本暂不需要认证，后续版本将支持API Key认证。

## 接口列表

### 1. 健康检查

**接口**: `GET /health`

**描述**: 检查API服务状态

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00"
}
```

### 2. 获取支持的分析师类型

**接口**: `GET /api/v1/supported_analysts`

**描述**: 获取所有支持的分析师类型

**响应示例**:
```json
{
  "analysts": [
    {
      "type": "market",
      "name": "技术分析师",
      "description": "分析技术指标和市场趋势"
    },
    {
      "type": "fundamentals",
      "name": "基本面分析师",
      "description": "分析公司财务数据和基本面指标"
    },
    {
      "type": "news",
      "name": "新闻分析师",
      "description": "处理新闻事件和宏观经济数据"
    },
    {
      "type": "social",
      "name": "社交媒体分析师",
      "description": "分析社交媒体情绪和舆论"
    }
  ]
}
```

### 3. 获取支持的模型列表

**接口**: `GET /api/v1/supported_models`

**描述**: 获取所有支持的LLM提供商和模型

**响应示例**:
```json
{
  "providers": {
    "dashscope": {
      "name": "阿里百炼",
      "models": ["qwen-turbo", "qwen-plus", "qwen-max"]
    },
    "openai": {
      "name": "OpenAI",
      "models": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"]
    },
    "google": {
      "name": "Google AI",
      "models": ["gemini-2.0-flash", "gemini-1.5-pro"]
    }
  }
}
```

### 4. 股票分析 (核心接口)

**接口**: `POST /api/v1/analyze_stock`

**描述**: 对指定股票进行多智能体深度分析

#### 请求参数

```json
{
  "stock_code": "000001.SZ",
  "market": "A股",
  "quantitative_data": {
    "pe_ratio": 12.5,
    "pb_ratio": 1.2,
    "roe": 0.15,
    "current_price": 15.68,
    "ma5": 15.2,
    "ma20": 14.8,
    "rsi": 65.2,
    "macd": 0.12,
    "volume_ratio": 1.5,
    "turnover_rate": 2.3
  },
  "analysis_config": {
    "analysts": ["market", "fundamentals", "news"],
    "depth": "standard",
    "llm_provider": "dashscope",
    "model": "qwen-plus",
    "max_debate_rounds": 2,
    "online_tools": true
  },
  "analysis_date": "2024-01-15"
}
```

#### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| stock_code | string | 是 | 股票代码，如 000001.SZ |
| market | string | 否 | 市场类型，默认"A股" |
| quantitative_data | object | 否 | 量化数据对象 |
| analysis_config | object | 否 | 分析配置对象 |
| analysis_date | string | 否 | 分析日期，格式YYYY-MM-DD |

#### 量化数据字段

| 字段 | 类型 | 说明 |
|------|------|------|
| pe_ratio | float | 市盈率 |
| pb_ratio | float | 市净率 |
| roe | float | 净资产收益率 |
| current_price | float | 当前价格 |
| ma5 | float | 5日均线 |
| ma20 | float | 20日均线 |
| rsi | float | RSI指标 |
| macd | float | MACD指标 |
| volume_ratio | float | 量比 |
| turnover_rate | float | 换手率 |

#### 分析配置字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| analysts | array | ["market", "fundamentals", "news"] | 分析师类型列表 |
| depth | string | "standard" | 分析深度: quick/standard/deep |
| llm_provider | string | "dashscope" | LLM提供商 |
| model | string | "qwen-plus" | 模型名称 |
| max_debate_rounds | int | 1 | 最大辩论轮数 |
| online_tools | bool | true | 是否使用在线工具 |

#### 响应示例

```json
{
  "success": true,
  "data": {
    "stock_code": "000001.SZ",
    "stock_name": "平安银行",
    "analysis_date": "2024-01-15",
    "overall_rating": "BUY",
    "confidence_score": 0.75,
    "risk_score": 0.35,
    "target_price": 18.50,
    "summary": "基于多维度分析，该股票具有较好的投资价值...",
    "detailed_analysis": {
      "fundamental_analysis": {
        "pe_analysis": "市盈率处于合理区间...",
        "financial_health": "财务状况良好...",
        "growth_potential": "增长潜力较大..."
      },
      "technical_analysis": {
        "trend_analysis": "技术趋势向好...",
        "support_resistance": "支撑位15.0，阻力位18.0...",
        "momentum": "动量指标积极..."
      },
      "news_sentiment": {
        "sentiment_score": 0.65,
        "key_events": ["正面新闻1", "正面新闻2"],
        "market_impact": "积极影响..."
      },
      "risk_assessment": {
        "market_risk": 0.3,
        "company_risk": 0.2,
        "liquidity_risk": 0.1,
        "overall_risk": 0.35
      }
    },
    "agents_opinions": [
      {
        "agent_type": "market",
        "opinion": "技术指标显示上涨趋势...",
        "score": 0.8,
        "confidence": 0.75
      },
      {
        "agent_type": "fundamentals",
        "opinion": "基本面数据支持买入...",
        "score": 0.7,
        "confidence": 0.8
      }
    ],
    "full_decision": {
      "action": "BUY",
      "confidence": 0.75,
      "risk_score": 0.35,
      "reasoning": "综合分析显示该股票具有投资价值...",
      "target_price": 18.50,
      "stop_loss": 14.50,
      "take_profit": 20.00
    }
  }
}
```

#### 错误响应

```json
{
  "success": false,
  "error": "分析失败: 股票代码不存在"
}
```

## 使用示例

### Python 示例

```python
import requests

# 基础分析请求
def analyze_stock(stock_code):
    url = "http://localhost:8000/api/v1/analyze_stock"
    data = {
        "stock_code": stock_code,
        "analysis_config": {
            "analysts": ["market", "fundamentals"],
            "depth": "quick",
            "llm_provider": "dashscope",
            "model": "qwen-turbo"
        }
    }
    
    response = requests.post(url, json=data)
    return response.json()

# 使用示例
result = analyze_stock("000001.SZ")
if result["success"]:
    data = result["data"]
    print(f"股票: {data['stock_name']}")
    print(f"建议: {data['overall_rating']}")
    print(f"置信度: {data['confidence_score']:.1%}")
else:
    print(f"分析失败: {result['error']}")
```

### JavaScript 示例

```javascript
async function analyzeStock(stockCode) {
    const url = 'http://localhost:8000/api/v1/analyze_stock';
    const data = {
        stock_code: stockCode,
        analysis_config: {
            analysts: ['market', 'fundamentals'],
            depth: 'quick',
            llm_provider: 'dashscope',
            model: 'qwen-turbo'
        }
    };
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('分析失败:', error);
        return { success: false, error: error.message };
    }
}

// 使用示例
analyzeStock('000001.SZ').then(result => {
    if (result.success) {
        console.log('股票:', result.data.stock_name);
        console.log('建议:', result.data.overall_rating);
        console.log('置信度:', (result.data.confidence_score * 100).toFixed(1) + '%');
    } else {
        console.log('分析失败:', result.error);
    }
});
```

## 性能说明

- **快速分析** (depth: "quick"): 2-4分钟
- **标准分析** (depth: "standard"): 4-8分钟  
- **深度分析** (depth: "deep"): 8-15分钟

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 500 | 服务器内部错误 |
| 503 | 服务暂时不可用 |

## 注意事项

1. API调用需要配置相应的LLM API密钥
2. 分析结果仅供参考，不构成投资建议
3. 建议在生产环境中添加请求频率限制
4. 长时间分析可能会超时，建议设置合理的超时时间
