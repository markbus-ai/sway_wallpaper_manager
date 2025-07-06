# -------------------------------------------------------------------
# utils.py - Utilidades Comunes (Versión con Miniaturas)
# -------------------------------------------------------------------
# Añade la lógica para generar y cachear miniaturas para rofi.
# -------------------------------------------------------------------

import subprocess
import configparser
import hashlib
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

def create_default_config():
    """Crea un archivo config.ini con valores por defecto si no existe."""
    print("INFO: No se encontró 'config.ini'. Creando uno por defecto.")
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
        print(f"INFO: Archivo de configuración creado en '{CONFIG_FILE}'")
    except IOError as e:
        print(f"ERROR: No se pudo crear el archivo de configuración: {e}", file=sys.stderr)
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
        print("ERROR: Faltan dependencias críticas.", file=sys.stderr)
        for dep in missing:
            print(f"  - '{dep}' no se encontró.", file=sys.stderr)
        print("\nPor favor, ejecuta de nuevo 'install.sh' para instalarlas.", file=sys.stderr)
        sys.exit(1)

def get_image_files(folder_path_str: str) -> list[Path]:
    """Encuentra todos los archivos de imagen en una carpeta específica."""
    folder_path = Path(folder_path_str).expanduser()
    
    if not folder_path.is_dir():
        send_notification(
            "Error de Configuración",
            f"La carpeta '{folder_path}' no existe. Edita 'config.ini'."
        )
        print(f"Error: La carpeta de fondos '{folder_path}' no existe.", file=sys.stderr)
        return []

    image_files = [p for ext in SUPPORTED_EXTENSIONS for p in folder_path.glob(ext)]
    
    return sorted(image_files, key=lambda p: p.name)

def get_thumbnail(image_path: Path) -> Path:
    """Genera (si es necesario) y devuelve la ruta a una miniatura cacheada."""
    THUMBNAIL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    hash_name = hashlib.md5(str(image_path).encode()).hexdigest()
    thumbnail_path = THUMBNAIL_CACHE_DIR / f"{hash_name}_{image_path.name}"

    if not thumbnail_path.exists() or image_path.stat().st_mtime > thumbnail_path.stat().st_mtime:
        print(f"Generando miniatura para: {image_path.name}")
        run_command([
            'convert', str(image_path),
            '-thumbnail', THUMBNAIL_SIZE + '^',
            '-gravity', 'center',
            '-extent', THUMBNAIL_SIZE,
            str(thumbnail_path)
        ])
    
    return thumbnail_path

def run_command(command: list[str], **kwargs):
    """Ejecuta un comando en el sistema."""
    try:
        return subprocess.run(command, check=True, **kwargs)
    except FileNotFoundError:
        print(f"Error: El comando '{command[0]}' no se encontró.", file=sys.stderr)
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar '{' '.join(command)}': {e}", file=sys.stderr)
        return None

def kill_previous_swaybg():
    """Busca y termina cualquier proceso 'swaybg' existente."""
    subprocess.run(['pkill', '-f', 'swaybg'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def send_notification(title: str, message: str, icon: str = "dialog-information") -> None:
    """Envía una notificación de escritorio."""
    try:
        subprocess.Popen(['notify-send', title, message, '-i', icon])
    except FileNotFoundError:
        print(f"NOTIFICACIÓN: {title} - {message}")
