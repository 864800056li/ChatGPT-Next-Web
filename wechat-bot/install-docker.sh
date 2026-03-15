#!/bin/bash
# install-docker-macos.sh - 自动安装 Docker Desktop for Mac

echo "🐳 开始安装 Docker Desktop..."

# 检查是否已安装
if [ -d "/Applications/Docker.app" ]; then
    echo "✅ Docker Desktop 已安装"
    open -a Docker
    echo "🚀 正在启动 Docker..."
    sleep 10
    exit 0
fi

# 创建临时目录
TMP_DIR=$(mktemp -d)
cd "$TMP_DIR"

# 下载 Docker Desktop (Apple Silicon) - 使用国内镜像
echo "⬇️  下载 Docker Desktop..."
curl -L -o Docker.dmg "https://desktop.docker.com/mac/main/arm64/Docker.dmg" --retry 3 --retry-delay 5 || {
    echo "官方源失败，尝试备用源..."
    curl -L -o Docker.dmg "https://mirrors.aliyun.com/docker-toolbox/mac/docker-for-mac/stable/Docker.dmg" --retry 3
}

# 挂载 DMG
echo "📦 挂载安装包..."
hdiutil attach Docker.dmg -nobrowse

# 复制到 Applications
echo "📋 安装到 Applications..."
cp -R "/Volumes/Docker/Docker.app" /Applications/

# 卸载 DMG
hdiutil detach "/Volumes/Docker"

# 清理
rm -rf "$TMP_DIR"

# 启动 Docker
echo "🚀 启动 Docker Desktop..."
open -a Docker

# 等待启动
echo "⏳ 等待 Docker 启动 (约 30 秒)..."
sleep 30

# 验证
docker --version && echo "✅ Docker 安装成功！" || echo "❌ Docker 启动失败，请手动检查"
