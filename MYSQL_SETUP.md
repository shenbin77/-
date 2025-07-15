# MySQL数据库配置指南

## 📋 前提条件

1. **安装MySQL服务器**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install mysql-server
   
   # CentOS/RHEL
   sudo yum install mysql-server
   
   # Windows: 下载MySQL安装包
   # https://dev.mysql.com/downloads/mysql/
   ```

2. **安装Python MySQL驱动**
   ```bash
   pip install pymysql
   ```

## 🔧 配置步骤

### 方法1: 使用数据库切换工具（推荐）

```bash
# 1. 切换到MySQL并创建数据库
python switch_database.py mysql --create-db --init-tables --password=your_mysql_password

# 2. 重启应用
python run.py
```

### 方法2: 手动配置

1. **创建数据库**
   ```sql
   CREATE DATABASE stock_analysis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. **修改配置文件**
   编辑 `config_simple.py`：
   ```python
   # 注释SQLite配置
   # SQLALCHEMY_DATABASE_URI = 'sqlite:///stock_analysis.db'
   
   # 启用MySQL配置
   SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:your_password@localhost/stock_analysis?charset=utf8mb4'
   ```

3. **初始化数据库表**
   ```bash
   python -c "from app import create_app; from app.extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
   ```

4. **导入示例数据**
   ```bash
   python simple_init_data.py
   ```

## 🔍 验证配置

```bash
# 检查当前数据库配置
python switch_database.py

# 测试数据库连接
python test_database_query.py
```

## 📊 数据库对比

| 特性 | SQLite | MySQL |
|------|--------|-------|
| 安装复杂度 | 简单 | 中等 |
| 性能 | 适合小型应用 | 适合大型应用 |
| 并发支持 | 有限 | 优秀 |
| 数据类型 | 基础 | 丰富 |
| 备份恢复 | 文件复制 | 专业工具 |
| 推荐场景 | 开发/演示 | 生产环境 |

## 🚨 常见问题

1. **连接被拒绝**
   - 检查MySQL服务是否启动
   - 验证用户名和密码
   - 确认防火墙设置

2. **字符编码问题**
   - 确保数据库使用utf8mb4字符集
   - 连接字符串包含charset=utf8mb4

3. **权限问题**
   ```sql
   GRANT ALL PRIVILEGES ON stock_analysis.* TO 'root'@'localhost';
   FLUSH PRIVILEGES;
   ```

## 💡 性能优化建议

1. **MySQL配置优化**
   ```ini
   # my.cnf
   [mysqld]
   innodb_buffer_pool_size = 1G
   innodb_log_file_size = 256M
   max_connections = 200
   ```

2. **应用层优化**
   - 使用连接池
   - 添加适当的索引
   - 定期清理历史数据
