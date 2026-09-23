# Starts render_agent.py as a detached background process (no console
# window, via pythonw.exe). Safe to run multiple times -- it won't start a
# second copy if one is already running.
#
# Usage:   .\start_render_agent.ps1
# Stop:    .\stop_render_agent.ps1
# Logs:    render_agent.log (stdout), render_agent.err.log (stderr)

$ErrorActionPreference = "Stop"

$pidFile = Join-Path $PSScriptRoot "render_agent.pid"
$outLog = Join-Path $PSScriptRoot "render_agent.log"
$errLog = Join-Path $PSScriptRoot "render_agent.err.log"

if (Test-Path $pidFile) {
    $existingPid = Get-Content $pidFile -ErrorAction SilentlyContinue
    $existingProcess = Get-Process -Id $existingPid -ErrorAction SilentlyContinue
    if ($existingProcess -and $existingProcess.ProcessName -match "python") {
        Write-Host "render_agent.py is already running (PID $existingPid). Not starting a second copy."
        exit 0
    }
    Write-Host "Found a stale PID file (process $existingPid is not running). Cleaning up."
    Remove-Item $pidFile -Force
}

$process = Start-Process -FilePath "pythonw" `
    -ArgumentList "-u", "render_agent.py" `
    -WorkingDirectory $PSScriptRoot `
    -RedirectStandardOutput $outLog `
    -RedirectStandardError $errLog `
    -WindowStyle Hidden `
    -PassThru

$process.Id | Out-File -FilePath $pidFile -Encoding ascii

Write-Host "Started render_agent.py in the background (PID $($process.Id))."
Write-Host "Logs: $outLog / $errLog"
Write-Host "Stop it with: .\stop_render_agent.ps1"
