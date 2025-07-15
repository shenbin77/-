import os
from datetime import timedelta

class Config:
    """简化配置类 - 用于演示"""
    
    # 数据库配置 - 可以选择SQLite或MySQL

    # 选项1: SQLite数据库 (默认，适合开发和演示)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///stock_analysis.db'

    # 选项2: MySQL数据库 (适合生产环境)
    # 请先创建数据库: CREATE DATABASE stock_analysis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:your_password@localhost/stock_analysis?charset=utf8mb4'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask配置
    SECRET_KEY = 'demo-secret-key-for-testing'
    DEBUG = True
    
    # Redis配置 (暂时禁用)
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 0
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/stock_analysis.log'
    
    # 数据更新配置
    DATA_UPDATE_HOUR = 18
    DATA_UPDATE_MINUTE = 0
    
    # 预警配置
    EMAIL_SMTP_SERVER = 'smtp.qq.com'
    EMAIL_SMTP_PORT = 587
    EMAIL_USERNAME = ''
    EMAIL_PASSWORD = ''
    
    # 分页配置
    ITEMS_PER_PAGE = 20
    MAX_ITEMS_PER_PAGE = 100
    
    # API配置
    API_RATE_LIMIT = '1000 per hour'
    
    # 缓存配置
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    
    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # CORS配置
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    # WebSocket配置
    SOCKETIO_ASYNC_MODE = 'eventlet'
    
    # 数据源配置
    TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN', '')
    AKSHARE_ENABLED = True
    
    # AI分析配置
    AI_SERVICE_URL = 'http://localhost:8000'
    AI_SERVICE_TIMEOUT = 300
    
    # 实时数据配置
    REALTIME_UPDATE_INTERVAL = 5  # 秒
    REALTIME_CACHE_TTL = 60  # 秒
    
    # 回测配置
    BACKTEST_MAX_STOCKS = 50
    BACKTEST_MAX_DAYS = 1000
    
    # 因子配置
    FACTOR_UPDATE_INTERVAL = 24  # 小时
    FACTOR_CACHE_TTL = 3600  # 秒
    
    # 模型配置
    ML_MODEL_CACHE_TTL = 7200  # 秒
    ML_MAX_FEATURES = 100
    
    # 监控配置
    MONITOR_ENABLED = True
    MONITOR_INTERVAL = 60  # 秒
    
    # 安全配置
    WTF_CSRF_ENABLED = False  # 简化演示，生产环境应启用
    WTF_CSRF_TIME_LIMIT = None
    
    # 数据库连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    # 生产环境应使用更安全的配置

# 配置字典
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
