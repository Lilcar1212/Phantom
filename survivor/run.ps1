<#
.SYNOPSIS
  Set up (if needed) and start SURVIVOR in the background.
.PARAMETER Foreground
  Run in this window instead of the background (Ctrl+C stops it).
.PARAMETER NoBrowser
  Do not open the city dashboard in the browser.
.EXAMPLE
  .\run.ps1
#>
[CmdletBinding()]
param(
    [switch]$Foreground,
    [switch]$NoBrowser
)
. (Join-Path $PSScriptRoot '_common.ps1')

Write-Host '== SURVIVOR ==' -ForegroundColor Cyan
Write-Risk

$venvPy = Get-VenvPython
if (-not (Test-Path $venvPy)) {
    Write-Host 'First run: installing ...'
    & (Join-Path $Root 'install.ps1')
}

$running = Get-BotProcess
if ($running) {
    Write-Host "SURVIVOR is already running (PID $($running.Id)). Use .\status.ps1 or .\stop.ps1." -ForegroundColor Yellow
    exit 0
}

if (Test-Path $KillFile) {
    Write-Host 'Removing KILL file left by the last stop.'
    Remove-Item $KillFile -Force
}
New-Item -ItemType Directory -Force -Path $DataDir, $LogDir | Out-Null

if ($Foreground) {
    Push-Location $Root
    try { & $venvPy -m core.main } finally { Pop-Location }
    exit $LASTEXITCODE
}

$startArgs = @{
    FilePath               = $venvPy
    ArgumentList           = @('-m', 'core.main')
    WorkingDirectory       = $Root
    RedirectStandardOutput = (Join-Path $LogDir 'console.out.log')
    RedirectStandardError  = (Join-Path $LogDir 'console.err.log')
    PassThru               = $true
}
if ($OnWindows) { $startArgs.WindowStyle = 'Hidden' }
$proc = Start-Process @startArgs

# Wait for the first heartbeat so problems show up now, not later.
$deadline = (Get-Date).AddSeconds(20)
while ((Get-Date) -lt $deadline) {
    if ($proc.HasExited) { break }
    if ((Test-Path $StatusFile) -and ((Get-Item $StatusFile).LastWriteTime -gt $proc.StartTime)) { break }
    Start-Sleep -Milliseconds 500
}

if ($proc.HasExited) {
    Write-Host "SURVIVOR exited immediately (code $($proc.ExitCode)). Last errors:" -ForegroundColor Red
    Get-Content (Join-Path $LogDir 'console.err.log') -Tail 20 -ErrorAction SilentlyContinue
    exit 1
}

Write-Host "SURVIVOR started (PID $($proc.Id))." -ForegroundColor Green
Write-Host '  Logs:   data\logs\survivor.log'
Write-Host '  Status: .\status.ps1'
Write-Host '  Stop:   .\stop.ps1   (or create a file named KILL in this folder)'
if (-not $NoBrowser) {
    Write-Host '  City dashboard: arrives in milestone 4.'
}
