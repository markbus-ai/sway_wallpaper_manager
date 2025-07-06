# -------------------------------------------------------------------
# automode.py - Módulo de Modo Automático (Versión Mejorada)
# -------------------------------------------------------------------
# Implementa la funcionalidad de cambio de fondo de pantalla
# automático en intervalos de tiempo definidos.
# -------------------------------------------------------------------

import time
import random
import logging
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
        interval_minutes = int(config.get('rotation_interval_minutes', 30))
        if interval_minutes < 1:
            raise ValueError("El intervalo mínimo recomendado es de 1 minuto.")
        
        interval_seconds = interval_minutes * 60
        wallpaper_folder = config['wallpaper_folder']
        rotation_order = config.get('rotation_order', 'random').lower()

        start_message = f"Cambiando fondo cada {interval_minutes} min (orden: {rotation_order})."
        logging.info(f"Modo automático iniciado. {start_message}")
        logging.info("Presiona Ctrl+C para detener.")
        send_notification("Modo Automático Activado", start_message, "preferences-desktop-wallpaper")

        no_images_count = 0
        current_index = 0

        while True:
            images = get_images_func(wallpaper_folder)
            
            if not images:
                if no_images_count == 0:
                    logging.warning(f"No se encontraron imágenes en '{wallpaper_folder}'. Esperando...")
                no_images_count += 1
                time.sleep(interval_seconds)
                continue
            else:
                no_images_count = 0

            if rotation_order == 'sequential':
                if current_index >= len(images):
                    current_index = 0  # Reinicia al llegar al final
                selected_image = images[current_index]
                current_index += 1
            else:  # random
                selected_image = random.choice(images)
            
            logging.info(f"Estableciendo nuevo fondo: {selected_image.name}")
            set_wallpaper_func(selected_image, config, quiet=True)
            
            time.sleep(interval_seconds)

    except (ValueError, KeyError) as e:
        error_msg = f"Error de configuración: {e}"
        logging.error(error_msg)
        send_notification("Error de Configuración", str(e), "dialog-error")
    except KeyboardInterrupt:
        logging.info("\nModo automático detenido por el usuario.")
        send_notification("Modo Automático Desactivado", "El cambio de fondos se ha detenido.", "process-stop")
    except Exception as e:
        logging.error(f"Ocurrió un error inesperado: {e}")
        send_notification("Error en Modo Automático", str(e), "dialog-error")