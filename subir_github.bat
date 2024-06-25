@echo off
REM Cambiar al directorio del repositorio
cd 'C:\Users\fariass\OneDrive - SUBSECRETARIA DE SALUD PUBLICA\Escritorio\PNI\dashboard_vacunacion_ministerial_influenza_comunal'

REM Verificar que estamos en la rama main
git checkout main

REM Añadir todos los cambios
git add .

REM Obtener fecha y hora actuales
for /f "tokens=1-4 delims=/ " %%i in ("%date%") do set currentDate=%%i-%%j-%%k
for /f "tokens=1-2 delims=: " %%i in ("%time%") do set currentTime=%%i-%%j

REM Hacer commit con un mensaje
set commitMessage=Actualizacion automatizada %currentDate% %currentTime%
git commit -m "%commitMessage%"

REM Subir los cambios a la rama main
git push origin main