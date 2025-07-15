#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from flask import Flask, render_template, jsonify
from flask_cors import CORS
try:
    from config_simple import config
except ImportError:
    from config import config
from app.extensions import db

def create_simple_app():
    """创建简化的Flask应用"""
    app = Flask(__name__, template_folder='app/templates', static_folder='app/static')
    
    # 加载配置
    app.config.from_object(config['development'])
    
    # 初始化扩展
    db.init_app(app)
    CORS(app)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    # 简单的路由
    @app.route('/')
    def index():
        # 重定向到AI决策驾驶舱
        return render_template('ai_dashboard.html')

    @app.route('/dashboard')
    def ai_dashboard():
        return render_template('ai_dashboard.html')

    @app.route('/stock/<stock_code>')
    def stock_detail(stock_code):
        return render_template('stock_detail.html', stock_code=stock_code)
    
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok', 'message': 'Application is running'})
    
    @app.route('/api/stocks')
    def stocks():
        # 返回一些示例股票数据
        sample_stocks = [
            {'ts_code': '000001.SZ', 'name': '平安银行', 'industry': '银行'},
            {'ts_code': '000002.SZ', 'name': '万科A', 'industry': '房地产'},
            {'ts_code': '600519.SH', 'name': '贵州茅台', 'industry': '食品饮料'},
            {'ts_code': '000858.SZ', 'name': '五粮液', 'industry': '食品饮料'},
            {'ts_code': '300750.SZ', 'name': '宁德时代', 'industry': '电池'},
        ]
        return jsonify({'success': True, 'data': sample_stocks})
    
    return app

if __name__ == '__main__':
    app = create_simple_app()
    print("🚀 启动简化版量化分析平台...")
    print("📡 访问地址: http://localhost:5001")
    print("📖 健康检查: http://localhost:5001/api/health")
    print("📊 股票列表: http://localhost:5001/api/stocks")
    print("\n按 Ctrl+C 停止服务\n")
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )
