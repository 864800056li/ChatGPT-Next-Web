#!/bin/bash
# 企业微信自动回复系统一键安装脚本

set -e

echo "========================================="
echo "  企业微信自动回复系统安装脚本"
echo "========================================="

# 检查Python版本
echo "[1/6] 检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到python3，请先安装Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "  Python版本: $PYTHON_VERSION"

# 检查虚拟环境
echo "[2/6] 检查虚拟环境..."
if [ ! -d "venv" ]; then
    echo "  创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "[3/6] 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "[4/6] 安装依赖包..."
pip install --upgrade pip
pip install -r requirements.txt

# 创建配置文件
echo "[5/6] 创建配置文件..."
if [ ! -f "config/config.yaml" ]; then
    if [ -f "config/config_template.yaml" ]; then
        cp config/config_template.yaml config/config.yaml
        echo "  配置文件已创建: config/config.yaml"
        echo "  请编辑此文件，填写企业微信API信息"
    else
        echo "  警告: 配置文件模板未找到"
    fi
else
    echo "  配置文件已存在"
fi

# 创建数据目录
echo "[6/6] 创建数据目录..."
mkdir -p data/documents data/history logs

# 设置文件权限
chmod +x main.py

echo ""
echo "========================================="
echo "  安装完成！"
echo "========================================="
echo ""
echo "下一步操作："
echo "1. 编辑配置文件: vi config/config.yaml"
echo "2. 填写企业微信API信息："
echo "   - corp_id (企业ID)"
echo "   - secret (应用Secret)"
echo "   - agent_id (应用ID)"
echo "3. 运行测试: python main.py"
echo "4. 添加文档到: data/documents/"
echo "5. 添加历史聊天记录到: data/history/"
echo ""
echo "企业微信API获取步骤："
echo "1. 登录企业微信管理后台"
echo "2. 应用管理 → 自建应用 → 创建应用"
echo "3. 获取 CorpID, Secret, AgentId"
echo ""
echo "如需帮助，请查看 README.md"
echo "========================================="