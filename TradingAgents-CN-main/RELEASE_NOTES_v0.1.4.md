# TradingAgents v0.1.4 发布说明 | Release Notes

发布日期 | Release Date: 2024-12-19

## 🎯 主要功能 | Major Features

### 数据目录配置系统 | Data Directory Configuration System

本版本引入了完整的数据目录配置管理系统，解决了路径硬编码和跨平台兼容性问题。

This version introduces a complete data directory configuration management system, solving path hardcoding and cross-platform compatibility issues.

#### 核心功能 | Core Features

- **灵活的配置方式** | Flexible Configuration Methods
  - CLI命令配置 | CLI command configuration
  - 环境变量配置 | Environment variable configuration
  - 程序化配置 | Programmatic configuration

- **自动目录管理** | Automatic Directory Management
  - 自动创建必要的目录结构 | Automatically create necessary directory structure
  - 跨平台路径处理 | Cross-platform path handling
  - 目录存在性验证 | Directory existence validation

- **配置优先级** | Configuration Priority
  1. 环境变量 | Environment Variables (最高优先级 | Highest Priority)
  2. CLI设置 | CLI Settings
  3. 默认配置 | Default Configuration

## 🔧 新增功能 | New Features

### CLI命令增强 | CLI Command Enhancement

#### 新增 `data-config` 命令 | New `data-config` Command

```bash
# 查看当前配置 | View current configuration
python -m cli.main data-config
python -m cli.main data-config --show

# 设置自定义数据目录 | Set custom data directory
python -m cli.main data-config --set "C:\MyTradingData"

# 重置为默认配置 | Reset to default configuration
python -m cli.main data-config --reset
```

### 环境变量支持 | Environment Variable Support

- `TRADINGAGENTS_DATA_DIR` - 数据目录路径 | Data directory path
- `TRADINGAGENTS_CACHE_DIR` - 缓存目录路径 | Cache directory path
- `TRADINGAGENTS_RESULTS_DIR` - 结果目录路径 | Results directory path

### 配置管理器增强 | Configuration Manager Enhancement

- 新增数据目录相关配置项 | Added data directory related configuration items
- 支持动态配置更新 | Support dynamic configuration updates
- 集成目录自动创建功能 | Integrated automatic directory creation

### 缓存子系统架构优化 | Cache Subsystem Architecture Optimization

#### 四层缓存架构设计 | Four-Layer Cache Architecture Design

TradingAgents v0.1.4 实现了完整的四层缓存架构，提供从毫秒级到持久化的全方位数据缓存解决方案：

TradingAgents v0.1.4 implements a complete four-layer cache architecture, providing comprehensive data caching solutions from millisecond-level to persistent storage:

- **L1 内存缓存** | **L1 Memory Cache**: Python内存中的快速数据访问（毫秒级响应）| Fast data access in Python memory (millisecond response)
- **L2 本地文件缓存** | **L2 Local File Cache**: 基于磁盘的持久化缓存（秒级响应）| Disk-based persistent cache (second-level response)
- **L3 Redis缓存** | **L3 Redis Cache**: 分布式内存数据库缓存（毫秒级响应，支持集群）| Distributed memory database cache (millisecond response, cluster support)
- **L4 MongoDB缓存** | **L4 MongoDB Cache**: 文档数据库持久化存储（秒级响应，支持复杂查询）| Document database persistent storage (second-level response, complex query support)

#### MongoDB与Redis的分工协作 | MongoDB and Redis Division of Labor

**MongoDB (持久化层)** | **MongoDB (Persistence Layer)**:
- **作用** | **Role**: 长期数据存储和复杂查询支持 | Long-term data storage and complex query support
- **数据类型** | **Data Types**: 股票历史数据、新闻数据、基本面分析数据 | Stock historical data, news data, fundamental analysis data
- **索引优化** | **Index Optimization**: 针对symbol、data_source、时间范围建立复合索引 | Composite indexes for symbol, data_source, and time range
- **集合设计** | **Collection Design**:
  - `stock_data`: 股票价格数据 | Stock price data
  - `news_data`: 新闻和资讯数据 | News and information data
  - `fundamentals_data`: 基本面分析数据 | Fundamental analysis data
- **数据格式** | **Data Format**: JSON文档，支持DataFrame序列化存储 | JSON documents with DataFrame serialization support

