# Windows 部署入口：用 Git for Windows 自带的 bash 运行 scripts/unix/deploy.sh（不需要 WSL）
#   .\scripts\windows\deploy.ps1 web | topik | course | nginx | pull-data | push-data | users [--apply] | all
#
# Git Bash 没有 rsync，deploy.sh 会自动改用 tar + ssh 全量上传，效果相同。
# deploy/.env 中 SSH_KEY 可写 C:\Users\你\.ssh\key、C:/Users/你/.ssh/key 或 ~/.ssh/key
$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

# 找 Git for Windows 的 bash（不能用 PATH 里的 bash.exe：那可能是 WSL 的启动器）
$git = Get-Command git -ErrorAction SilentlyContinue
if (-not $git) { throw '需要 Git for Windows：winget install Git.Git' }
# git --exec-path 形如 C:/Program Files/Git/mingw64/libexec/git-core，往上三级是 Git 安装目录
$gitRoot = Split-Path (Split-Path (Split-Path (& git --exec-path)))
$bash = Join-Path $gitRoot 'bin\bash.exe'
if (-not (Test-Path $bash)) { throw "找不到 Git Bash：$bash" }

$script = (Join-Path $Root 'scripts\unix\deploy.sh') -replace '\\', '/'

# bash 输出 UTF-8，临时切换控制台编码以免中文乱码
$prevEncoding = [Console]::OutputEncoding
[Console]::OutputEncoding = [Text.Encoding]::UTF8
# 成败只看退出码：5.1 在 Stop 模式下会把 stderr 上的普通提示（如 vite 警告）当成错误
$ErrorActionPreference = 'Continue'
try {
    & $bash $script @args
    $code = $LASTEXITCODE
} finally {
    [Console]::OutputEncoding = $prevEncoding
}
exit $code
