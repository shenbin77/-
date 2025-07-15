# TradingAgents-CN v0.1.2 发布说明

## 🌐 Web管理界面和Google AI支持

### ✨ 主要新功能

#### 🌐 Streamlit Web管理界面
- 完整的Web股票分析平台
- 直观的用户界面和实时进度显示
- 支持多种分析师组合选择
- 可视化的分析结果展示
- 响应式设计，支持移动端访问

#### 🤖 Google AI模型集成
- 完整的Google Gemini模型支持
- 支持gemini-2.0-flash、gemini-1.5-pro等模型
- 智能混合嵌入服务（Google AI + 阿里百炼）
- 完美的中文分析能力
- 稳定的LangChain集成

#### 🔧 多LLM提供商支持
- Web界面支持LLM提供商选择
- 阿里百炼和Google AI无缝切换
- 自动配置最优嵌入服务
- 统一的配置管理界面

### 🔧 改进优化

- 📊 新增分析配置信息显示
- 🗂️ 项目结构优化（tests/docs/web目录规范化）
- 🔑 多种API服务配置支持
- 🧪 完整的测试体系（25+个测试文件）

### 🚀 快速开始

#### 安装依赖
```bash
pip install -r requirements.txt
```

#### 配置API密钥
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，添加您的API密钥
# DASHSCOPE_API_KEY=your_dashscope_key
# GOOGLE_API_KEY=your_google_key  # 可选
```

#### 启动Web界面
```bash
# Windows
start_web.bat

# Linux/Mac
python -m streamlit run web/app.py
```

#### 使用CLI工具
```bash
python cli/main.py --stock AAPL --analysts market fundamentals
```

### 📚 文档和支持

- 📖 [完整文档](./docs/)
- 🧪 [测试指南](./tests/README.md)
- 🌐 [Web界面指南](./web/README.md)
- 💡 [示例代码](./examples/)

### 🙏 致谢

感谢 [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) 原始项目的开发者们，为金融AI领域提供了优秀的开源框架。

### 📄 许可证

本项目遵循 Apache 2.0 许可证。