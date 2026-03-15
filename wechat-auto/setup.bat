@echo off
REM 企业微信自动回复系统一键安装脚本 (Windows)

echo =========================================
echo   企业微信自动回复系统安装脚本
echo =========================================

REM 检查Python版本
echo [1/6] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到python，请先安装Python 3.8+
    pause
    exit /b 1
)

python -c "import sys; print(f'  Python版本: {sys.version_info.major}.{sys.version_info.minor}')"

REM 检查虚拟环境
echo [2/6] 检查虚拟环境...
if not exist "venv" (
    echo   创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo [3/6] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo [4/6] 安装依赖包...
pip install --upgrade pip
pip install -r requirements.txt

REM 创建配置文件
echo [5/6] 创建配置文件...
if not exist "config\config.yaml" (
    if exist "config\config_template.yaml" (
        copy config\config_template.yaml config\config.yaml
        echo   配置文件已创建: config\config.yaml
        echo   请编辑此文件，填写企业微信API信息
    ) else (
        echo   警告: 配置文件模板未找到
    )
) else (
    echo   配置文件已存在
)

REM 创建数据目录
echo [6/6] 创建数据目录...
if not exist "data\documents" mkdir data\documents
if not exist "data\history" mkdir data\history
if not exist "logs" mkdir logs

echo.
echo =========================================
echo   安装完成！
echo =========================================
echo.
echo 下一步操作：
echo 1. 编辑配置文件: config\config.yaml
echo 2. 填写企业微信API信息：
echo    - corp_id ^(企业ID^)
echo    - secret ^(应用Secret^)
echo    - agent_id ^(应用ID^)
echo 3. 运行测试: python main.py
echo 4. 添加文档到: data\documents\
echo 5. 添加历史聊天记录到: data\history\
echo.
echo 企业微信API获取步骤：
echo 1. 登录企业微信管理后台
echo 2. 应用管理 → 自建应用 → 创建应用
echo 3. 获取 CorpID, Secret, AgentId
echo.
echo 如需帮助，请查看 README.md
echo =========================================
pause