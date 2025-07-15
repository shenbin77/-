# TradingAgents-CN Web应用启动脚本

Write-Host "🚀 启动TradingAgents-CN Web应用..." -ForegroundColor Green
Write-Host ""

# 激活虚拟环境
& ".\env\Scripts\Activate.ps1"

# 启动Streamlit应用
python -m streamlit run web/app.py --server.port 8501 --server.address localhost

Write-Host "按任意键退出..." -ForegroundColor Yellow
Read-Host
