# Windows 本地开发入口（macOS / Linux 用 scripts/unix/dev.sh 或 make）
#   .\scripts\windows\dev.ps1 setup        首次：安装两个后端（uv sync）与前端依赖，生成 .env.develop，迁移本地数据库
#   .\scripts\windows\dev.ps1 migrate      两个后端执行数据库迁移（拉取新代码后出现 unapplied migrations 提示时）
#   .\scripts\windows\dev.ps1 info         显示本地访问地址与测试账号
#   .\scripts\windows\dev.ps1 all       在三个新窗口里分别启动下面三个服务
#   .\scripts\windows\dev.ps1 topik-api    topik 后端 :8000
#   .\scripts\windows\dev.ps1 course-api   course 后端 :8001
#   .\scripts\windows\dev.ps1 web          前端 :5173（代理 /api/topik、/api/course、/media）
#   .\scripts\windows\dev.ps1 build        构建前端
#   .\scripts\windows\dev.ps1 images       由 images\src 重新生成 web\public 图片
#
# 依赖：uv（winget install astral-sh.uv）、Node ^20.19 或 >=22.12、pnpm（corepack enable）
param([Parameter(Position = 0)][string]$Task = '')

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

# 与 Linux 服务器一致：Python 读写文件、标准输出一律 UTF-8（Windows 默认是 GBK/cp936）
$env:PYTHONUTF8 = '1'

# 打印文件开头的注释块（到第一个非注释行为止）。不带参数是正常查看帮助（退出码 0），命令写错才算失败
function Show-Usage {
    if ($Task) { Write-Host "未知命令：$Task" -ForegroundColor Red; Write-Host '' }
    $lines = Get-Content -Encoding UTF8 $PSCommandPath
    for ($i = 0; $i -lt $lines.Count -and $lines[$i] -match '^#'; $i++) { $lines[$i] -replace '^# ?', '' }
    if ($Task) { exit 1 } else { exit 0 }
}

function Require([string]$Cmd, [string]$Hint) {
    if (-not (Get-Command $Cmd -ErrorAction SilentlyContinue)) { throw "缺少 ${Cmd}：$Hint" }
}

# 在 $Dir 下运行一个原生命令；结束后回到原目录，退出码非 0 时报错
# （PowerShell 5.1 的 $ErrorActionPreference 管不到原生命令的退出码）
function Exec([string]$Dir, [string]$Exe, [string[]]$CmdArgs) {
    # 只以退出码判断成败：5.1 在 Stop 模式下会把原生命令写到 stderr 的普通提示也当成错误
    $ErrorActionPreference = 'Continue'
    Push-Location $Dir
    try {
        $global:LASTEXITCODE = 0
        & $Exe @CmdArgs
        if ($LASTEXITCODE -ne 0) { throw "$Exe $($CmdArgs -join ' ') 失败（退出码 $LASTEXITCODE）" }
    } finally {
        Pop-Location
    }
}

$EnvDev = Join-Path $Root 'topik\backend\.env.develop'

# 读取 .env.develop 中的值；缺省值与 create_admin 命令一致
function Get-EnvDev([string]$Key, [string]$Default) {
    if (Test-Path $EnvDev) {
        $line = Get-Content -Encoding UTF8 $EnvDev | Where-Object { $_ -match "^$Key=" } | Select-Object -Last 1
        if ($line) { $v = ($line -replace "^$Key=", '').Trim(); if ($v) { return $v } }
    }
    return $Default
}

function Show-Info {
    $user = Get-EnvDev 'ADMIN_USERNAME' 'admin'
    $pass = Get-EnvDev 'ADMIN_PASSWORD' 'admin123'
    $bar = '─' * 56
    Write-Host $bar -ForegroundColor DarkGray
    Write-Host ' 前端        http://localhost:5173'
    Write-Host ' 登录页      http://localhost:5173/login'
    Write-Host ' 管理后台    http://localhost:5173/admin'
    Write-Host ' topik API   http://localhost:8000      course API  http://localhost:8001'
    Write-Host ''
    Write-Host ' 本地测试账号（管理员）' -ForegroundColor Cyan
    Write-Host "   用户名    $user" -ForegroundColor Yellow
    Write-Host "   密码      $pass" -ForegroundColor Yellow
    Write-Host '   来源      topik\backend\.env.develop 的 ADMIN_USERNAME / ADMIN_PASSWORD'
    Write-Host "   改密码    cd topik\backend; uv run python manage.py changepassword $user"
    Write-Host '             （setup 只在账号不存在时创建，不会覆盖已有账号的密码）'
    Write-Host $bar -ForegroundColor DarkGray
}

# 只作用于本地开发数据库（两个后端各自的 db.sqlite3，不进 git）
function Invoke-Migrate {
    Write-Host '▶ topik 数据库迁移'
    Exec (Join-Path $Root 'topik\backend') uv @('run', 'python', 'manage.py', 'migrate')
    Write-Host '▶ course 数据库迁移'
    Exec (Join-Path $Root 'course') uv @('run', 'python', 'backend/manage.py', 'migrate')
}

switch ($Task) {
    'setup' {
        Require uv 'winget install astral-sh.uv'
        Require pnpm 'corepack enable 或 npm i -g pnpm'
        # 两个后端都是 uv 项目：各自的 .venv 由 uv sync 按 uv.lock 创建（topik 为 Python 3.10，course 为 3.13）
        Exec (Join-Path $Root 'topik') uv @('sync')
        if (-not (Test-Path $EnvDev)) {
            Copy-Item "$EnvDev.example" $EnvDev
            Write-Host '已生成 topik\backend\.env.develop，按需修改'
        }
        Exec (Join-Path $Root 'course') uv @('sync')
        Exec (Join-Path $Root 'web') pnpm @('install')
        Invoke-Migrate
        Write-Host '▶ 创建本地测试账号'
        Exec (Join-Path $Root 'topik\backend') uv @('run', 'python', 'manage.py', 'create_admin')
        Write-Host ''
        Write-Host '✔ 完成。启动：.\scripts\windows\dev.ps1 all' -ForegroundColor Green
        Show-Info
    }
    'migrate' { Invoke-Migrate }
    'info'    { Show-Info }
    'all' {
        foreach ($t in 'topik-api', 'course-api', 'web') {
            Start-Process powershell -ArgumentList @(
                '-NoExit', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`"", $t)
        }
        Write-Host '已在三个新窗口中启动 topik-api / course-api / web，关闭窗口或 Ctrl-C 即停止' -ForegroundColor Green
        Show-Info
    }
    'topik-api' {
        $Host.UI.RawUI.WindowTitle = 'topik-api :8000'
        Exec (Join-Path $Root 'topik\backend') uv @('run', 'python', 'manage.py', 'runserver', '8000')
    }
    'course-api' {
        $Host.UI.RawUI.WindowTitle = 'course-api :8001'
        Exec (Join-Path $Root 'course') uv @('run', 'python', 'backend/manage.py', 'runserver', '8001')
    }
    'web' {
        $Host.UI.RawUI.WindowTitle = 'web :5173'
        Exec (Join-Path $Root 'web') pnpm @('dev')
    }
    'build'  { Exec (Join-Path $Root 'web') pnpm @('run', 'build') }
    'images' { Exec $Root uv @('run', 'scripts/optimize_images.py') }
    default  { Show-Usage }
}
