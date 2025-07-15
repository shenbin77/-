# Token使用统计和成本跟踪功能

本次更新为TradingAgents项目添加了完整的Token使用统计和成本跟踪功能。

## 🎯 功能概述

- **自动Token统计**: 自动记录所有LLM调用的输入/输出token数量
- **成本计算**: 基于官方定价自动计算使用成本
- **多存储支持**: 支持JSON文件和MongoDB两种存储方式
- **实时监控**: 提供会话成本跟踪和成本警告
- **统计分析**: 按供应商、模型、时间等维度统计使用情况

## 📁 新增文件

### 核心功能文件
- `tradingagents/config/mongodb_storage.py` - MongoDB存储适配器
- `tradingagents/config/token_tracker.py` - Token跟踪器（已集成到config_manager.py）

### 配置和示例
- `.env.example` - 环境配置示例（包含MongoDB配置）
- `examples/token_tracking_demo.py` - 功能演示脚本
- `tests/test_dashscope_token_tracking.py` - 测试脚本

### 文档
- `docs/configuration/token-tracking-guide.md` - 详细使用指南

## 🔧 修改的文件

### DashScope适配器增强
- `tradingagents/llm_adapters/dashscope_adapter.py`
  - 添加token使用量提取逻辑
  - 集成TokenTracker自动记录
  - 增加错误处理机制

### 配置管理器增强
- `tradingagents/config/config_manager.py`
  - 添加MongoDB存储支持
  - 增强使用记录管理
  - 优化统计功能

### 依赖更新
- `requirements.txt` - 添加pymongo依赖

## 🚀 快速开始

### 1. 基础配置
```bash
# 确保已安装依赖
pip install -r requirements.txt

# 配置API密钥（.env文件）
DASHSCOPE_API_KEY=your_api_key_here
```

### 2. 运行演示
```bash
# 基础功能演示
python examples/token_tracking_demo.py

# 运行测试
python tests/test_dashscope_token_tracking.py
```

### 3. MongoDB存储（可选）
```bash
# 安装MongoDB依赖
pip install pymongo

# 配置MongoDB（.env文件）
USE_MONGODB_STORAGE=true
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
MONGODB_DATABASE_NAME=tradingagents
```

## 📊 使用示例

### 自动Token统计
```python
from tradingagents.llm_adapters.dashscope_adapter import ChatDashScope
from tradingagents.config.config_manager import token_tracker

# 创建LLM实例
llm = ChatDashScope(model="qwen-turbo")

# 正常使用，token会自动统计
response = llm.invoke("你好，请介绍一下量化交易")

# 查看当前会话成本
print(f"当前会话成本: ¥{token_tracker.get_session_cost():.4f}")
```

### 查看统计信息
```python
from tradingagents.config.config_manager import config_manager

# 获取使用统计
stats = config_manager.get_usage_statistics()
print(f"总成本: ¥{stats['total_cost']:.4f}")
print(f"总调用次数: {stats['total_calls']}")
```

## 🎯 支持的LLM供应商

- ✅ **DashScope (阿里百炼)** - 完全支持
- 🔄 **OpenAI** - 计划支持
- 🔄 **其他供应商** - 计划支持

## 📈 功能特性

### Token统计
- 输入token数量
- 输出token数量
- 总token数量
- 调用时间戳

### 成本计算
- 基于官方定价
- 支持不同模型定价
- 实时成本累计
- 成本警告机制

### 存储方式
- **JSON文件**: 轻量级，适合开发测试
- **MongoDB**: 高性能，适合生产环境

### 统计分析
- 按供应商统计
- 按模型统计
- 按时间段统计
- 成本趋势分析

## 🔍 故障排除

### 常见问题
1. **导入错误**: 确保没有同名模块冲突
2. **API密钥**: 检查.env文件配置
3. **MongoDB连接**: 验证连接字符串和数据库权限

### 调试模式
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 更多信息

- 详细配置指南: `docs/configuration/token-tracking-guide.md`
- API文档: 查看各模块的docstring
- 示例代码: `examples/` 目录
- 测试用例: `tests/` 目录

## 🔮 未来计划

- [ ] 支持更多LLM供应商
- [ ] Web界面统计面板
- [ ] 成本预算和限制
- [ ] 详细的使用报告
- [ ] API调用性能分析

---

**注意**: 此功能会记录所有LLM调用的token使用情况，请确保在生产环境中妥善管理存储的数据。