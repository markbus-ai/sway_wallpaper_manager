# Sway Wallpaper Manager

Gestor de fondos de pantalla para Sway, con selección interactiva vía Rofi, rotación automática y persistencia.

## 🚀 Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/markbus-ai/sway_wallpaper_manager.git
    cd sway_wallpaper_manager
    ```
2.  **Ejecutar el script de instalación:**
    Este script verificará e instalará las dependencias necesarias (para Arch Linux) y configurará el comando `sway-wallpaper` en tu `$HOME/.local/bin`.
    ```bash
    ./install.sh
    ```
    Durante la instalación, se te preguntará si deseas configurar la persistencia del modo automático.

## 💡 Uso Básico

El script principal se ejecuta con el comando `sway-wallpaper`.

*   **Modo Interactivo (Rofi):**
    Lanza Rofi con miniaturas de tus fondos de pantalla. Selecciona uno para aplicarlo.
    ```bash
    sway-wallpaper
    ```

*   **Establecer un Fondo Específico:**
    Aplica una imagen directamente.
    ```bash
    sway-wallpaper --set /ruta/a/tu/imagen.jpg
    ```
    Puedes usar rutas absolutas o relativas a tu directorio home (ej. `~/Imágenes/fondo.png`).

*   **Modo Automático:**
    Inicia la rotación automática de fondos de pantalla según el intervalo configurado en `config.ini`.
    ```bash
    sway-wallpaper --auto
    ```

*   **Modo Silencioso:**
    Suprime las notificaciones de escritorio para los comandos `--set` y `--auto`.
    ```bash
    sway-wallpaper --set /ruta/a/tu/imagen.jpg --quiet
    sway-wallpaper --auto --quiet
    ```

*   **Ver Versión:**
    Muestra la versión actual del script.
    ```bash
    sway-wallpaper --version
    ```

*   **Ayuda:**
    Muestra un mensaje de ayuda con todas las opciones.
    ```bash
    sway-wallpaper --help
    ```

## ⚙️ Configuración

El archivo de configuración principal es `config.ini`, ubicado en el mismo directorio del script.

```ini
# Ejemplo de config.ini
[Settings]
wallpaper_folder = ~/wallpaper          ; Carpeta donde se encuentran tus fondos.
rotation_interval_minutes = 30          ; Intervalo en minutos para el modo automático.
rotation_order = random                 ; Orden de rotación: 'random' o 'sequential'.
swaybg_output = *                       ; Monitor al que aplicar el fondo (ej. 'eDP-1', '*' para todos).
swaybg_mode = fill                      ; Modo de ajuste de la imagen: stretch, fill, fit, center, tile.
```

## 🔄 Persistencia

El script permite que tu fondo de pantalla actual o el modo automático se restauren automáticamente cada vez que inicias Sway.

*   **Habilitar Persistencia:**
    Usa la opción `--persist` junto con `--set` o `--auto`. Esto creará un script `~/.config/sway-wallpaper-manager/restore.sh` y añadirá una línea `exec_always` a tu archivo de configuración de Sway (`~/.config/sway/config`).

    ```bash
    sway-wallpaper --set /ruta/a/tu/imagen.png --persist
    sway-wallpaper --auto --persist
    ```

*   **Deshabilitar Persistencia:**
    Elimina el script de restauración y la línea `exec_always` de tu configuración de Sway.
    ```bash
    sway-wallpaper --disable-persist
    ```

## ⚠️ Errores Comunes

*   **Dependencias Faltantes:**
    Si el script no se ejecuta o muestra errores de comandos no encontrados (`swaybg`, `rofi`, `wal`, `notify-send`, `convert`), asegúrate de que todas las dependencias estén instaladas. El script `install.sh` intenta gestionarlas automáticamente en Arch Linux.

*   **Carpeta de Fondos no Encontrada:**
    Verifica que la ruta especificada en `wallpaper_folder` en `config.ini` sea correcta y que la carpeta exista.

*   **Tipo de Archivo no Soportado:**
    Asegúrate de que las imágenes que intentas establecer tengan una extensión soportada (JPG, PNG, GIF, BMP, SVG, WEBP, TIFF, AVIF, HEIC).

*   **Problemas con Rofi:**
    Si Rofi no se ve correctamente, verifica tu instalación de Rofi y asegúrate de que no haya configuraciones de tema conflictivas. El script intenta aplicar un tamaño de ventana y fuente básicos.

*   **Error al Modificar Configuración de Sway:**
    Si el script no puede modificar tu `~/.config/sway/config` para la persistencia, verifica los permisos del archivo.
