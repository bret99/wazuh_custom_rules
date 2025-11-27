#!/bin/bash

# Dependecies installing for System Information Collector
# Support: Alt Linux, RedOS, Ubuntu, Debian, CentOS, AlmaLinux, Rocky Linux, etc.

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${GREEN}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

detect_distro() {
    if [ -f /etc/altlinux-release ]; then
        echo "alt"
    elif [ -f /etc/redos-release ] || [ -f /etc/redos/redos-release ]; then
        echo "redos"
    elif [ -f /etc/centos-release ]; then
        echo "centos"
    elif [ -f /etc/almalinux-release ]; then
        echo "almalinux"
    elif [ -f /etc/rocky-release ]; then
        echo "rocky"
    elif [ -f /etc/fedora-release ]; then
        echo "fedora"
    elif [ -f /etc/debian_version ]; then
        echo "debian"
    elif [ -f /etc/lsb-release ] && grep -q "Ubuntu" /etc/lsb-release; then
        echo "ubuntu"
    elif [ -f /etc/arch-release ]; then
        echo "arch"
    elif [ -f /etc/SuSE-release ]; then
        echo "suse"
    else
        echo "unknown"
    fi
}

check_command() {
    command -v $1 >/dev/null 2>&1
}

# Installing for Alt Linux, RedOS, CentOS, AlmaLinux, Rocky (yum-based)
install_yum_deps() {
    info "Installing dependencies using yum..."
    
    # Base way
    if check_command yum; then
        yum update -y
        yum install -y python3 python3-pip sqlite
        
        # Alternative way with dnf if yum does not work
        if [ $? -ne 0 ] && check_command dnf; then
            warn "yum failed, trying dnf..."
            dnf update -y
            dnf install -y python3 python3-pip sqlite
        fi
    elif check_command dnf; then
        warn "yum not found, using dnf..."
        dnf update -y
        dnf install -y python3 python3-pip sqlite
    else
        error "Neither yum nor dnf found!"
        return 1
    fi
    
    if ! check_command python3; then
        warn "python3 not found in PATH, trying alternative packages..."
        yum install -y python36 python36-pip || dnf install -y python36 python36-pip
    fi
}

# Installing for Debian, Ubuntu (apt-based)
install_apt_deps() {
    info "Installing dependencies using apt..."
    
    apt-get update
    
    # Base way
    apt-get install -y python3 python3-pip sqlite3
    
    # Alternative way
    if [ $? -ne 0 ]; then
        warn "Main apt repositories failed, trying alternatives..."
        
        apt-get install -y python3
        apt-get install -y python3-pip
        apt-get install -y sqlite3
    fi
    
    if ! check_command pip3; then
        warn "pip3 not found, installing manually..."
        apt-get install -y python3-setuptools
        easy_install3 pip || curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3 get-pip.py
    fi
}

# Installing for Arch Linux
install_arch_deps() {
    info "Installing dependencies using pacman..."
    
    if check_command pacman; then
        pacman -Syu --noconfirm
        pacman -S --noconfirm python python-pip sqlite
    else
        error "pacman not found!"
        return 1
    fi
}

# Installing for openSUSE
install_suse_deps() {
    info "Installing dependencies using zypper..."
    
    if check_command zypper; then
        zypper refresh
        zypper install -y python3 python3-pip sqlite3
    else
        error "zypper not found!"
        return 1
    fi
}

install_pip_deps() {
    info "Installing Python dependencies..."
    
    if ! check_command pip3; then
        error "pip3 not found, cannot install Python dependencies"
        return 1
    fi
    
    local pip_packages=""
    
    pip3 install --upgrade pip
    
    pip3 install sqlite3
    
    python3 -c "import sqlite3" 2>/dev/null
    if [ $? -ne 0 ]; then
        warn "sqlite3 not available in Python, trying alternative packages..."
        
        pip3 install pysqlite3 || pip3 install sqlite3-python || pip3 install db-sqlite3
        
        local distro=$(detect_distro)
        case $distro in
            debian|ubuntu)
                apt-get install -y python3-sqlite3 libsqlite3-dev
                ;;
            alt|redos|centos|almalinux|rocky|fedora)
                yum install -y python3-sqlite3 sqlite-devel || dnf install -y python3-sqlite3 sqlite-devel
                ;;
            arch)
                pacman -S --noconfirm sqlite
                ;;
        esac
    fi
    
    info "Python dependencies installed successfully"
}

verify_installation() {
    info "Verifying installation..."
    
    local success=0
    
    if check_command python3; then
        info "Python3: OK"
        python3 --version
    else
        error "Python3: NOT FOUND"
        success=1
    fi
    
    if check_command pip3; then
        info "pip3: OK"
        pip3 --version
    else
        warn "pip3: NOT FOUND (some features may not work)"
    fi
    
    if check_command sqlite3; then
        info "SQLite: OK"
        sqlite3 --version
    else
        warn "SQLite: NOT FOUND (some features may not work)"
    fi
    
    if python3 -c "import sqlite3; import json; import glob; import hashlib; import logging; from datetime import datetime; print('All Python modules: OK')" 2>/dev/null; then
        info "Python modules: OK"
    else
        error "Some Python modules are missing"
        success=1
    fi
    
    return $success
}

install_python_manual() {
    warn "Attempting manual Python installation..."

    local python_version="3.9.18"
    local install_dir="/usr/local/python3"
    
    info "Downloading Python $python_version..."
    cd /tmp
    wget https://www.python.org/ftp/python/$python_version/Python-$python_version.tgz || \
    curl -O https://www.python.org/ftp/python/$python_version/Python-$python_version.tgz
    
    if [ -f "Python-$python_version.tgz" ]; then
        tar xzf Python-$python_version.tgz
        cd Python-$python_version
        
        info "Compiling Python..."
        ./configure --prefix=$install_dir --enable-optimizations
        make -j$(nproc)
        make altinstall

        ln -sf $install_dir/bin/python3.9 /usr/local/bin/python3
        ln -sf $install_dir/bin/pip3.9 /usr/local/bin/pip3
        
        info "Manual Python installation completed"
    else
        error "Failed to download Python"
        return 1
    fi
}

main() {
    info "Starting dependency installation for System Information Collector..."
    
    if [ "$EUID" -ne 0 ]; then
        error "Please run as root"
        exit 1
    fi
    
    local distro=$(detect_distro)
    info "Detected distribution: $distro"

    case $distro in
        alt|redos|centos|almalinux|rocky|fedora)
            install_yum_deps
            ;;
        debian|ubuntu)
            install_apt_deps
            ;;
        arch)
            install_arch_deps
            ;;
        suse)
            install_suse_deps
            ;;
        *)
            warn "Unknown distribution, trying generic installation..."
            
            if check_command yum; then
                install_yum_deps
            elif check_command apt-get; then
                install_apt_deps
            elif check_command pacman; then
                install_arch_deps
            elif check_command zypper; then
                install_suse_deps
            else
                error "No supported package manager found!"
            fi
            ;;
    esac

    if ! check_command python3; then
        warn "Python3 not installed by package manager, attempting manual installation..."
        install_python_manual
    fi
    
    install_pip_deps

    if verify_installation; then
        info "Dependency installation completed successfully!"
        info "System Information Collector is ready to use."
    else
        error "Dependency installation completed with errors."
        error "Some features may not work properly."
        exit 1
    fi
}

trap 'error "Installation interrupted"; exit 1' INT TERM

main "$@"
