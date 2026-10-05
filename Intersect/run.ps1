# Windows PowerShell Single Command Launcher for CTF Platform
$ErrorActionPreference = "Stop"
Set-Location -Path $PSScriptRoot

Write-Host "Starting CTF Platform..." -ForegroundColor Green
python start.py