**Redis (快速缓存层)** | **Redis (Fast Cache Layer)**:
- **作用** | **Role**: 高频访问数据的快速缓存 | Fast cache for high-frequency access data
- **TTL策略** | **TTL Strategy**: 
  - 股票数据 | Stock data: 6小时自动过期 | 6 hours auto-expiration
  - 新闻数据 | News data: 24小时自动过期 | 24 hours auto-expiration
  - 基本面数据 | Fundamental data: 24小时自动过期 | 24 hours auto-expiration
- **数据同步** | **Data Sync**: 从MongoDB加载时自动同步到Redis | Auto-sync to Redis when loading from MongoDB
- **内存优化** | **Memory Optimization**: JSON序列化存储，支持中文数据 | JSON serialization storage with Chinese data support

#### 与缓存目录的配合机制 | Integration with Cache Directory

**本地文件缓存目录结构** | **Local File Cache Directory Structure**:
```
data_cache/
├── us_stocks/          # 美股数据缓存 | US stock data cache
├── china_stocks/       # A股数据缓存 | China A-share data cache
├── us_news/           # 美股新闻缓存 | US stock news cache
├── china_news/        # A股新闻缓存 | China A-share news cache
├── us_fundamentals/   # 美股基本面缓存 | US stock fundamentals cache
├── china_fundamentals/ # A股基本面缓存 | China A-share fundamentals cache
└── metadata/          # 缓存元数据 | Cache metadata
```

**智能缓存策略** | **Intelligent Cache Strategy**:
- **市场分类** | **Market Classification**: 自动识别美股/A股，应用不同TTL策略 | Auto-identify US/China stocks with different TTL strategies
- **数据源适配** | **Data Source Adaptation**: 支持多数据源（yfinance、finnhub、通达信等）| Support multiple data sources (yfinance, finnhub, TongDaXin, etc.)
- **缓存键生成** | **Cache Key Generation**: MD5哈希确保唯一性和快速查找 | MD5 hash for uniqueness and fast lookup
- **元数据管理** | **Metadata Management**: 独立的元数据文件记录缓存信息 | Independent metadata files for cache information

**缓存查找优先级** | **Cache Lookup Priority**:
1. **Redis查找** | **Redis Lookup** → 最快响应 | Fastest response
2. **MongoDB查找** | **MongoDB Lookup** → 如果Redis未命中 | If Redis miss
3. **本地文件查找** | **Local File Lookup** → 如果数据库未连接 | If database not connected
4. **API重新获取** | **API Re-fetch** → 如果所有缓存都未命中 | If all caches miss

#### 缓存配置增强 | Cache Configuration Enhancement

```python
# 智能缓存配置 | Intelligent cache configuration
cache_config = {
    'us_stock_data': {
        'ttl_hours': 2,      # 美股2小时TTL | US stocks 2-hour TTL
        'max_files': 1000,   # 最大文件数 | Max file count
        'description': '美股历史数据' | 'US stock historical data'
    },
    'china_stock_data': {
        'ttl_hours': 1,      # A股1小时TTL（实时性要求高）| A-shares 1-hour TTL (high real-time requirement)
        'max_files': 1000,
        'description': 'A股历史数据' | 'China A-share historical data'
    },
    'us_news': {
        'ttl_hours': 6,      # 新闻6小时TTL | News 6-hour TTL
        'max_files': 500,
        'description': '美股新闻数据' | 'US stock news data'
    }
}
```

**缓存性能优化** | **Cache Performance Optimization**:
- **连接池管理** | **Connection Pool Management**: MongoDB和Redis连接复用 | MongoDB and Redis connection reuse
- **批量操作** | **Batch Operations**: 支持批量数据写入和查询 | Support batch data write and query
- **错误容错** | **Error Tolerance**: 单层缓存失败不影响其他层级 | Single-layer cache failure doesn't affect other layers
- **监控统计** | **Monitoring Statistics**: 实时缓存命中率和性能指标 | Real-time cache hit rate and performance metrics

## 🐛 问题修复 | Bug Fixes

### Finnhub新闻数据路径修复 | Finnhub News Data Path Fix

- **问题** | Issue: 硬编码的Unix路径导致Windows系统无法正常工作
- **解决方案** | Solution: 实现跨平台路径处理和动态配置
- **影响** | Impact: 解决了"No such file or directory"错误

### 跨平台兼容性改进 | Cross-Platform Compatibility Improvements

- 修复路径分隔符问题 | Fixed path separator issues
- 改进错误处理和用户提示 | Improved error handling and user prompts
- 增强目录权限检查 | Enhanced directory permission checks

