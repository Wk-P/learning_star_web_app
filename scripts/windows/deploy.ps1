# Windows 部署入口：deploy.sh 依赖 bash + rsync，这里通过 WSL 调用 scripts/unix/deploy.sh
#   .\scripts\windows\deploy.ps1 web | topik | course | nginx | pull-data | push-data | users [--apply] | all
# 前提：已安装 WSL（wsl --install），并在 WSL 内装好 rsync、openssh-client、node、pnpm；
#       deploy/.env 里的 SSH_KEY 写 WSL 内可访问的路径（如 /mnt/c/Users/你/.ssh/id_ed25519，或复制到 ~/.ssh）
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
if (-not (Get-Command wsl -ErrorAction SilentlyContinue)) { throw '未找到 wsl，请先 wsl --install' }
$wslRoot = (wsl wslpath -a ($Root -replace '\', '/')).Trim()
wsl bash -c "cd '$wslRoot' && ./scripts/unix/deploy.sh $($args -join ' ')"
exit $LASTEXITCODE
