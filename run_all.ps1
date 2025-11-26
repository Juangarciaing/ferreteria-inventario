# Lanza backend y frontend en ventanas separadas de PowerShell
$root = "c:\Users\Juanc\Videos\Modelo y simulacion\S2"
$backend = Join-Path $root "run_backend.ps1"
$frontend = Join-Path $root "run_frontend.ps1"

if (-not (Test-Path $backend)) { Write-Error "No se encontró $backend"; exit 1 }
if (-not (Test-Path $frontend)) { Write-Error "No se encontró $frontend"; exit 1 }

# Verificación previa: MySQL disponible en 127.0.0.1:3306
Write-Host "Verificando MySQL en 127.0.0.1:3306..." -ForegroundColor Cyan
$mysqlCheck = $null
try {
	$mysqlCheck = Test-NetConnection -ComputerName 127.0.0.1 -Port 3306 -WarningAction SilentlyContinue
} catch {
	$mysqlCheck = $null
}

if (-not $mysqlCheck -or -not $mysqlCheck.TcpTestSucceeded) {
	Write-Warning "MySQL no responde en 127.0.0.1:3306."
	Write-Host "Sugerencias:" -ForegroundColor Yellow
	Write-Host " - Asegúrate de que el servicio MySQL esté iniciado (MySQL80)." -ForegroundColor Yellow
	Write-Host " - Revisa puerto/credenciales en la variable DATABASE_URL del backend (app/config.py o entorno)." -ForegroundColor Yellow
	Write-Host " - Puedes probar: Test-NetConnection -ComputerName 127.0.0.1 -Port 3306" -ForegroundColor Yellow
	exit 1
}

Write-Host "Abriendo ventana para BACKEND..."
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit -ExecutionPolicy Bypass -File `"$backend`"" -WorkingDirectory $root

Start-Sleep -Seconds 2

Write-Host "Abriendo ventana para FRONTEND..."
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit -ExecutionPolicy Bypass -File `"$frontend`"" -WorkingDirectory $root

Write-Host "Listo. Se abrieron dos ventanas: backend y frontend."