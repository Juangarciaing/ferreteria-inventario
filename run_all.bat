@echo off
setlocal
set ROOT_DIR=C:\Users\Juanc\Videos\Modelo y simulacion\S2
set PS1_FILE="%ROOT_DIR%\run_all.ps1"

if not exist %PS1_FILE% (
  echo No se encontró %PS1_FILE%
  exit /b 1
)

powershell.exe -NoProfile -ExecutionPolicy Bypass -File %PS1_FILE%
endlocal
