# -------------------------------------------------------------------
# automode.py - Módulo de Modo Automático (Versión Mejorada)
# -------------------------------------------------------------------
# Implementa la funcionalidad de cambio de fondo de pantalla
# automático en intervalos de tiempo definidos.
# -------------------------------------------------------------------

import time
import random
from pathlib import Path
from typing import Callable
from utils import send_notification

def start_auto_mode(
    config: dict, 
    get_images_func: Callable[[str], list[Path]], 
    set_wallpaper_func: Callable[[Path, dict], None]
):
    """Inicia el ciclo de cambio de fondo de pantalla automático."""
    try:
        interval_minutes = int(config['rotation_interval_minutes'])
        interval_seconds = interval_minutes * 60
        wallpaper_folder = config['wallpaper_folder']
        
        start_message = f"Cambiando fondo cada {interval_minutes} min."
        print(f"Modo automático iniciado. {start_message}")
        print("Presiona Ctrl+C para detener.")
        send_notification("Modo Automático Activado", start_message, "preferences-desktop-wallpaper")

        while True:
            images = get_images_func(wallpaper_folder)
            if not images:
                print(f"No se encontraron imágenes en '{wallpaper_folder}'. Esperando...")
                time.sleep(interval_seconds)
                continue

            random_image = random.choice(images)
            
            print(f"Estableciendo nuevo fondo: {random_image.name}")
            set_wallpaper_func(random_image, config, quiet=True) # quiet=True para no duplicar notificaciones
            
            time.sleep(interval_seconds)

    except (ValueError, KeyError):
        error_msg = "'rotation_interval_minutes' no es un número válido en 'config.ini'."
        print(f"Error: {error_msg}")
        send_notification("Error de Configuración", error_msg, "dialog-error")
    except KeyboardInterrupt:
        print("\nModo automático detenido por el usuario.")
        send_notification("Modo Automático Desactivado", "El cambio de fondos se ha detenido.", "process-stop")
    except Exception as e:
        print(f"Ocurrió un error inesperado en el modo automático: {e}")
        send_notification("Error en Modo Automático", str(e), "dialog-error")