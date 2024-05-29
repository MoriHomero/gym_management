@echo off
cd /d C:\Users\hmori\OneDrive - El Cronista Comercial S.A\Escritorio\gym_management
start python manage.py runserver
timeout /t 5 >nul  # Espera unos segundos para que el servidor se inicie completamente
start "" "http://127.0.0.1:8000"  # Abre la URL en el navegador predeterminado
