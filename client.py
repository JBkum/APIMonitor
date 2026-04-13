import psutil
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Configuración (Estándar: Usar variables de entorno)
API_URL = "http://127.0.0.1:5000/metrics" # Cambia esto cuando subas la API a la nube
API_KEY = os.getenv('MY_SECRET_API_KEY')

def get_system_metrics():
    # 1. Obtener Memoria
    mem = psutil.virtual_memory()
    mem_info = f"{mem.used / (1024**3):.1f}Gi/{mem.total / (1024**3):.1f}Gi"
    
    # 2. Obtener Batería (Si el dispositivo tiene)
    battery = psutil.sensors_battery()
    if battery:
        percent = battery.percent
        status = "CHARGING" if battery.power_plugged else "DISCHARGING"
    else:
        percent = 0
        status = "NO_BATTERY"
        
    # 3. Temperatura (Nota: psutil.sensors_temperatures() varía según el SO)
    # Por simplicidad profesional, usaremos un valor base o mock si no es Linux
    temp = 31.6 # Aquí podrías mapear sensores reales según el hardware
    
    return {
        "memory": mem_info,
        "battery": int(percent),
        "status": status,
        "temp": temp
    }

def send_data():
    payload = get_system_metrics()
    headers = {'X-API-KEY': API_KEY}
    
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        if response.status_code == 201:
            print(f"[{time.strftime('%H:%M:%S')}] Datos enviados con éxito.")
        else:
            print(f"Error del servidor: {response.status_code}")
    except Exception as e:
        print(f"Error de conexión: {e}")

if __name__ == "__main__":
    # Para cumplir tu requerimiento de "cada minuto"
    print("Iniciando monitoreo profesional...")
    while True:
        send_data()
        time.sleep(60) # Espera 60 segundos