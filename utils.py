# -------------------------------------------------------------------
# utils.py - Utilidades Comunes (Versión con Miniaturas)
# -------------------------------------------------------------------
# Añade la lógica para generar y cachear miniaturas para rofi.
# -------------------------------------------------------------------

import subprocess
import configparser
import hashlib
import logging
from pathlib import Path
import sys
import shutil

# Constantes del proyecto
VERSION = "1.1.0"
CONFIG_FILE = Path(__file__).parent / 'config.ini'
THUMBNAIL_CACHE_DIR = Path.home() / '.cache/sway-wallpaper-manager/thumbnails'
THUMBNAIL_SIZE = "128x128"
SUPPORTED_EXTENSIONS = [
    "*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.svg", "*.webp",
    "*.tiff", "*.avif", "*.heic"
]

# Rutas para la persistencia en Sway
SWAY_CONFIG_DIR = Path.home() / '.config/sway'
SWAY_CONFIG_FILE = SWAY_CONFIG_DIR / 'config'
SWAY_WM_CONFIG_DIR = Path.home() / '.config/sway-wallpaper-manager'
RESTORE_SCRIPT_PATH = SWAY_WM_CONFIG_DIR / 'restore.sh'

def create_default_config():
    """Crea un archivo config.ini con valores por defecto si no existe."""
    logging.info("No se encontró 'config.ini'. Creando uno por defecto.")
    config = configparser.ConfigParser()
    config['Settings'] = {
        'wallpaper_folder': '~/wallpaper',
        'rotation_interval_minutes': '30',
        'rotation_order': 'random',
        'swaybg_output': '*',
        'swaybg_mode': 'fill'
    }
    try:
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
        logging.info(f"Archivo de configuración creado en '{CONFIG_FILE}'")
    except IOError as e:
        logging.error(f"No se pudo crear el archivo de configuración: {e}")
        sys.exit(1)

def get_config():
    """Lee y parsear el archivo config.ini. Si no existe, lo crea."""
    if not CONFIG_FILE.exists():
        create_default_config()
        
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config['Settings']

def check_dependencies():
    """Verifica que todas las dependencias de línea de comandos estén instaladas."""
    dependencies = ['swaybg', 'rofi', 'wal', 'notify-send', 'convert']
    missing = [dep for dep in dependencies if not shutil.which(dep)]
    
    if missing:
        logging.error("Faltan dependencias críticas.")
        for dep in missing:
            logging.error(f"  - '{dep}' no se encontró.")
        logging.error("\nPor favor, ejecuta de nuevo 'install.sh' para instalarlas.")
        sys.exit(1)

def get_image_files(folder_path_str: str) -> list[Path]:
    """Encuentra todos los archivos de imagen en una carpeta específica."""
    folder_path = Path(folder_path_str).expanduser()
    
    if not folder_path.is_dir():
        send_notification(
            "Error de Configuración",
            f"La carpeta '{folder_path}' no existe. Edita 'config.ini'."
        )
        logging.error(f"La carpeta de fondos '{folder_path}' no existe.")
        return []

    image_files = [p for ext in SUPPORTED_EXTENSIONS for p in folder_path.glob(ext)]
    
    return sorted(image_files, key=lambda p: p.name)

def get_thumbnail(image_path: Path) -> Path:
    """Genera (si es necesario) y devuelve la ruta a una miniatura cacheada."""
    THUMBNAIL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    hash_name = hashlib.md5(str(image_path).encode()).hexdigest()
    thumbnail_path = THUMBNAIL_CACHE_DIR / f"{hash_name}_{image_path.name}"

    if not thumbnail_path.exists() or image_path.stat().st_mtime > thumbnail_path.stat().st_mtime:
        logging.info(f"Generando miniatura para: {image_path.name}")
        run_command([
            'convert', str(image_path),
            '-thumbnail', THUMBNAIL_SIZE + '^',
            '-gravity', 'center',
            '-extent', THUMBNAIL_SIZE,
            str(thumbnail_path)
        ])
    
    return thumbnail_path

def run_command(command: list[str], background: bool = False, **kwargs):
    """Ejecuta un comando en el sistema. Si background=True, no espera a que termine."""
    try:
        if background:
            return subprocess.Popen(command, **kwargs)
        else:
            return subprocess.run(command, check=True, **kwargs)
    except FileNotFoundError:
        logging.error(f"El comando '{command[0]}' no se encontró.")
        return None
    except subprocess.CalledProcessError as e:
        logging.error(f"Error al ejecutar '{' '.join(command)}': {e}")
        return None

