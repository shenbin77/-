# 股票名称获取功能迁移到MongoDB

## 概述

本次修改将项目中获取股票名称的实现从通达信API改为从MongoDB数据库中获取，提高了数据获取的效率和可靠性。

## 修改内容

### 1. 新增MongoDB连接功能

在 `tradingagents/dataflows/tdx_utils.py` 中新增了以下功能：

- **MongoDB依赖导入**: 添加了pymongo库的导入和可用性检查
- **全局连接管理**: 新增了`_mongodb_client`和`_mongodb_db`全局变量
- **连接函数**: `_get_mongodb_connection()` - 负责建立和管理MongoDB连接
- **股票名称查询函数**: `_get_stock_name_from_mongodb()` - 从MongoDB查询股票名称

### 2. 修改股票名称获取逻辑

原有的`_get_stock_name()`方法优先级调整为：

```
缓存 -> MongoDB -> 常用股票映射 -> 通达信API -> 默认格式
```

**优势**:
- 优先从MongoDB获取，数据更全面（6251条记录 vs 原有的少量硬编码映射）
- 减少对通达信API的依赖
- 提高响应速度
- 数据一致性更好

### 3. 环境配置

MongoDB连接使用以下环境变量：
- `MONGODB_HOST`: MongoDB主机地址（默认: localhost）
- `MONGODB_PORT`: MongoDB端口（默认: 27018）
- `MONGODB_USERNAME`: 用户名
- `MONGODB_PASSWORD`: 密码
- `MONGODB_DATABASE`: 数据库名（默认: tradingagents）
- `MONGODB_AUTH_SOURCE`: 认证数据库（默认: admin）

## 测试结果

### 股票名称获取测试
- **测试股票数量**: 13个
- **成功率**: 92.3% (12/13)
- **成功案例**: 
  - 000001: 平安银行
  - 000002: 万  科Ａ
  - 600000: 浦发银行
  - 600036: 招商银行
  - 000858: 五 粮 液
  - 600519: 贵州茅台
  - 等等...

### 实时数据测试
- **功能**: 实时数据获取中正确显示股票名称
- **测试结果**: ✅ 成功
- **示例输出**:
  ```
  股票代码: 000001
  股票名称: 平安银行
  当前价格: 12.35
  涨跌幅: 0.24%
  ```

## 性能优化

1. **连接复用**: MongoDB连接采用全局单例模式，避免重复连接
2. **缓存机制**: 保留原有的内存缓存，避免重复查询
3. **超时控制**: 设置3秒连接超时，避免长时间等待
4. **错误处理**: 完善的异常处理，确保系统稳定性

## 向后兼容性

- 保留了原有的通达信API获取方式作为备选方案
- 保留了常用股票映射表
- 如果MongoDB不可用，系统会自动降级到原有方式

## 文件清单

### 修改的文件
- `tradingagents/dataflows/tdx_utils.py`: 主要修改文件

### 新增的文件
- `test_mongodb_stock_name.py`: 测试脚本
- `MONGODB_STOCK_NAME_MIGRATION.md`: 本文档

## 使用方式

修改后的使用方式与之前完全相同：

```python
from tradingagents.dataflows.tdx_utils import TongDaXinDataProvider

provider = TongDaXinDataProvider()

# 获取股票名称（现在优先从MongoDB获取）
stock_name = provider._get_stock_name('000001')  # 返回: "平安银行"

# 获取实时数据（包含从MongoDB获取的股票名称）
real_time_data = provider.get_real_time_data('000001')
print(real_time_data['name'])  # 输出: "平安银行"
```

## 总结

本次迁移成功将股票名称获取功能从通达信API迁移到MongoDB数据库，实现了：

✅ **数据完整性提升**: 从少量硬编码映射提升到6251条完整记录  
✅ **性能优化**: 减少API调用，提高响应速度  
✅ **可靠性增强**: 减少对外部API的依赖  
✅ **向后兼容**: 保留原有功能作为备选方案  
✅ **测试验证**: 92.3%的成功率，功能稳定可靠  

这次修改为项目的数据获取能力奠定了更加稳固的基础。