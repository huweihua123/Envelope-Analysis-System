#!/bin/bash

# ClickHouse Docker 启动脚本
# 包络分析系统专用

echo "启动 ClickHouse 容器..."

# 创建数据目录
mkdir -p ./clickhouse_data
mkdir -p ./clickhouse_logs

# 停止并删除已存在的容器（如果有）
docker stop clickhouse-baoluo 2>/dev/null || true
docker rm clickhouse-baoluo 2>/dev/null || true

# 启动 ClickHouse 容器
docker run -d \
  --name clickhouse-baoluo \
  --restart unless-stopped \
  -p 8123:8123 \
  -p 9000:9000 \
  -p 9440:9440 \
  -v $(pwd)/clickhouse_data:/var/lib/clickhouse \
  -v $(pwd)/clickhouse_logs:/var/log/clickhouse-server \
  -e CLICKHOUSE_DB=baoluo \
  -e CLICKHOUSE_USER=root \
  -e CLICKHOUSE_PASSWORD=123456 \
  -e CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1 \
  --ulimit nofile=262144:262144 \
  clickhouse/clickhouse-server:latest

# 等待容器启动
echo "等待 ClickHouse 启动..."
sleep 10

# 检查容器状态
if docker ps | grep -q clickhouse-baoluo; then
    echo "✅ ClickHouse 容器启动成功!"
    echo ""
    echo "连接信息:"
    echo "  HTTP 端口: 8123"
    echo "  TCP 端口: 9000" 
    echo "  用户名: root"
    echo "  密码: 123456"
    echo "  数据库: baoluo"
    echo ""
    echo "测试连接:"
    echo "  curl 'http://localhost:8123/ping'"
    echo ""
    
    # 测试连接
    echo "测试连接中..."
    if curl -s 'http://localhost:8123/ping' | grep -q "Ok."; then
        echo "✅ ClickHouse 连接测试成功!"
        
        # 创建数据库
        echo "创建数据库 baoluo..."
        curl -X POST 'http://localhost:8123/' \
          -H 'X-ClickHouse-User: root' \
          -H 'X-ClickHouse-Key: 123456' \
          -d 'CREATE DATABASE IF NOT EXISTS baoluo'
        
        echo "✅ 数据库创建完成!"
    else
        echo "❌ ClickHouse 连接失败，请检查容器状态"
    fi
else
    echo "❌ ClickHouse 容器启动失败!"
    echo "查看日志: docker logs clickhouse-baoluo"
fi
