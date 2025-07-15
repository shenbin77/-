@echo off
echo 🚀 启动TradingAgents-CN Web应用...
echo.

REM 激活虚拟环境
call env\Scripts\activate.bat

REM 启动Streamlit应用
python -m streamlit run web/app.py --server.port 8501 --server.address localhost

pause
