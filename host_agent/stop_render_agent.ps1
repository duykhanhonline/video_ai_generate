# Stops the background render_agent.py process started by
# start_render_agent.ps1.
#
# Usage: .\stop_render_agent.ps1

$ErrorActionPreference = "Stop"

$pidFile = Join-Path $PSScriptRoot "render_agent.pid"

if (-not (Test-Path $pidFile)) {
    Write-Host "render_agent.py does not appear to be running (no PID file found)."
    exit 0
}

$existingPid = Get-Content $pidFile -ErrorAction SilentlyContinue
$process = Get-Process -Id $existingPid -ErrorAction SilentlyContinue

if (-not $process) {
    Write-Host "PID file points to a process that is not running. Cleaning up."
    Remove-Item $pidFile -Force
    exit 0
}

Stop-Process -Id $existingPid -Force
Remove-Item $pidFile -Force
Write-Host "Stopped render_agent.py (PID $existingPid)."
