Write-Host "Starting VegeStore Development Servers..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\VegeStore\backend'; python app.py"
Start-Sleep 3
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\VegeStore\frontend'; npm install; npm start"
Write-Host "Backend: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan