from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# 数据库实例
db = SQLAlchemy()
migrate = Migrate()

# SocketIO实例 (暂时禁用)
socketio = None

# Redis实例 (暂时禁用)
redis_client = None