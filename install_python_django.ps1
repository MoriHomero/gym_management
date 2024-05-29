# Verificar si PowerShell está habilitado
if ($PSVersionTable.PSEdition -eq 'Desktop' -and (Get-ExecutionPolicy) -ne 'Bypass') {
    Write-Host "Por favor, habilite la ejecución de scripts de PowerShell."
    Write-Host "Para hacerlo, abra PowerShell como administrador y ejecute el siguiente comando:"
    Write-Host "Set-ExecutionPolicy Bypass -Scope Process -Force"
    Write-Host "Después de ejecutar el comando, vuelva a ejecutar este script."
    pause
    exit
}

# Descargar el instalador de Python
Invoke-WebRequest https://www.python.org/ftp/python/3.10.2/python-3.10.2-amd64.exe -OutFile python_installer.exe

# Instalar Python
Start-Process -Wait python_installer.exe -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1"

# Eliminar el instalador de Python
Remove-Item python_installer.exe

# Instalar Django
python -m pip install django

# Instalar openpyxl
python -m pip install openpyxl

Write-Host "La instalación de Python, Django y openpyxl se ha completado correctamente."
