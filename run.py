#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from app import create_app

# 创建Flask应用实例
app = create_app(os.getenv('FLASK_ENV', 'default'))

if __name__ == '__main__':
    # 开发环境下运行
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )