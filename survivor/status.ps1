<#
.SYNOPSIS
  Show whether SURVIVOR is running, its last heartbeat and recent log lines.
#>
[CmdletBinding()]
param(
    [int]$LogLines = 10
)
. (Join-Path $PSScriptRoot '_common.ps1')

$proc = Get-BotProcess
if ($proc) {
    Write-Host "SURVIVOR: RUNNING (PID $($proc.Id))" -ForegroundColor Green
} else {
    Write-Host 'SURVIVOR: NOT RUNNING' -ForegroundColor Yellow
}
if (Test-Path $KillFile) { Write-Host 'KILL file present: the bot will not trade until .\run.ps1 removes it.' -ForegroundColor Yellow }

if (Test-Path $StatusFile) {
    $s = Get-Content $StatusFile -Raw | ConvertFrom-Json
    $age = [int]((Get-Date).ToUniversalTime() - [datetime]::Parse($s.updated_utc).ToUniversalTime()).TotalSeconds
    Write-Host ''
    Write-Host ("State:      {0} (mode: {1})" -f $s.state, $s.mode)
    Write-Host ("Heartbeat:  {0} s ago" -f $age)
    Write-Host ("Loops:      {0}   errors: {1}   uptime: {2} s" -f $s.ticks, $s.errors, $s.uptime_s)
    if ($s.stop_reason) { Write-Host ("Stopped by: {0}" -f $s.stop_reason) }
    Write-Host ("Limits:     max {0:P0}/trade, {1} open, daily loss {2:P0} -> pause {3} h" -f `
        $s.limits.max_position_frac, $s.limits.max_open_positions, $s.limits.daily_loss_frac, $s.limits.daily_loss_pause_hours)
} else {
    Write-Host 'No heartbeat yet.'
}

$log = Join-Path $LogDir 'survivor.log'
if (Test-Path $log) {
    Write-Host ''
    Write-Host "Last $LogLines log lines:"
    Get-Content $log -Tail $LogLines
}
