<#
.SYNOPSIS
  Emergency stop. Creates the KILL file (checked every second), waits for a clean
  exit, then force-stops the process if it has not exited.
.PARAMETER TimeoutSeconds
  How long to wait for a clean exit before force-stopping.
#>
[CmdletBinding()]
param(
    [int]$TimeoutSeconds = 30
)
. (Join-Path $PSScriptRoot '_common.ps1')

New-Item -ItemType File -Force -Path $KillFile | Out-Null
Write-Host 'KILL file created.' -ForegroundColor Yellow

$proc = Get-BotProcess
if (-not $proc) {
    Write-Host 'SURVIVOR is not running.'
    exit 0
}

Write-Host "Waiting up to $TimeoutSeconds s for PID $($proc.Id) to exit cleanly ..."
if ($proc.WaitForExit($TimeoutSeconds * 1000)) {
    Write-Host 'SURVIVOR stopped cleanly.' -ForegroundColor Green
} else {
    Write-Host 'No clean exit; force-stopping. Open positions stay in the wallet and are recovered from the ledger on the next run.' -ForegroundColor Red
    Stop-Process -Id $proc.Id -Force
}
