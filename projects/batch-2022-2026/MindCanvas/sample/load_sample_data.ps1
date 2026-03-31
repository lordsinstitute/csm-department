# MindCanvas Sample Data Loader
# Run this in PowerShell: .\load_sample_data.ps1
# Make sure backend is running on localhost:8090

Write-Host "`n=== MindCanvas Sample Data Loader ===" -ForegroundColor Cyan
Write-Host "Loading 35 sample URLs into MindCanvas...`n" -ForegroundColor White

$jsonPath = Join-Path $PSScriptRoot "sample_data.json"
if (-Not (Test-Path $jsonPath)) {
    Write-Host "ERROR: sample_data.json not found at $jsonPath" -ForegroundColor Red
    exit 1
}

$body = Get-Content $jsonPath -Raw

try {
    Write-Host "Sending to http://localhost:8090/api/ingest ..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri "http://localhost:8090/api/ingest" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -TimeoutSec 300

    Write-Host "`n=== Results ===" -ForegroundColor Green
    Write-Host "Status    : $($response.status)"
    Write-Host "Total     : $($response.total)"
    Write-Host "New       : $($response.new)"
    Write-Host "Existing  : $($response.existing)"
    Write-Host "Message   : $($response.message)"
    Write-Host "`nDone! Open http://localhost:3030 to see your knowledge graph.`n" -ForegroundColor Cyan
}
catch {
    Write-Host "ERROR: Failed to connect. Is the backend running?" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host "`nStart it with: docker-compose up -d" -ForegroundColor Yellow
}
