# Root Launcher for CTF Platform
$ErrorActionPreference = "Stop"
Set-Location -Path "$PSScriptRoot\ctf-platform"

Write-Host "Starting CTF Platform..." -ForegroundColor Green
python start.py
