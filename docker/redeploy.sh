#!/bin/bash
# vibe-blog 服务重部署脚本
# 用法: ./redeploy.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔄 开始重部署 vibe-blog 服务..."
echo "📁 项目目录: $PROJECT_DIR"

# 进入项目目录
cd "$PROJECT_DIR"

# 拉取最新代码
echo "📥 拉取最新代码..."
git pull

# 停止现有容器
echo "🛑 停止现有容器..."
docker compose -f docker/docker-compose.yml down

# 重新构建并启动
echo "🚀 重新构建并启动容器..."
docker compose -f docker/docker-compose.yml up -d --build

echo "✅ 重部署完成！"
echo ""
echo "查看日志: docker compose -f docker/docker-compose.yml logs -f"
