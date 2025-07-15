
# 🔑 API密钥获取指南

## 1. 阿里百炼 (DashScope) - 已配置 ✅
- 您的密钥: sk-61f17f4d75fc45429a44977814eb8cf7
- 状态: 已在.env文件中配置完成

## 2. FinnHub API - 需要配置 ⚠️
- 访问: https://finnhub.io/
- 注册免费账户
- 获取API密钥
- 在.env文件中替换: FINNHUB_API_KEY=your_finnhub_api_key_here

## 3. 可选API (根据需要配置)
- OpenAI: https://platform.openai.com/
- Google AI: https://ai.google.dev/
- Anthropic: https://console.anthropic.com/

# 💰 成本估算
- 阿里百炼: 每次分析约0.1-0.3元
- FinnHub: 免费版每分钟60次请求
- 总成本: 每月约150-500元 (中等使用量)

# 🚀 下一步
1. 获取FinnHub API密钥
2. 运行: python test_api_configuration.py
3. 测试TradingAgents功能
4. 开始股票分析
