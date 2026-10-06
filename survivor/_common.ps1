# Shared helpers for install.ps1 / run.ps1 / stop.ps1 / status.ps1.
# Works in Windows PowerShell 5.1 and PowerShell 7+.

$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
$OnWindows = ($PSVersionTable.PSEdition -eq 'Desktop') -or $IsWindows

$DataDir    = Join-Path $Root 'data'
$LogDir     = Join-Path $DataDir 'logs'
$PidFile    = Join-Path $DataDir 'survivor.pid'
$StatusFile = Join-Path $DataDir 'status.json'
$KillFile   = Join-Path $Root 'KILL'
$VenvDir    = Join-Path $Root '.venv'

function Get-VenvPython {
    if ($OnWindows) { return Join-Path (Join-Path $VenvDir 'Scripts') 'python.exe' }
    return Join-Path (Join-Path $VenvDir 'bin') 'python'
}

function Test-PythonVersion([string[]]$Cmd) {
    # Returns $true when the command runs Python 3.11 or newer.
    try {
        $exe = $Cmd[0]
        $rest = @()
        if ($Cmd.Count -gt 1) { $rest = $Cmd[1..($Cmd.Count - 1)] }
        $out = & $exe @rest -c 'import sys; print(sys.version_info[0] * 100 + sys.version_info[1])' 2>$null
        return ($LASTEXITCODE -eq 0) -and ([int]$out -ge 311)
    } catch {
        return $false
    }
}

function Find-Python {
    # The Windows "py" launcher first, then whatever is on PATH. The Microsoft Store
    # "python" stub fails the version probe, so it is skipped automatically.
    $candidates = @(@('py', '-3.12'), @('py', '-3.11'), @('py', '-3'), @('python'), @('python3'))
    foreach ($c in $candidates) {
        if (Get-Command $c[0] -ErrorAction SilentlyContinue) {
            if (Test-PythonVersion $c) { return , $c }
        }
    }
    return $null
}

function Get-BotProcess {
    if (-not (Test-Path $PidFile)) { return $null }
    $botPid = 0
    if (-not [int]::TryParse((Get-Content $PidFile -Raw).Trim(), [ref]$botPid)) { return $null }
    $p = Get-Process -Id $botPid -ErrorAction SilentlyContinue
    if (-not $p -or $p.ProcessName -notmatch 'python') { return $null }
    # After a crash the PID file is stale and Windows may reuse the PID. The bot writes
    # the file right after it starts, so a process that started later is someone else.
    try {
        if ($p.StartTime -gt (Get-Item $PidFile).LastWriteTime.AddSeconds(5)) { return $null }
    } catch { }
    return $p
}

function Write-Risk {
    Write-Host ''
    Write-Host 'REMINDER: most meme coins lose money. Results on a $20 account are mostly noise.' -ForegroundColor Yellow
    Write-Host '          Only fund the bot with money you can afford to lose completely.' -ForegroundColor Yellow
    Write-Host ''
}