def kill_previous_swaybg():
    """Busca y termina cualquier proceso 'swaybg' existente."""
    subprocess.run(['pkill', '-f', 'swaybg'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def send_notification(title: str, message: str, icon: str = "dialog-information") -> None:
    """Envía una notificación de escritorio."""
    try:
        subprocess.Popen(['notify-send', title, message, '-i', icon])
    except FileNotFoundError:
        logging.warning(f"El comando 'notify-send' no se encontró. Notificación: {title} - {message}")

def manage_persistence() -> None:
    """Genera un script restore.sh que lee la ruta del fondo dinámicamente y usa la config actual."""
    SWAY_WM_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # Leer la configuración actual para swaybg
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    settings = config['Settings']
    swaybg_output = settings.get('swaybg_output', '*')
    swaybg_mode = settings.get('swaybg_mode', 'fill')

    try:
        restore_script = f'''#!/bin/bash

WALLPAPER_FILE="{LAST_WALLPAPER_FILE}"
if [ -f "$WALLPAPER_FILE" ]; then
    WALLPAPER_PATH=$(cat "$WALLPAPER_FILE")
    pkill -f swaybg
    sleep 1
    # Reintento hasta 3 veces si swaybg falla
    for i in 1 2 3; do
        swaybg -o "{swaybg_output}" -i "$WALLPAPER_PATH" -m {swaybg_mode} && break
        sleep 1
    done
else
    echo "No se encontró el fondo guardado en $WALLPAPER_FILE" >&2
fi
'''
        with open(RESTORE_SCRIPT_PATH, 'w') as f:
            f.write(restore_script)
        RESTORE_SCRIPT_PATH.chmod(0o755)
        logging.info(f"Script de restauración creado en '{RESTORE_SCRIPT_PATH}'")
    except IOError as e:
        logging.error(f"No se pudo crear el script de restauración: {e}")
        send_notification("Error de Persistencia", "No se pudo crear el script de restauración.", "dialog-error")
        return

    if not SWAY_CONFIG_FILE.exists():
        logging.warning(f"Archivo de configuración de Sway no encontrado en '{SWAY_CONFIG_FILE}'.")
        send_notification("Error de Persistencia", "Archivo de configuración de Sway no encontrado.", "dialog-warning")
        return

    try:
        sway_config_content = SWAY_CONFIG_FILE.read_text()
        exec_line = f'exec_always "{RESTORE_SCRIPT_PATH}"'

        if exec_line not in sway_config_content:
            with open(SWAY_CONFIG_FILE, 'a') as f:
                f.write(f"\n# Sway Wallpaper Manager Persistence\n{exec_line}\n")
            logging.info(f"Línea de persistencia añadida a '{SWAY_CONFIG_FILE}'")
            send_notification("Persistencia Configurada", "El fondo se restaurará al iniciar Sway.", "dialog-information")
        else:
            logging.info("La línea de persistencia ya existe.")
            send_notification("Persistencia Existente", "El fondo ya está configurado para restaurarse.", "dialog-information")

    except IOError as e:
        logging.error(f"Error al modificar el config de Sway: {e}")
        send_notification("Error de Persistencia", "No se pudo modificar el archivo de configuración de Sway.", "dialog-error")

def disable_persistence() -> None:
    """Deshabilita la persistencia eliminando el script y la línea del config de Sway."""
    # Eliminar el script restore.sh
    if RESTORE_SCRIPT_PATH.exists():
        try:
            RESTORE_SCRIPT_PATH.unlink()
            logging.info(f"Script de restauración eliminado: {RESTORE_SCRIPT_PATH}")
        except OSError as e:
            logging.error(f"No se pudo eliminar el script de restauración: {e}")
            send_notification("Error al Deshabilitar", "No se pudo eliminar el script de restauración.", "dialog-error")
            return
    else:
        logging.info("El script de restauración no existe. Nada que eliminar.")

    # Eliminar la línea de exec_always del config de Sway
    if not SWAY_CONFIG_FILE.exists():
        logging.warning(f"Archivo de configuración de Sway no encontrado en '{SWAY_CONFIG_FILE}'. No hay persistencia que deshabilitar.")
        send_notification("Error al Deshabilitar", "Archivo de configuración de Sway no encontrado.", "dialog-warning")
        return

    try:
        lines = SWAY_CONFIG_FILE.read_text().splitlines()
        new_lines = []
        removed = False
        skip_next = False
        for i, line in enumerate(lines):
            if f"exec_always \"{RESTORE_SCRIPT_PATH}\"" in line:
                removed = True
                # Intentar también eliminar el comentario si está justo antes
                if i > 0 and lines[i-1].strip() == "# Sway Wallpaper Manager Persistence":
                    new_lines.pop() # Eliminar la línea de comentario anterior
                continue
            new_lines.append(line)
        
        if removed:
            SWAY_CONFIG_FILE.write_text("\n".join(new_lines) + "\n")
            logging.info(f"Línea de persistencia eliminada de '{SWAY_CONFIG_FILE}'")
            send_notification("Persistencia Deshabilitada", "El fondo de pantalla ya no se restaurará al iniciar Sway.", "dialog-information")
        else:
            logging.info("La línea de persistencia no se encontró en la configuración de Sway. Nada que deshabilitar.")
            send_notification("Persistencia No Encontrada", "La persistencia no estaba configurada.", "dialog-information")

    except IOError as e:
        logging.error(f"Error al leer/escribir el archivo de configuración de Sway: {e}")
        send_notification("Error al Deshabilitar", "No se pudo modificar el archivo de configuración de Sway.", "dialog-error")
LAST_WALLPAPER_FILE = SWAY_WM_CONFIG_DIR / 'last_wallpaper.txt'

def save_last_wallpaper(image_path: Path) -> None:
    """Guarda la ruta del último fondo de pantalla usado."""
    SWAY_WM_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(LAST_WALLPAPER_FILE, 'w') as f:
            f.write(str(image_path))
        logging.info(f"Ruta del fondo guardada en '{LAST_WALLPAPER_FILE}'")
    except IOError as e:
        logging.error(f"No se pudo guardar la ruta del fondo: {e}")
        send_notification("Error", "No se pudo guardar el fondo actual.", "dialog-error")
