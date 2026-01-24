# ============================================================================
# 完整系统启动脚本
# 按正确顺序启动所有必需服务：PostgreSQL → Redis → Celery → 后端 → 前端
# 配置来源：.env 文件（统一配置管理）
# ============================================================================

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  启动外贸CRM自动化系统" -ForegroundColor Cyan  
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# 检查.env文件是否存在
if (-not (Test-Path "$PSScriptRoot\.env")) {
    Write-Host "❌ .env文件不存在！" -ForegroundColor Red
    Write-Host "   请复制 .env.example 为 .env 并配置实际值" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ 检测到 .env 配置文件" -ForegroundColor Green
Write-Host ""

# 步骤1: 检查PostgreSQL (5432)
Write-Host "[1/5] 检查PostgreSQL..." -ForegroundColor Yellow
$pgPort = netstat -an | Select-String "0.0.0.0:5432.*LISTENING"
if ($pgPort) {
    Write-Host "  ✅ PostgreSQL已运行 (端口5432)" -ForegroundColor Green
} else {
    Write-Host "  ❌ PostgreSQL未运行，请手动启动" -ForegroundColor Red
    Write-Host "     命令: & 'D:\Program Files\PostgreSQL\15\bin\pg_ctl.exe' start -D 'D:\Program Files\PostgreSQL\15\data'" -ForegroundColor Gray
    exit 1
}

# 步骤2: 启动Redis (Memurai)  
Write-Host "`n[2/5] 启动Redis (Memurai)..." -ForegroundColor Yellow
$redisPort = netstat -an | Select-String "0.0.0.0:6379.*LISTENING"
if ($redisPort) {
    Write-Host "  ✅ Redis已运行 (端口6379)" -ForegroundColor Green
} else {
    Write-Host "  🚀 正在启动Memurai..." -ForegroundColor Cyan
    Start-Process -FilePath "C:\Program Files\Memurai\memurai.exe" -WindowStyle Minimized
    Start-Sleep -Seconds 3
    
    $redisPort = netstat -an | Select-String "0.0.0.0:6379.*LISTENING"
    if ($redisPort) {
        Write-Host "  ✅ Memurai启动成功 (端口6379)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Memurai启动失败" -ForegroundColor Red
        exit 1
    }
}

# 步骤3: 启动Celery Worker
Write-Host "`n[3/5] 启动Celery Worker..." -ForegroundColor Yellow
$celeryProcess = Get-Process -Name "celery" -ErrorAction SilentlyContinue
if ($celeryProcess) {
    Write-Host "  ✅ Celery Worker已运行" -ForegroundColor Green
} else {
    Write-Host "  🚀 正在启动Celery Worker..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot' ; .\.venv\Scripts\celery.exe -A src.celery_config worker --loglevel=info --pool=solo"
    Start-Sleep -Seconds 5
    Write-Host "  ✅ Celery Worker已启动（请查看新窗口确认）" -ForegroundColor Green
}

# 步骤4: 启动后端API (8001)
Write-Host "`n[4/5] 启动后端API..." -ForegroundColor Yellow
$backendPort = netstat -an | Select-String "0.0.0.0:8001.*LISTENING"
if ($backendPort) {
    Write-Host "  ✅ 后端API已运行 (端口8001)" -ForegroundColor Green
} else {
    Write-Host "  🚀 正在启动后端API..." -ForegroundColor Cyan
    if (Test-Path "$PSScriptRoot\start_backend.ps1") {
        Start-Process powershell -ArgumentList "-NoExit", "-File", "$PSScriptRoot\start_backend.ps1"
    } else {
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot' ; `$env:DB_TYPE='postgresql' ; .\.venv\Scripts\python.exe -m uvicorn src.api.main:app --host 0.0.0.0 --port 8001 --reload"
    }
    Start-Sleep -Seconds 5
    
    $backendPort = netstat -an | Select-String "0.0.0.0:8001.*LISTENING"
    if ($backendPort) {
        Write-Host "  ✅ 后端API启动成功 (端口8001)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  后端API可能仍在启动中..." -ForegroundColor Yellow
    }
}

# 步骤5: 启动前端 (5173)
Write-Host "`n[5/5] 启动前端..." -ForegroundColor Yellow
$frontendPort = netstat -an | Select-String "127.0.0.1:5173.*LISTENING"
if ($frontendPort) {
    Write-Host "  ✅ 前端已运行 (端口5173)" -ForegroundColor Green
} else {
    Write-Host "  🚀 正在启动前端..." -ForegroundColor Cyan
    if (Test-Path "$PSScriptRoot\start_frontend.ps1") {
        Start-Process powershell -ArgumentList "-NoExit", "-File", "$PSScriptRoot\start_frontend.ps1"
    } else {
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend' ; npm run dev"
    }
    Start-Sleep -Seconds 5
    Write-Host "  ✅ 前端已启动（请查看新窗口确认）" -ForegroundColor Green
}

# 最终状态检查
Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "  系统启动完成！" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "服务状态检查：" -ForegroundColor White
Write-Host "  PostgreSQL (5432): " -NoNewline
if (netstat -an | Select-String "0.0.0.0:5432.*LISTENING") { Write-Host "✅ 运行中" -ForegroundColor Green } else { Write-Host "❌ 未运行" -ForegroundColor Red }

Write-Host "  Redis (6379):      " -NoNewline
if (netstat -an | Select-String "0.0.0.0:6379.*LISTENING") { Write-Host "✅ 运行中" -ForegroundColor Green } else { Write-Host "❌ 未运行" -ForegroundColor Red }

Write-Host "  后端API (8001):    " -NoNewline
if (netstat -an | Select-String "0.0.0.0:8001.*LISTENING") { Write-Host "✅ 运行中" -ForegroundColor Green } else { Write-Host "❌ 未运行" -ForegroundColor Red }

Write-Host "  前端 (5173):       " -NoNewline
if (netstat -an | Select-String "127.0.0.1:5173.*LISTENING") { Write-Host "✅ 运行中" -ForegroundColor Green } else { Write-Host "❌ 未运行" -ForegroundColor Red }

Write-Host "  Celery Worker:     " -NoNewline
if (Get-Process -Name "celery" -ErrorAction SilentlyContinue) { Write-Host "✅ 运行中" -ForegroundColor Green } else { Write-Host "⚠️  未检测到" -ForegroundColor Yellow }

Write-Host ""
Write-Host "访问地址：" -ForegroundColor White
Write-Host "  前端: http://localhost:5173" -ForegroundColor Cyan
Write-Host "  API:  http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "按任意键退出..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
