#!/usr/bin/env python3
# -------------------------------------------------------------------
# main.py - Punto de Entrada Principal (Versión con Miniaturas)
# -------------------------------------------------------------------
# Muestra previsualizaciones de imágenes directamente en rofi.
# El flujo es más directo: seleccionar en rofi aplica el fondo.
# -------------------------------------------------------------------

import sys
from pathlib import Path

# Importaciones de nuestros módulos locales
import utils
import automode

def set_wallpaper(image_path: Path, config: dict, quiet: bool = False):
    """
    Establece el fondo de pantalla, genera la paleta y envía una notificación.
    """
    if not quiet:
        print(f"Estableciendo fondo: {image_path.name}")
    
    utils.kill_previous_swaybg()

    swaybg_cmd = [
        'swaybg', '-o', config['swaybg_output'], '-i', str(image_path), '-m', config['swaybg_mode']
    ]
    utils.run_command(swaybg_cmd)

    if not quiet:
        print("Generando paleta de colores con pywal...")
    wal_cmd = ['wal', '-i', str(image_path), '-n', '-q']
    utils.run_command(wal_cmd)
    
    utils.send_notification(
        "Fondo de Pantalla Actualizado",
        image_path.name,
        icon=str(image_path)
    )
    if not quiet:
        print("¡Listo!")

def main_interactive(config: dict):
    """Lanza el modo interactivo usando rofi con miniaturas."""
    images = utils.get_image_files(config['wallpaper_folder'])
    if not images:
        utils.send_notification("Error", "No se encontraron imágenes.", "dialog-warning")
        return

    # Genera las miniaturas y prepara la entrada para rofi
    rofi_input = []
    image_map = {}
    print("Preparando imágenes para rofi...")
    for img in images:
        thumbnail_path = utils.get_thumbnail(img)
        # El formato es: "<texto>\0icon\x1f<ruta_icono>"
        rofi_input.append(f"{img.name}\0icon\x1f{thumbnail_path}")
        image_map[img.name] = img

    rofi_input_str = "\n".join(rofi_input)

    # Lanza rofi en modo de iconos
    rofi_process = utils.run_command(
        [
            'rofi',
            '-dmenu',
            '-p', '🖼️ Fondo',
            '-i',
            '-show-icons',
            '-theme-str', 'window {width: 80%;}',
            '-theme-str', 'configuration {font: "JetBrains Mono 14";}',
        ],
        input=rofi_input_str, capture_output=True, text=True
    )

    if not rofi_process or rofi_process.returncode != 0:
        print("Selección cancelada.")
        return

    # La salida de rofi es solo el texto, sin la parte del icono
    selected_filename = rofi_process.stdout.strip()
    selected_image_path = image_map.get(selected_filename)

    if selected_image_path:
        # Al seleccionar, se aplica directamente el fondo.
        set_wallpaper(selected_image_path, config)
    else:
        print(f"Error: No se encontró la imagen para '{selected_filename}'", file=sys.stderr)

def print_help():
    """Imprime un mensaje de ayuda detallado."""
    script_name = "sway-wallpaper"
    print(f"Gestor de fondos de pantalla para Sway con miniaturas en Rofi.")
    print("\nUso:")
    print(f"  {script_name}                - Inicia en modo interactivo con rofi.")
    print(f"  {script_name} --auto         - Inicia el modo de rotación automática.")
    print(f"  {script_name} --set <ruta>   - Establece un fondo de pantalla específico.")
    print(f"  {script_name} --help, -h     - Muestra este mensaje de ayuda.")
    print("\nConfiguración:")
    print(f"  El archivo de configuración se encuentra en: {utils.CONFIG_FILE}")

def main():
    """Punto de entrada principal."""
    utils.check_dependencies()
    config = utils.get_config()
    args = sys.argv[1:]

    if not args:
        main_interactive(config)
    elif args[0] in ['--help', '-h']:
        print_help()
    elif args[0] == '--auto':
        automode.start_auto_mode(config, utils.get_image_files, set_wallpaper)
    elif args[0] == '--set' and len(args) > 1:
        image_path = Path(args[1]).expanduser()
        if image_path.is_file():
            set_wallpaper(image_path, config)
        else:
            error_msg = f"El archivo '{image_path}' no existe."
            print(error_msg, file=sys.stderr)
            utils.send_notification("Error", error_msg, "dialog-error")
    else:
        print(f"Argumento no válido: '{args[0]}'. Usa '--help' para ver las opciones.", file=sys.stderr)

if __name__ == "__main__":
    main()
