# ClickHouse Docker 启动脚本 (Windows PowerShell)
# 包络分析系统专用

Write-Host "启动 ClickHouse 容器..." -ForegroundColor Green

# 创建数据目录
if (!(Test-Path ".\clickhouse_data")) {
    New-Item -ItemType Directory -Path ".\clickhouse_data" | Out-Null
}
if (!(Test-Path ".\clickhouse_logs")) {
    New-Item -ItemType Directory -Path ".\clickhouse_logs" | Out-Null
}

# 停止并删除已存在的容器（如果有）
Write-Host "清理已存在的容器..." -ForegroundColor Yellow
docker stop clickhouse-baoluo 2>$null
docker rm clickhouse-baoluo 2>$null

# 启动 ClickHouse 容器
Write-Host "启动 ClickHouse 容器..." -ForegroundColor Green
docker run -d `
  --name clickhouse-baoluo `
  --restart unless-stopped `
  -p 8123:8123 `
  -p 9000:9000 `
  -p 9440:9440 `
  -v "${PWD}\clickhouse_data:/var/lib/clickhouse" `
  -v "${PWD}\clickhouse_logs:/var/log/clickhouse-server" `
  -e CLICKHOUSE_DB=baoluo `
  -e CLICKHOUSE_USER=root `
  -e CLICKHOUSE_PASSWORD=123456 `
  -e CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1 `
  --ulimit nofile=262144:262144 `
  clickhouse/clickhouse-server:latest

if ($LASTEXITCODE -eq 0) {
    Write-Host "容器启动命令执行成功" -ForegroundColor Green
} else {
    Write-Host "容器启动命令执行失败" -ForegroundColor Red
    exit 1
}

# 等待容器启动
Write-Host "等待 ClickHouse 启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# 检查容器状态
$containerStatus = docker ps --filter "name=clickhouse-baoluo" --format "{{.Status}}"
if ($containerStatus) {
    Write-Host "✅ ClickHouse 容器启动成功!" -ForegroundColor Green
    Write-Host ""
    Write-Host "连接信息:" -ForegroundColor Cyan
    Write-Host "  HTTP 端口: 8123" -ForegroundColor White
    Write-Host "  TCP 端口: 9000" -ForegroundColor White
    Write-Host "  用户名: root" -ForegroundColor White
    Write-Host "  密码: 123456" -ForegroundColor White
    Write-Host "  数据库: baoluo" -ForegroundColor White
    Write-Host ""
    Write-Host "测试连接:" -ForegroundColor Cyan
    Write-Host "  PowerShell: Invoke-RestMethod 'http://localhost:8123/ping'" -ForegroundColor White
    Write-Host "  浏览器: http://localhost:8123/play" -ForegroundColor White
    Write-Host ""
    
    # 测试连接
    Write-Host "测试连接中..." -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri 'http://localhost:8123/ping' -TimeoutSec 5
        if ($response -eq "Ok.") {
            Write-Host "✅ ClickHouse 连接测试成功!" -ForegroundColor Green
            
            # 创建数据库
            Write-Host "创建数据库 baoluo..." -ForegroundColor Yellow
            $headers = @{
                'X-ClickHouse-User' = 'root'
                'X-ClickHouse-Key' = '123456'
            }
            try {
                Invoke-RestMethod -Uri 'http://localhost:8123/' -Method Post -Body 'CREATE DATABASE IF NOT EXISTS baoluo' -Headers $headers
                Write-Host "✅ 数据库创建完成!" -ForegroundColor Green
            } catch {
                Write-Host "⚠️ 数据库创建可能失败: $($_.Exception.Message)" -ForegroundColor Yellow
            }
        } else {
            Write-Host "❌ ClickHouse 连接失败，响应: $response" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ ClickHouse 连接失败: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "请检查容器是否正常运行: docker logs clickhouse-baoluo" -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ ClickHouse 容器启动失败!" -ForegroundColor Red
    Write-Host "查看日志: docker logs clickhouse-baoluo" -ForegroundColor Yellow
    Write-Host "检查端口占用: netstat -an | findstr ':8123'" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "常用命令:" -ForegroundColor Cyan
Write-Host "  查看容器状态: docker ps | findstr clickhouse" -ForegroundColor White
Write-Host "  查看容器日志: docker logs clickhouse-baoluo" -ForegroundColor White
Write-Host "  停止容器: docker stop clickhouse-baoluo" -ForegroundColor White
Write-Host "  重启容器: docker restart clickhouse-baoluo" -ForegroundColor White
