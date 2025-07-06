#!/bin/bash
# -------------------------------------------------------------------
# Script de Instalación para Sway Wallpaper Manager (Versión Mejorada)
# -------------------------------------------------------------------
# - Verifica e instala dependencias para Arch Linux.
# - Hace que el gestor de fondos sea accesible globalmente.
# -------------------------------------------------------------------

# --- Verificación de Dependencias ---
echo "🔎 Verificando dependencias..."

# Comprueba si el sistema es Arch Linux
if [ -f /etc/arch-release ]; then
    # Lista de paquetes necesarios en los repositorios de Arch
    REQUIRED_PACKAGES="swaybg rofi python-pywal libnotify imagemagick"
    PACKAGES_TO_INSTALL=""

    # Itera sobre cada paquete para ver si está instalado
    for pkg in $REQUIRED_PACKAGES; do
        # pacman -Q verifica si el paquete está en la base de datos local
        if ! pacman -Q "$pkg" &> /dev/null; then
            echo "  - Dependencia no encontrada: $pkg"
            PACKAGES_TO_INSTALL+="$pkg "
        fi
    done

    # Si hay paquetes en la lista de instalación, pregunta al usuario
    if [ -n "$PACKAGES_TO_INSTALL" ]; then
        echo "Algunas dependencias críticas no están instaladas."
        read -p "--> ¿Deseas instalarlas ahora con pacman? (S/n) " response

        # Si el usuario responde sí (o simplemente presiona Enter), instala
        if [[ "$response" =~ ^([sS][iI]?|[yY])$ || -z "$response" ]]; then
            echo "📦 Ejecutando: sudo pacman -S --noconfirm $PACKAGES_TO_INSTALL"
            # Necesitarás introducir tu contraseña para sudo
            sudo pacman -S --noconfirm $PACKAGES_TO_INSTALL
            if [ $? -ne 0 ]; then
                echo "❌ Error durante la instalación de dependencias. Abortando."
                exit 1
            fi
            echo "✅ Dependencias instaladas correctamente."
        else
            echo "🛑 Instalación de dependencias cancelada por el usuario."
            echo "Por favor, instálalas manualmente para continuar: sudo pacman -S $PACKAGES_TO_INSTALL"
            exit 1
        fi
    else
        echo "✅ Todas las dependencias ya están satisfechas."
    fi
else
    echo "⚠️ No se detectó Arch Linux. La verificación automática de dependencias fue omitida."
    echo "Asegúrate de tener instalados: swaybg, rofi, pywal, libnotify, imv."
fi

# --- Instalación del Script ---

# Directorio donde se instalará el comando para el usuario actual.
INSTALL_DIR="$HOME/.local/bin"

# Ubicación del script principal.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
MAIN_SCRIPT="main.py"
COMMAND_NAME="sway-wallpaper"

echo "
🚀 Instalando el gestor de fondos de pantalla..."

# 1. Asegurarse de que el directorio de instalación existe.
mkdir -p "$INSTALL_DIR"

# 2. Dar permisos de ejecución al script principal.
chmod +x "$SCRIPT_DIR/$MAIN_SCRIPT"

# 3. Crear un enlace simbólico para que el comando esté disponible globalmente.
ln -sf "$SCRIPT_DIR/$MAIN_SCRIPT" "$INSTALL_DIR/$COMMAND_NAME"

echo "
✅ ¡Instalación completada!"
echo "Ahora puedes usar el comando '$COMMAND_NAME' desde cualquier lugar de tu terminal."
echo "Asegúrate de que '$INSTALL_DIR' esté en tu variable de entorno PATH."