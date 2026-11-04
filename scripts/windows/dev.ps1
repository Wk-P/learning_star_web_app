# Windows 下替代 Makefile 的开发入口（macOS/Linux 继续用 make）
#   .\scripts\windows\dev.ps1 setup        首次：创建 topik/.venv 并安装依赖、复制 .env.develop、安装前端依赖
#   .\scripts\windows\dev.ps1 topik-api    topik 后端 :8000
#   .\scripts\windows\dev.ps1 course-api   course 后端 :8001
#   .\scripts\windows\dev.ps1 web          前端 :5173
#   .\scripts\windows\dev.ps1 all          在三个新窗口里同时启动以上三个
#   .\scripts\windows\dev.ps1 build        构建前端
#   .\scripts\windows\dev.ps1 images       重新生成 web/public 图片
param([Parameter(Position = 0)][string]$Task = '')

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$VenvPy = Join-Path $Root 'topik\.venv\Scripts\python.exe'

function Run-TopikApi {
    if (-not (Test-Path $VenvPy)) { throw '缺少 topik\.venv，请先运行 .\scripts\windows\dev.ps1 setup' }
    Set-Location (Join-Path $Root 'topik\backend')
    & $VenvPy manage.py runserver 8000
}
function Run-CourseApi {
    Set-Location (Join-Path $Root 'course')
    uv run python backend/manage.py runserver 8001
}
function Run-Web {
    Set-Location (Join-Path $Root 'web')
    pnpm dev
}

switch ($Task) {
    'setup' {
        if (-not (Test-Path $VenvPy)) { uv venv (Join-Path $Root 'topik\.venv') }
        uv pip install --python $VenvPy -r (Join-Path $Root 'topik\requirements.txt')
        $envDev = Join-Path $Root 'topik\backend\.env.develop'
        if (-not (Test-Path $envDev)) { Copy-Item "$envDev.example" $envDev; Write-Host '已生成 topik\backend\.env.develop，按需修改' }
        Push-Location (Join-Path $Root 'course'); uv sync; Pop-Location
        Push-Location (Join-Path $Root 'web'); pnpm install; Pop-Location
    }
    'topik-api'  { Run-TopikApi }
    'course-api' { Run-CourseApi }
    'web'        { Run-Web }
    'all' {
        foreach ($t in 'topik-api', 'course-api', 'web') {
            Start-Process powershell -ArgumentList '-NoExit', '-ExecutionPolicy', 'Bypass', '-File', "`"$PSCommandPath`"", $t
        }
    }
    'build'  { Set-Location (Join-Path $Root 'web'); pnpm run build }
    'images' { Set-Location $Root; uv run scripts/optimize_images.py }
    default  { Get-Content $PSCommandPath -TotalCount 8 | Select-Object -Skip 1; exit 1 }
}
