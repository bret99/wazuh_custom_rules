#!/bin/bash

# Скрипт установки службы сбора истории браузеров
# Поддерживает: Alt Linux, RedOS, Ubuntu, Debian, CentOS, etc.

set -e

SCRIPT_NAME="systeminfocollect.py"
SERVICE_NAME="systeminfocollect"
INSTALL_DIR="/opt/systeminfocollect"
LOG_DIR="/var/log"
SERVICE_USER="root"
DEPS_SCRIPT="install_dependencies.sh"

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Проверка зависимостей
check_dependencies() {
    info "Checking dependencies..."
    
    local missing_deps=()
    
    # Проверяем Python
    if ! command -v python3 >/dev/null 2>&1; then
        missing_deps+=("python3")
    fi
    
    # Проверяем SQLite
    if ! python3 -c "import sqlite3" 2>/dev/null; then
        missing_deps+=("python3-sqlite3")
    fi
    
    # Проверяем остальные модули Python
    if ! python3 -c "import json; import glob; import hashlib; import logging; from datetime import datetime" 2>/dev/null; then
        missing_deps+=("python3-standard-library")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        warn "Missing dependencies: ${missing_deps[*]}"
        return 1
    else
        info "All dependencies are satisfied"
        return 0
    fi
}

# Установка зависимостей
install_dependencies() {
    info "Installing dependencies..."
    
    # Если есть скрипт установки зависимостей, используем его
    if [ -f "$DEPS_SCRIPT" ]; then
        info "Using dependency installation script..."
        chmod +x "$DEPS_SCRIPT"
        if "./$DEPS_SCRIPT"; then
            info "Dependencies installed successfully"
            return 0
        else
            error "Dependency script failed"
            return 1
        fi
    else
        warn "Dependency script not found, trying system package manager..."
        
        # Базовая установка через системный пакетный менеджер
        if command -v apt-get >/dev/null 2>&1; then
            apt-get update
            apt-get install -y python3 python3-pip sqlite3
        elif command -v yum >/dev/null 2>&1; then
            yum install -y python3 python3-pip sqlite
        elif command -v dnf >/dev/null 2>&1; then
            dnf install -y python3 python3-pip sqlite
        elif command -v pacman >/dev/null 2>&1; then
            pacman -Syu --noconfirm python python-pip sqlite
        else
            error "No supported package manager found"
            return 1
        fi
    fi
}

# Создаем директории
create_directories() {
    info "Creating directories..."
    mkdir -p $INSTALL_DIR
    mkdir -p $LOG_DIR
    chmod 755 $INSTALL_DIR
}

# Копируем файлы
copy_files() {
    info "Copying files..."
    cp $SCRIPT_NAME $INSTALL_DIR/
    chmod +x $INSTALL_DIR/$SCRIPT_NAME
    
    # Копируем скрипт зависимостей если есть
    if [ -f "$DEPS_SCRIPT" ]; then
        cp "$DEPS_SCRIPT" $INSTALL_DIR/
        chmod +x $INSTALL_DIR/$DEPS_SCRIPT
    fi
    
    chown -R $SERVICE_USER:$SERVICE_USER $INSTALL_DIR
}

# Создаем службу для systemd
create_systemd_service() {
    info "Creating systemd service..."
    
    cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=System Information Collector (Browser History)
After=network.target

[Service]
Type=oneshot
User=root
ExecStart=/usr/bin/python3 $INSTALL_DIR/$SCRIPT_NAME
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    cat > /etc/systemd/system/$SERVICE_NAME.timer << EOF
[Unit]
Description=Run System Information Collector hourly
Requires=$SERVICE_NAME.service

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
EOF

    systemctl daemon-reload
    systemctl enable $SERVICE_NAME.timer
    systemctl start $SERVICE_NAME.timer
}

# Создаем службу для cron (универсальный способ)
create_cron_job() {
    info "Creating cron job..."
    
    # Добавляем задание в crontab
    (crontab -l 2>/dev/null | grep -v "$INSTALL_DIR/$SCRIPT_NAME"; \
     echo "0 * * * * /usr/bin/python3 $INSTALL_DIR/$SCRIPT_NAME") | crontab -
    
    info "Cron job installed to run hourly"
}

# Проверяем права
check_permissions() {
    info "Setting permissions..."
    touch $LOG_DIR/systeminfocollect.json
    chmod 644 $LOG_DIR/systeminfocollect.json
    chown $SERVICE_USER:$SERVICE_USER $LOG_DIR/systeminfocollect.json
    
    # Создаем лог файл
    touch $LOG_DIR/systeminfocollect.log
    chmod 644 $LOG_DIR/systeminfocollect.log
    chown $SERVICE_USER:$SERVICE_USER $LOG_DIR/systeminfocollect.log
}

# Основная установка
main() {
    info "Starting System Information Collector installation..."
    
    # Проверяем права
    if [ "$EUID" -ne 0 ]; then
        error "Please run as root"
        exit 1
    fi
    
    # Проверяем и устанавливаем зависимости
    if ! check_dependencies; then
        warn "Some dependencies are missing, attempting to install..."
        if ! install_dependencies; then
            error "Failed to install dependencies"
            exit 1
        fi
    fi
    
    # Создаем директории
    create_directories
    
    # Копируем файлы
    copy_files
    
    # Пробуем установить systemd службу
    if systemctl --version &>/dev/null; then
        info "Systemd detected, installing service..."
        create_systemd_service
    else
        info "Systemd not found, using cron..."
        create_cron_job
    fi
    
    # Настраиваем права
    check_permissions
    
    info "Installation completed successfully!"
    info "Service: $SERVICE_NAME"
    info "Install directory: $INSTALL_DIR"
    info "Data file: $LOG_DIR/systeminfocollect.json"
    info "Service log: $LOG_DIR/systeminfocollect.log"
    echo ""
    info "To check status:"
    if systemctl --version &>/dev/null; then
        echo "  systemctl status $SERVICE_NAME.timer"
        echo "  systemctl list-timers $SERVICE_NAME.timer"
    else
        echo "  crontab -l"
    fi
    echo ""
    info "To view collected data:"
    echo "  tail -f $LOG_DIR/systeminfocollect.json"
}

main "$@"
