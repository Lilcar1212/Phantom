<#
.SYNOPSIS
  One-time setup: Python 3.11+, a virtual environment, dependencies, .env and data folders.
.EXAMPLE
  .\install.ps1
#>
[CmdletBinding()]
param(
    [switch]$SkipPythonInstall
)
. (Join-Path $PSScriptRoot '_common.ps1')

Write-Host '== SURVIVOR install ==' -ForegroundColor Cyan
Write-Risk

# 1. Python 3.11+
$py = Find-Python
if (-not $py) {
    if ($SkipPythonInstall -or -not $OnWindows) {
        throw 'Python 3.11 or newer was not found. Install it, then run this script again.'
    }
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        throw 'Python 3.11+ is missing and winget is not available. Install Python from https://www.python.org/downloads/ and rerun.'
    }
    Write-Host 'Python 3.11+ not found. Installing Python 3.12 with winget (per-user)...'
    winget install --exact --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
    if ($LASTEXITCODE -ne 0) { throw "winget failed with exit code $LASTEXITCODE" }
    # Pick up the new PATH without reopening the terminal.
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'User') + ';' + [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $py = Find-Python
    if (-not $py) { throw 'Python was installed but is not on PATH yet. Open a new PowerShell window and rerun .\install.ps1.' }
}
Write-Host ("Using Python: " + ($py -join ' '))

# 2. Virtual environment
$venvPy = Get-VenvPython
if (-not (Test-Path $venvPy)) {
    Write-Host 'Creating virtual environment in .venv ...'
    $exe = $py[0]
    $rest = @()
    if ($py.Count -gt 1) { $rest = $py[1..($py.Count - 1)] }
    & $exe @rest -m venv $VenvDir
    if ($LASTEXITCODE -ne 0) { throw 'Failed to create the virtual environment.' }
}

# 3. Dependencies
Write-Host 'Installing dependencies ...'
& $venvPy -m pip install --upgrade pip --quiet
& $venvPy -m pip install -r (Join-Path $Root 'requirements.txt') --quiet
if ($LASTEXITCODE -ne 0) { throw 'pip install failed.' }

# 4. Folders and .env
New-Item -ItemType Directory -Force -Path $DataDir, $LogDir | Out-Null
$envFile = Join-Path $Root '.env'
if (-not (Test-Path $envFile)) {
    Copy-Item (Join-Path $Root '.env.example') $envFile
    Write-Host 'Created .env from .env.example. Add your RPC URL there (never commit it).'
}

Write-Host ''
Write-Host 'Install complete.' -ForegroundColor Green
Write-Host '  Start:  .\run.ps1'
Write-Host '  Status: .\status.ps1'
Write-Host '  Stop:   .\stop.ps1'
