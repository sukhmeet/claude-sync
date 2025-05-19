#!/bin/bash
# install.sh - Installation script for Claude Sync with pyenv support

set -e  # Exit immediately if a command exits with a non-zero status

# Check if pyenv is installed
if ! command -v pyenv &> /dev/null; then
    echo "Error: pyenv is required but not installed. Please install pyenv first."
    echo "Visit: https://github.com/pyenv/pyenv#installation"
    exit 1
fi

# Check if pyenv-virtualenv is installed
if ! pyenv commands | grep -q virtualenv; then
    echo "Error: pyenv-virtualenv plugin is required but not installed."
    echo "Visit: https://github.com/pyenv/pyenv-virtualenv#installation"
    exit 1
fi

# Display banner
echo "==============================================="
echo "Claude Sync Installation (pyenv edition)"
echo "==============================================="

# Ask for virtual environment name
read -p "Enter pyenv virtual environment name (default: claude): " venv_name
venv_name=${venv_name:-claude}

# Get current active Python version
current_python=$(pyenv version-name)
read -p "Enter Python version to use (default: $current_python): " python_version
python_version=${python_version:-$current_python}

# Check if the Python version is installed
if ! pyenv versions --bare | grep -q "^$python_version$"; then
    echo "Python version $python_version is not installed."
    read -p "Would you like to install it now? [y/N]: " install_python
    install_python=${install_python:-n}
    
    if [[ $install_python =~ ^[Yy]$ ]]; then
        echo "Installing Python $python_version..."
        pyenv install $python_version
    else
        echo "Installation cancelled."
        exit 0
    fi
fi

# Check if virtual environment already exists
if pyenv versions --bare | grep -q "^$venv_name$"; then
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
            pyenv virtualenv-delete -f $venv_name
            echo "Creating new virtual environment '$venv_name'..."
            pyenv virtualenv $python_version $venv_name
        else
            echo "Installation cancelled."
            exit 0
        fi
    fi
else
    echo "Creating virtual environment '$venv_name'..."
    pyenv virtualenv $python_version $venv_name
fi

# Create a temporary activation script
temp_activation_script=$(mktemp)
cat > $temp_activation_script << EOF
#!/bin/bash
export PYENV_VERSION=$venv_name
EOF

# Source the temporary activation script to activate the environment for this session
source $temp_activation_script

echo "Temporarily activated pyenv environment '$venv_name'"
echo "Installing required dependencies..."

# Verify we're in the right environment
current_env=$(pyenv version-name)
if [ "$current_env" != "$venv_name" ]; then
    echo "Error: Failed to activate pyenv environment. Expected $venv_name, got $current_env"
    exit 1
fi

# Install requirements
pip install --upgrade pip setuptools wheel
pip install --upgrade requests pyperclip curl_cffi

echo "Installing Claude Sync..."
# Assuming we're in the project root directory
pip install --upgrade .

# Get the directory where the script is running
if [ -n "$BASH_SOURCE" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
elif [ -n "$ZSH_NAME" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
else
    SCRIPT_DIR="$(pwd)"
fi

# Ask about local directory activation
read -p "Would you like to set up automatic activation when you enter this directory? [y/N]: " setup_local_activation
setup_local_activation=${setup_local_activation:-n}

if [[ $setup_local_activation =~ ^[Yy]$ ]]; then
    # Create .python-version file for auto-activation
    echo "$venv_name" > "$SCRIPT_DIR/.python-version"
    echo "Created .python-version file. The environment will activate automatically when you enter this directory."
    
    # Check if shell integration is set up
    if ! grep -q "pyenv init" ~/.bashrc 2>/dev/null && ! grep -q "pyenv init" ~/.zshrc 2>/dev/null; then
        echo "Note: To enable automatic activation, you need to add pyenv init to your shell config."
        echo "For bash, add these lines to ~/.bashrc:"
        echo 'export PATH="$HOME/.pyenv/bin:$PATH"'
        echo 'eval "$(pyenv init -)"'
        echo 'eval "$(pyenv virtualenv-init -)"'
        echo ""
        echo "For zsh, add similar lines to ~/.zshrc"
        echo ""
        read -p "Would you like to add these lines to your shell config now? [y/N]: " setup_shell
        setup_shell=${setup_shell:-n}
        
        if [[ $setup_shell =~ ^[Yy]$ ]]; then
            # Determine shell
            if [ -n "$BASH_VERSION" ]; then
                SHELL_RC="$HOME/.bashrc"
            elif [ -n "$ZSH_VERSION" ]; then
                SHELL_RC="$HOME/.zshrc"
            else
                echo "Could not determine shell type. Please manually add pyenv init to your shell config."
                SHELL_RC=""
            fi
            
            if [ -n "$SHELL_RC" ]; then
                echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> "$SHELL_RC"
                echo 'eval "$(pyenv init -)"' >> "$SHELL_RC"
                echo 'eval "$(pyenv virtualenv-init -)"' >> "$SHELL_RC"
                echo "Added pyenv initialization to $SHELL_RC"
                echo "Please restart your shell or run: source $SHELL_RC"
            fi
        fi
    fi
fi

# Clean up
rm -f $temp_activation_script

echo "Installation complete!"
echo ""
echo "To use Claude Sync:"
echo "1. Activate the pyenv environment with:"
echo "   pyenv activate $venv_name"
echo "2. Run any Claude Sync command, e.g.:"
echo "   claude-sync --status"
echo ""
if [[ $setup_local_activation =~ ^[Yy]$ ]]; then
    echo "Note: The environment will activate automatically when you enter the directory"
    echo "      (if pyenv virtualenv-init is enabled in your shell)"
fi
echo "The first time you run it, you'll be guided through configuration."
echo "==============================================="