#!/bin/bash

# PowerEdu-AI 系统依赖安装脚本
# 为Linux服务器环境安装必要的系统依赖

set -e

echo "🔧 PowerEdu-AI 系统依赖安装脚本"
echo "====================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检测操作系统
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
    elif type lsb_release >/dev/null 2>&1; then
        OS=$(lsb_release -si)
        VER=$(lsb_release -sr)
    elif [ -f /etc/redhat-release ]; then
        OS="Red Hat Enterprise Linux"
        VER=$(cat /etc/redhat-release | sed 's/.*release \([0-9]\+\).*/\1/')
    else
        OS=$(uname -s)
        VER=$(uname -r)
    fi
    
    log_info "检测到操作系统: $OS $VER"
}

# Ubuntu/Debian系统安装
install_ubuntu_deps() {
    log_info "为Ubuntu/Debian系统安装依赖..."
    
    # 更新包索引
    log_info "更新包索引..."
    sudo apt-get update
    
    # 安装Python相关依赖
    log_info "安装Python依赖..."
    sudo apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        python3-setuptools \
        python3-wheel
    
    # 安装编译工具
    log_info "安装编译工具..."
    sudo apt-get install -y \
        build-essential \
        gcc \
        g++ \
        make \
        cmake \
        pkg-config
    
    # 安装系统工具
    log_info "安装系统工具..."
    sudo apt-get install -y \
        curl \
        wget \
        git \
        lsof \
        htop \
        unzip
    
    # 安装Node.js
    install_nodejs_ubuntu
}

# CentOS/RHEL系统安装
install_centos_deps() {
    log_info "为CentOS/RHEL系统安装依赖..."
    
    # 安装EPEL源
    if ! rpm -qa | grep -q epel-release; then
        log_info "安装EPEL源..."
        sudo yum install -y epel-release
    fi
    
    # 更新系统
    log_info "更新系统包..."
    sudo yum update -y
    
    # 安装Python相关依赖
    log_info "安装Python依赖..."
    sudo yum install -y \
        python3 \
        python3-pip \
        python3-devel \
        python3-setuptools \
        python3-wheel
    
    # 安装编译工具
    log_info "安装编译工具..."
    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y \
        gcc \
        gcc-c++ \
        make \
        cmake \
        pkgconfig
    
    # 安装系统工具
    log_info "安装系统工具..."
    sudo yum install -y \
        curl \
        wget \
        git \
        lsof \
        htop \
        unzip
    
    # 安装Node.js
    install_nodejs_centos
}

# Fedora系统安装
install_fedora_deps() {
    log_info "为Fedora系统安装依赖..."
    
    # 更新系统
    log_info "更新系统包..."
    sudo dnf update -y
    
    # 安装Python相关依赖
    log_info "安装Python依赖..."
    sudo dnf install -y \
        python3 \
        python3-pip \
        python3-devel \
        python3-setuptools \
        python3-wheel
    
    # 安装编译工具
    log_info "安装编译工具..."
    sudo dnf groupinstall -y "Development Tools"
    sudo dnf install -y \
        gcc \
        gcc-c++ \
        make \
        cmake \
        pkgconfig
    
    # 安装系统工具
    log_info "安装系统工具..."
    sudo dnf install -y \
        curl \
        wget \
        git \
        lsof \
        htop \
        unzip \
        nodejs \
        npm
}

# Ubuntu安装Node.js
install_nodejs_ubuntu() {
    if command -v node >/dev/null 2>&1; then
        log_info "Node.js已安装: $(node --version)"
        return
    fi
    
    log_info "安装Node.js..."
    
    # 尝试使用NodeSource官方源
    if curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -; then
        sudo apt-get install -y nodejs
    else
        log_warning "NodeSource安装失败，使用系统源..."
        sudo apt-get install -y nodejs npm
        
        # 如果系统源版本太老，尝试snap安装
        if ! node --version | grep -q "v1[8-9]\|v[2-9][0-9]"; then
            log_warning "系统Node.js版本过旧，尝试snap安装..."
            if command -v snap >/dev/null 2>&1; then
                sudo snap install node --classic
            fi
        fi
    fi
}

# CentOS安装Node.js
install_nodejs_centos() {
    if command -v node >/dev/null 2>&1; then
        log_info "Node.js已安装: $(node --version)"
        return
    fi
    
    log_info "安装Node.js..."
    
    # 尝试使用NodeSource官方源
    if curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -; then
        sudo yum install -y nodejs
    else
        log_warning "NodeSource安装失败，使用系统源..."
        sudo yum install -y nodejs npm
    fi
}

# 验证安装
verify_installation() {
    log_info "验证安装结果..."
    
    local all_good=true
    
    # 检查Python
    if command -v python3 >/dev/null 2>&1; then
        log_success "Python3: $(python3 --version)"
    else
        log_error "Python3未正确安装"
        all_good=false
    fi
    
    # 检查pip
    if command -v pip3 >/dev/null 2>&1; then
        log_success "pip3: $(pip3 --version | cut -d' ' -f1-2)"
    else
        log_error "pip3未正确安装"
        all_good=false
    fi
    
    # 检查Python venv模块
    if python3 -c "import venv" 2>/dev/null; then
        log_success "Python venv模块可用"
    else
        log_error "Python venv模块不可用"
        all_good=false
    fi
    
    # 检查Node.js
    if command -v node >/dev/null 2>&1; then
        log_success "Node.js: $(node --version)"
    else
        log_error "Node.js未正确安装"
        all_good=false
    fi
    
    # 检查npm
    if command -v npm >/dev/null 2>&1; then
        log_success "npm: $(npm --version)"
    else
        log_error "npm未正确安装"
        all_good=false
    fi
    
    if $all_good; then
        log_success "所有依赖安装完成！"
        echo ""
        log_info "现在可以运行以下命令启动PowerEdu-AI："
        echo "   ./start-linux-server.sh"
        return 0
    else
        log_error "部分依赖安装失败，请检查错误信息"
        return 1
    fi
}

# 主函数
main() {
    # 检查是否为root用户或具有sudo权限
    if [ "$EUID" -eq 0 ]; then
        log_warning "检测到root用户"
    elif ! sudo -n true 2>/dev/null; then
        log_error "需要sudo权限来安装系统依赖"
        echo "请确保当前用户在sudoers文件中，或者切换到root用户"
        exit 1
    fi
    
    # 检测操作系统
    detect_os
    
    # 根据操作系统安装依赖
    case "$OS" in
        *"Ubuntu"*|*"Debian"*)
            install_ubuntu_deps
            ;;
        *"CentOS"*|*"Red Hat"*|*"Rocky"*|*"AlmaLinux"*)
            install_centos_deps
            ;;
        *"Fedora"*)
            install_fedora_deps
            ;;
        *)
            log_error "不支持的操作系统: $OS"
            echo ""
            echo "请手动安装以下依赖："
            echo "- Python 3.8+"
            echo "- pip3"
            echo "- python3-venv"
            echo "- python3-dev"
            echo "- build-essential (gcc, g++, make)"
            echo "- Node.js 18+"
            echo "- npm"
            echo "- curl, wget, git, lsof"
            exit 1
            ;;
    esac
    
    # 验证安装
    verify_installation
}

# 执行主函数
main "$@"
