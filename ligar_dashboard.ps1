# Script para iniciar o BLK Dashboarding com limite de 10GB
Write-Host "Iniciando Dashboard com limite de 10GB..." -ForegroundColor Green
streamlit run app.py --server.maxUploadSize 10240
