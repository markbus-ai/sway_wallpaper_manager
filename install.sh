# -------------------------------------------------------------------
# Script de Instalación para Sway Wallpaper Manager (Versión Mejorada)
# -------------------------------------------------------------------
# - Verifica e instala dependencias para Arch Linux.
# - Hace que el gestor de fondos sea accesible globalmente.
# - Configura un servicio de systemd para el modo automático persistente.
# -------------------------------------------------------------------

# --- Verificación de Dependencias ---
echo "🔎 Verificando dependencias..."

# Comprueba si el sistema es Arch Linux
if [ -f /etc/arch-release ]; then
    REQUIRED_PACKAGES="swaybg rofi python-pywal libnotify imagemagick"
    PACKAGES_TO_INSTALL=""

    for pkg in $REQUIRED_PACKAGES; do
        if ! pacman -Q "$pkg" &> /dev/null; then
            echo "  - Dependencia no encontrada: $pkg"
            PACKAGES_TO_INSTALL+="$pkg "
        fi
    done

    if [ -n "$PACKAGES_TO_INSTALL" ]; then
        echo "Algunas dependencias críticas no están instaladas."
        read -p "--> ¿Deseas instalarlas ahora con pacman? (S/n) " response

        if [[ "$response" =~ ^([sS][iI]?|[yY])$ || -z "$response" ]]; then
            echo "📦 Ejecutando: sudo pacman -S --noconfirm $PACKAGES_TO_INSTALL"
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

echo -e "\n🚀 Instalando el gestor de fondos de pantalla..."

# 1. Asegurarse de que el directorio de instalación existe.
mkdir -p "$INSTALL_DIR"

# 2. Dar permisos de ejecución al script principal.
chmod +x "$SCRIPT_DIR/$MAIN_SCRIPT"

# 3. Crear un enlace simbólico para que el comando esté disponible globalmente.
ln -sf "$SCRIPT_DIR/$MAIN_SCRIPT" "$INSTALL_DIR/$COMMAND_NAME"

echo "✅ ¡Script instalado en '$INSTALL_DIR/$COMMAND_NAME'!"

# --- Configuración del Modo Automático Persistente (Opcional) ---
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SYSTEMD_USER_DIR/sway-wallpaper-automode.service"
SCRIPT_ABS_PATH="$SCRIPT_DIR/$MAIN_SCRIPT"

echo -e "\n✨ ¿Deseas que el modo automático se inicie con tu sesión? (Opcional)"
read -p "Esto creará un servicio de systemd para ejecutar el script en segundo plano. (S/n) " response

if [[ "$response" =~ ^([sS][iI]?|[yY])$ || -z "$response" ]]; then
    echo "🔧 Configurando el servicio de systemd..."

    mkdir -p "$SYSTEMD_USER_DIR"

    echo "📝 Escribiendo el archivo de servicio en '$SERVICE_FILE'..."
    cat > "$SERVICE_FILE" << EOL
[Unit]
Description=Sway Wallpaper Manager - Modo Automático
After=graphical-session.target
PartOf=graphical-session.target

[Service]
Type=simple
ExecStart=$SCRIPT_ABS_PATH --auto --quiet
Restart=on-failure
RestartSec=15

[Install]
WantedBy=graphical-session.target
EOL

    echo "⚙️ Habilitando el servicio para que se inicie automáticamente..."
    systemctl --user daemon-reload
    systemctl --user enable --now sway-wallpaper-automode.service

    if [ $? -eq 0 ]; then
        echo "✅ ¡Servicio de modo automático habilitado y iniciado!"
        echo "Puedes gestionarlo con los siguientes comandos:"
        echo "   - Ver estado: systemctl --user status sway-wallpaper-automode"
        echo "   - Detener:    systemctl --user stop sway-wallpaper-automode"
        echo "   - Iniciar:    systemctl --user start sway-wallpaper-automode"
    else
        echo "❌ Error al habilitar el servicio de systemd."
        echo "Asegúrate de que tu sesión de usuario de systemd está activa."
    fi
else
    echo "ℹ️ Omitida la configuración del servicio de modo automático."
fi

echo -e "\n🎉 ¡Instalación completada!"
echo "Ahora puedes usar el comando '$COMMAND_NAME' desde tu terminal."
echo "Asegúrate de que '$INSTALL_DIR' esté en tu variable de entorno PATH."
"