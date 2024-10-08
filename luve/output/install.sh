#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for root privileges
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root."
    exit 1
fi

# Check for common package managers and install required packages
install_packages() {
    if command_exists apt; then
        echo "Package manager: apt (Debian/Ubuntu)"
        apt install -y debootstrap arch-install-scripts || { echo "Installation failed!"; exit 1; }
    elif command_exists dnf; then
        echo "Package manager: dnf (Fedora)"
        dnf install -y debootstrap arch-install-scripts || { echo "Installation failed!"; exit 1; }
    elif command_exists pacman; then
        echo "Package manager: pacman (Arch Linux)"
        pacman -Sy --needed --noconfirm debootstrap arch-install-scripts || { echo "Installation failed!"; exit 1; }
    elif command_exists brew; then
        echo "Package manager: brew (Homebrew for macOS)"
        brew install debian-utils || { echo "Installation failed!"; exit 1; }
        echo "Warning: LUVE in macOS doesn't support Arch Linux Environments"
    else
        echo "No known package manager found."
        exit 1
    fi
}

# Main function
main() {
    clear
    cat << EOF
$$\      $$\   $$\ $$\    $$\ $$$$$$$$\       $$$$$$\                       $$\               $$\ $$\                     
$$ |     $$ |  $$ |$$ |   $$ |$$  _____|      \_$$  _|                      $$ |              $$ |$$ |                    
$$ |     $$ |  $$ |$$ |   $$ |$$ |              $$ |  $$$$$$$\   $$$$$$$\ $$$$$$\    $$$$$$\  $$ |$$ | $$$$$$\   $$$$$$\  
$$ |     $$ |  $$ |\$$\  $$  |$$$$$\            $$ |  $$  __$$\ $$  _____|\_$$  _|   \____$$\ $$ |$$ |$$  __$$\ $$  __$$\ 
$$ |     $$ |  $$ | \$$\$$  / $$  __|           $$ |  $$ |  $$ |\$$$$$$\    $$ |     $$$$$$$ |$$ |$$ |$$$$$$$$ |$$ |  \__|
$$ |     $$ |  $$ |  \$$$  /  $$ |              $$ |  $$ |  $$ | \____$$\   $$ |$$\ $$  __$$ |$$ |$$ |$$   ____|$$ |      
$$$$$$$$\\$$$$$$  |   \$  /   $$$$$$$$\       $$$$$$\ $$ |  $$ |$$$$$$$  |  \$$$$  |\$$$$$$$ |$$ |$$ |\$$$$$$$\ $$ |      
\________|\______/     \_/    \________|      \______|\__|  \__|\_______/    \____/  \_______|\__|\__| \_______|\__|      
EOF

    # Download the file and check for success
    curl -O https://juanvel4000.serv00.net/luve/vl || { echo "Failed to download vl"; exit 1; }
    
    # Move and check if the move was successful
    mv vl /bin/ || { echo "Failed to move vl to /bin/"; exit 1; }

    # Execute the downloaded script
    vl
}

# Run the functions
install_packages
main
