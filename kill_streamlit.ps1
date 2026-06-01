# Aggressively kill ALL python processes
Get-Process python -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "Stopping PID $($_.Id) path=$($_.Path)"
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}
Start-Sleep -Seconds 5
# Check port
$left = @(Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue)
Write-Host "Port 8501 connections: $($left.Count)"
Get-Process python -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "Still alive: PID $($_.Id) path=$($_.Path)"
}