## 📁 目录结构 | Directory Structure

配置数据目录后，系统自动创建以下结构：

After configuring the data directory, the system automatically creates the following structure:

```
data/
├── cache/                          # 缓存目录 | Cache directory
├── finnhub_data/                   # Finnhub数据目录 | Finnhub data directory
│   ├── news_data/                  # 新闻数据 | News data
│   ├── insider_sentiment/          # 内部人情绪数据 | Insider sentiment data
│   └── insider_transactions/       # 内部人交易数据 | Insider transaction data
└── results/                        # 分析结果 | Analysis results
```

## 📚 新增文档 | New Documentation

### 配置指南 | Configuration Guides

- **数据目录配置指南** | Data Directory Configuration Guide
  - 文件位置 | File Location: `docs/configuration/data-directory-configuration.md`
  - 详细的配置方法和最佳实践 | Detailed configuration methods and best practices

- **故障排除指南** | Troubleshooting Guide
  - 文件位置 | File Location: `docs/troubleshooting/finnhub-news-data-setup.md`
  - Finnhub新闻数据配置问题解决方案 | Finnhub news data configuration issue solutions

### 示例和测试 | Examples and Tests

- **配置演示脚本** | Configuration Demo Script
  - 文件位置 | File Location: `examples/data_dir_config_demo.py`
  - 展示各种配置方法的使用 | Demonstrates usage of various configuration methods

- **测试脚本** | Test Scripts
  - 文件位置 | File Location: `test_data_config_cli.py`
  - 验证配置功能的完整性 | Validates the completeness of configuration features

- **示例数据生成脚本** | Sample Data Generation Script
  - 文件位置 | File Location: `scripts/download_finnhub_sample_data.py`
  - 生成Finnhub测试数据 | Generates Finnhub test data

## 🔄 升级指南 | Upgrade Guide

### 从v0.1.3升级 | Upgrading from v0.1.3

1. **更新代码** | Update Code
   ```bash
   git pull origin main
   ```

2. **配置数据目录** | Configure Data Directory
   ```bash
   # 查看当前配置 | View current configuration
   python -m cli.main data-config
   
   # 如需要，设置自定义路径 | Set custom path if needed
   python -m cli.main data-config --set "your/custom/path"
   ```

3. **验证配置** | Verify Configuration
   ```bash
   python test_data_config_cli.py
   ```

### 迁移现有数据 | Migrating Existing Data

如果您有现有的数据文件，可以：

If you have existing data files, you can:

1. 将现有数据复制到新的数据目录 | Copy existing data to the new data directory
2. 使用环境变量指向现有数据位置 | Use environment variables to point to existing data location
3. 使用CLI命令设置数据目录到现有位置 | Use CLI commands to set data directory to existing location

## 🧪 测试验证 | Testing and Validation

### 功能测试 | Feature Testing

- ✅ 数据目录配置功能 | Data directory configuration functionality
- ✅ CLI命令完整性 | CLI command completeness
- ✅ 环境变量支持 | Environment variable support
- ✅ 跨平台兼容性 | Cross-platform compatibility
- ✅ 自动目录创建 | Automatic directory creation
- ✅ 错误处理和用户提示 | Error handling and user prompts
- ✅ 缓存系统性能优化 | Cache system performance optimization
- ✅ 多层缓存架构验证 | Multi-layer cache architecture validation
- ✅ 缓存一致性测试 | Cache consistency testing
- ✅ 缓存清理机制验证 | Cache cleanup mechanism validation

### 兼容性测试 | Compatibility Testing

- ✅ Windows 10/11
- ✅ Linux (Ubuntu, CentOS)
- ✅ macOS
- ✅ Python 3.8+


## 🤝 贡献者 | Contributors

感谢所有为本版本做出贡献的开发者和用户。

Thanks to all developers and users who contributed to this version.

## 📞 技术支持 | Technical Support

如果在使用过程中遇到问题，请：

If you encounter issues during use, please:

1. 查看文档 | Check documentation
2. 运行诊断脚本 | Run diagnostic scripts
3. 提交Issue | Submit an issue
4. 参与社区讨论 | Participate in community discussions

---

**完整更新日志** | Full Changelog: [GitHub Releases](https://github.com/your-repo/releases)

**下载地址** | Download: [GitHub Releases](https://github.com/your-repo/releases/tag/v0.1.4)