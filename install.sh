#!/bin/bash
# install.sh - Installation script for Claude Sync

set -e  # Exit immediately if a command exits with a non-zero status

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed. Please install Python 3 first."
    exit 1
fi

# Display banner
echo "==============================================="
echo "Claude Sync Installation"
echo "==============================================="

# Ask for virtual environment name
read -p "Enter virtual environment name (default: claude): " venv_name
venv_name=${venv_name:-claude}

# Check if virtual environment already exists
if [ -d "$venv_name" ]; then
    echo "Virtual environment '$venv_name' already exists."
    read -p "Do you want to use the existing environment? [Y/n]: " use_existing
    use_existing=${use_existing:-y}
    
    if [[ $use_existing =~ ^[Yy]$ ]]; then
        echo "Using existing virtual environment..."
    else
        read -p "Would you like to replace it? This will delete the existing environment. [y/N]: " replace_env
        replace_env=${replace_env:-n}
        
        if [[ $replace_env =~ ^[Yy]$ ]]; then
            echo "Removing existing environment..."
            rm -rf $venv_name
            echo "Creating new virtual environment '$venv_name'..."
            python3 -m venv $venv_name
        else
            echo "Installation cancelled."
            exit 0
        fi
    fi
else
    echo "Creating virtual environment '$venv_name'..."
    python3 -m venv $venv_name
fi

# Activate virtual environment
source $venv_name/bin/activate

echo "Installing required dependencies..."
pip install --upgrade pip setuptools wheel
pip install --upgrade requests pyperclip curl_cffi

echo "Installing Claude Sync..."
pip install --upgrade .

echo "Installation complete!"
echo ""
echo "To use Claude Sync:"
echo "1. Activate the virtual environment with:"
echo "   source $venv_name/bin/activate"
echo "2. Run any Claude Sync command, e.g.:"
echo "   claude-sync --status"
echo ""
echo "The first time you run it, you'll be guided through configuration."
echo "==============================================="