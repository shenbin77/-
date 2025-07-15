#!/usr/bin/env python3
"""
TradingAgents-CN API服务启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖项"""
    try:
        import fastapi
        import uvicorn
        print("✅ FastAPI 和 Uvicorn 已安装")
    except ImportError:
        print("❌ 缺少依赖项，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn[standard]"])
        print("✅ 依赖项安装完成")

def check_env_config():
    """检查环境配置"""
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists():
        print("⚠️  未找到 .env 文件，请确保已配置API密钥")
        print("   请参考 README 文档配置相应的LLM API密钥")
        return False
    
    # 检查常用的API密钥
    required_keys = [
        "DASHSCOPE_API_KEY",  # 阿里百炼
        "OPENAI_API_KEY",     # OpenAI
        "GOOGLE_API_KEY",     # Google AI
    ]
    
    found_keys = []
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
        for key in required_keys:
            if key in content and not content.split(key + "=")[1].split('\n')[0].strip() == "":
                found_keys.append(key)
    
    if found_keys:
        print(f"✅ 找到配置的API密钥: {', '.join(found_keys)}")
        return True
    else:
        print("⚠️  未找到有效的API密钥配置")
        return False

def start_service():
    """启动API服务"""
    print("🚀 启动 TradingAgents-CN API 服务...")
    print("📡 服务地址: http://localhost:8000")
    print("📖 API文档: http://localhost:8000/docs")
    print("🔧 健康检查: http://localhost:8000/health")
    print("\n按 Ctrl+C 停止服务\n")
    
    try:
        # 启动uvicorn服务
        os.system("python -m uvicorn api_service:app --host 0.0.0.0 --port 8000 --reload")
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 TradingAgents-CN API 服务启动器")
    print("=" * 60)
    
    # 检查依赖
    check_dependencies()
    
    # 检查环境配置
    env_configured = check_env_config()
    
    if not env_configured:
        print("\n⚠️  建议配置API密钥后再启动服务")
        response = input("是否继续启动服务？(y/N): ")
        if response.lower() != 'y':
            print("👋 退出启动")
            sys.exit(0)
    
    print("\n" + "=" * 60)
    
    # 启动服务
    start_service()
