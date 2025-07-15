# TradingAgents 系统配置

## 当前配置

- **数据库可用**: 否
- **MongoDB**: ❌ 不可用
- **Redis**: ❌ 不可用
- **主要缓存后端**: file
- **性能模式**: 标准模式 (智能文件缓存)

## 系统特性

### 自动降级支持
- 系统会自动检测可用的数据库服务
- 如果数据库不可用，自动使用文件缓存
- 保证系统在任何环境下都能正常运行

### 性能优化
- 智能缓存策略，减少API调用
- 支持多种数据类型的TTL管理
- 自动清理过期缓存

## 使用方法

### 基本使用
```python
from tradingagents.dataflows.integrated_cache import get_cache

# 获取缓存实例
cache = get_cache()

# 保存数据
cache_key = cache.save_stock_data("AAPL", stock_data)

# 加载数据
data = cache.load_stock_data(cache_key)
```

### 检查系统状态
```bash
python scripts/validation/check_system_status.py
```

## 性能提升建议


### 安装数据库以获得更好性能

1. **安装Python依赖**:
   ```bash
   pip install pymongo redis
   ```

2. **启动MongoDB** (可选):
   ```bash
   docker run -d -p 27017:27017 --name mongodb mongo:4.4
   ```

3. **启动Redis** (可选):
   ```bash
   docker run -d -p 6379:6379 --name redis redis:alpine
   ```

4. **重新初始化系统**:
   ```bash
   python scripts/setup/initialize_system.py
   ```
