@echo off
REM 在现有虚拟环境中安装数据库相关包

echo 🔧 在虚拟环境中安装数据库包
echo ============================

echo 📍 项目目录: %CD%

REM 检查虚拟环境
if not exist "env\Scripts\python.exe" (
    echo ❌ 虚拟环境不存在
    pause
    exit /b 1
)

echo ✅ 找到虚拟环境: env\

echo.
echo 📦 使用清华镜像安装包...

REM 使用虚拟环境的python直接安装
echo 📥 安装pymongo...
env\Scripts\python.exe -m pip install pymongo -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn

echo.
echo 📥 安装redis...
env\Scripts\python.exe -m pip install redis -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn

echo.
echo 🧪 测试安装结果...
env\Scripts\python.exe -c "
try:
    import pymongo
    print('✅ pymongo 安装成功')
except ImportError:
    print('❌ pymongo 安装失败')

try:
    import redis
    print('✅ redis 安装成功')
except ImportError:
    print('❌ redis 安装失败')
"

echo.
echo ✅ 安装完成!
echo.
echo 🎯 下一步:
echo 1. 运行系统初始化: env\Scripts\python.exe scripts\setup\initialize_system.py
echo 2. 检查系统状态: env\Scripts\python.exe scripts\validation\check_system_status.py
echo.

pause
