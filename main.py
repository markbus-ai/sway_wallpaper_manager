#!/usr/bin/env python3
# -------------------------------------------------------------------
# main.py - Punto de Entrada Principal (Versión con Miniaturas)
# -------------------------------------------------------------------
# Muestra previsualizaciones de imágenes directamente en rofi.
# El flujo es más directo: seleccionar en rofi aplica el fondo.
# -------------------------------------------------------------------

import sys
import logging
from pathlib import Path
from functools import partial

# Importaciones de nuestros módulos locales
import utils
import automode

def set_wallpaper(image_path: Path, config: dict, quiet: bool = False):
    """
    Establece el fondo de pantalla, genera la paleta y envía una notificación.
    """
    if not quiet:
        logging.info(f"Estableciendo fondo: {image_path.name}")
    
    utils.kill_previous_swaybg()

    swaybg_cmd = [
        'swaybg', '-o', config['swaybg_output'], '-i', str(image_path), '-m', config['swaybg_mode']
    ]
    utils.run_command(swaybg_cmd)

    if not quiet:
        logging.info("Generando paleta de colores con pywal...")
    wal_cmd = ['wal', '-i', str(image_path), '-n', '-q']
    utils.run_command(wal_cmd)
    
    if not quiet:
        utils.send_notification(
            "Fondo de Pantalla Actualizado",
            image_path.name,
            icon=str(image_path)
        )
        logging.info("¡Listo!")

def main_interactive(config: dict):
    """Lanza el modo interactivo usando rofi con miniaturas."""
    images = utils.get_image_files(config['wallpaper_folder'])
    if not images:
        utils.send_notification("Error", "No se encontraron imágenes.", "dialog-warning")
        return

    # Genera las miniaturas y prepara la entrada para rofi
    rofi_input = []
    image_map = {}
    logging.info("Preparando imágenes para rofi...")
    for img in images:
        thumbnail_path = utils.get_thumbnail(img)
        # El formato es: "<texto>\0icon\x1f<ruta_icono>"
        rofi_input.append(f"{img.name}\0icon\x1f{thumbnail_path}")
        image_map[img.name] = img

    rofi_input_str = "\n".join(rofi_input)

    # Lanza rofi en modo de iconos
    rofi_theme = 'window {width: 80%;} configuration {font: "JetBrains Mono 14";}'
    rofi_process = utils.run_command(
        [
            'rofi',
            '-dmenu',
            '-p', '🖼️ Fondo',
            '-i',
            '-show-icons',
            '-theme-str', rofi_theme,
        ],
        input=rofi_input_str, capture_output=True, text=True
    )

    if not rofi_process or rofi_process.returncode != 0:
        logging.info("Selección cancelada.")
        return

    # La salida de rofi es solo el texto, sin la parte del icono
    selected_filename = rofi_process.stdout.strip()
    selected_image_path = image_map.get(selected_filename)

    if selected_image_path:
        # Al seleccionar, se aplica directamente el fondo.
        set_wallpaper(selected_image_path, config)
    else:
        logging.error(f"No se encontró la imagen para '{selected_filename}'")

def print_help():
    """Imprime un mensaje de ayuda detallado."""
    script_name = "sway-wallpaper"
    print(f"Gestor de fondos de pantalla para Sway v{utils.VERSION}")
    print("\nUso:")
    print(f"  {script_name}                - Inicia en modo interactivo con rofi.")
    print(f"  {script_name} --auto         - Inicia el modo de rotación automática.")
    print(f"  {script_name} --set <ruta>   - Establece un fondo de pantalla específico.")
    print(f"  {script_name} --quiet        - Suprime las notificaciones (solo con --set y --auto).")
    print(f"  {script_name} --persist      - Guarda el fondo actual o el modo automático para restaurar al inicio de Sway.")
    print(f"  {script_name} --disable-persist - Deshabilita la persistencia del fondo de pantalla.")
    print(f"  {script_name} --version, -v  - Muestra la versión del script.")
    print(f"  {script_name} --help, -h     - Muestra este mensaje de ayuda.")
    print("\nConfiguración:")
    print(f"  El archivo de configuración se encuentra en: {utils.CONFIG_FILE}")

def main():
    """Punto de entrada principal."""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    utils.check_dependencies()
    config = utils.get_config()
    args = sys.argv[1:]

    if '--version' in args or '-v' in args:
        print(f"sway-wallpaper-manager v{utils.VERSION}")
        return

    if '--disable-persist' in args:
        utils.disable_persistence()
        return

    quiet_mode = '--quiet' in args or '--no-notify' in args
    if quiet_mode:
        if '--quiet' in args:
            args.remove('--quiet')
        if '--no-notify' in args:
            args.remove('--no-notify')

    persist_mode = '--persist' in args
    if persist_mode:
        args.remove('--persist')

    if not args:
        main_interactive(config)
    elif args[0] in ['--help', '-h']:
        print_help()
    elif args[0] == '--auto':
        wallpaper_setter = partial(set_wallpaper, quiet=quiet_mode)
        automode.start_auto_mode(config, utils.get_image_files, wallpaper_setter)
        if persist_mode:
            utils.manage_persistence(f"python {Path(__file__).resolve()} --auto --quiet")
    elif args[0] == '--set' and len(args) > 1:
        image_path = Path(args[1]).expanduser()
        supported_extensions = [ext.replace("*", "") for ext in utils.SUPPORTED_EXTENSIONS]

        if not image_path.is_file():
            error_msg = f"El archivo '{image_path}' no existe."
            logging.error(error_msg)
            utils.send_notification("Error", error_msg, "dialog-error")
        elif image_path.suffix.lower() not in supported_extensions:
            error_msg = f"Tipo de archivo no soportado: '{image_path.suffix}'. Use un formato de imagen válido."
            logging.error(error_msg)
            utils.send_notification("Error", error_msg, "dialog-error")
        else:
            set_wallpaper(image_path, config, quiet=quiet_mode)
            if persist_mode:
                swaybg_cmd = f"swaybg -o {config['swaybg_output']} -i {str(image_path)} -m {config['swaybg_mode']}"
                utils.manage_persistence(swaybg_cmd)
    else:
        logging.error(f"Argumento no válido: '{args[0]}'. Usa '--help' para ver las opciones.")

if __name__ == "__main__":
    main()
