import os
import sys
import configparser
from luve import LUVE
import platform

# Initialize LUVE instance
luve = LUVE()

# Constants
LUVEDIR = "/usr/share/luve"
CONFIGDIR = os.path.join(LUVEDIR, "cfg")
IMGDIR = os.path.join(LUVEDIR, "img")
MOUNTDIR = os.path.join(LUVEDIR, "mount")

# Check for root and platform compatibility
if os.getuid() != 0:
    sys.exit("Please run as root.")
if platform.system() in ["Windows", "Darwin"]:
    sys.exit("LUVE only works on GNU/Linux Systems or WSL2.")

# Create necessary directories if they don't exist
for directory in [CONFIGDIR, IMGDIR, MOUNTDIR]:
    os.makedirs(directory, exist_ok=True)

# Basic Functions
def create_luve(name, distro, size):
    image = os.path.join(IMGDIR, f"{name}.luve")
    mount = os.path.join(MOUNTDIR, f"{name}-mount")
    
    os.makedirs(mount, exist_ok=True)
    luve.imagebuilder(image, size, name)

    with open(os.path.join(CONFIGDIR, f"{name}.conf"), 'w') as f:
        f.write(f'; Config for {name}\n[LUVE]\n')
        f.write(f'mountpoint = {mount}\nimage = {image}\nname = {name}\ndistro = {distro}\n')

    luve.installsystem(image, mount, distro)
    luve.chrootsys(mount)
    luve.umount(mount)

def chroot(name):
    config = configparser.ConfigParser()
    config.read(os.path.join(CONFIGDIR, f"{name}.conf"))
    mountpoint = config['LUVE']['mountpoint']
    image = config['LUVE']['image']
    
    luve.mount(mountpoint, image)
    os.system("clear")
    luve.chrootsys(mountpoint)
    luve.umount(mountpoint)

def install(name, package):
    config = configparser.ConfigParser()
    config.read(os.path.join(CONFIGDIR, f"{name}.conf"))
    mountpoint = config['LUVE']['mountpoint']
    image = config['LUVE']['image']
    distro = config['LUVE']['distro']
    
    luve.mount(mountpoint, image)
    if distro == "arch":
        luve.chrootsys(mountpoint, f"pacman -Sy {package}")
    else:  # Assume 'debian'
        luve.chrootsys(mountpoint, "apt update")
        luve.chrootsys(mountpoint, f"apt install -y {package}")
    luve.umount(mountpoint)

def settings(name):
    config = configparser.ConfigParser()
    config.read(os.path.join(CONFIGDIR, f"{name}.conf"))
    distro = config['LUVE']['distro']
    
    options = {
        "1": "Reinstall the system on",
        "2": f"Wipe out and install {'Debian' if distro == 'arch' else 'Arch Linux'}",
        "3": f"Delete {name}",
        "4": "Exit Settings."
    }
    
    print("\n".join([f"{key}. {value} {name}" for key, value in options.items()]))
    selection = input("Choose (1-4): ")

    if selection == "1":
        nsize = input(f"Select a new size for {name} (In Megabytes): ")
        os.remove(os.path.join(IMGDIR, f"{name}.luve"))
        create_luve(name, distro, nsize)
    elif selection == "2":
        ndistro = "debian" if distro == "arch" else "arch"
        nsize = input(f"Select a new size for {name} (In Megabytes): ")
        os.remove(os.path.join(IMGDIR, f"{name}.luve"))
        os.remove(os.path.join(CONFIGDIR, f"{name}.conf"))
        create_luve(name, ndistro, nsize)
    elif selection == "3":
        mountpoint = config['LUVE']['mountpoint']
        image = config['LUVE']['image']
        os.rmdir(mountpoint)  # Use rmdir instead of removing file
        os.remove(image)
        os.remove(os.path.join(CONFIGDIR, f"{name}.conf"))

def list_envs():
    return [os.path.splitext(file)[0] for file in os.listdir(CONFIGDIR) if file.endswith('.conf')]

def display_menu():
    ascii_art = r"""
           $$\ 
           $$ |      Version 0.1
$$\    $$\ $$ |      LUVE Version: 0.09
\$$\  $$  |$$ |      
 \$$\$$  / $$ |      
  \$$$  /  $$ |      
   \$  /   $$$$$$$$\ 
    \_/    \________|
    """ 
    os.system("clear")
    print(ascii_art)
    print("Welcome to vL")
    print("1. Create a new LUVE Environment")
    print("2. Enter a LUVE Environment")
    print("3. Configure a LUVE Environment")
    print("4. Install a package in a LUVE Environment")
    print("5. Exit.")

def main():
    while True:
        display_menu()
        selection = input("Your choice (1-5): ")

        if selection == "1":
            name = input("Enter a name for your LUVE Environment: ")
            size = input("Enter a size for your LUVE Environment: ")
            distro = "arch" if input("Choose a Distribution (1: Arch Linux, 2: Debian): ") == "1" else "debian"
            create_luve(name, distro, size)
        elif selection == "2":
            print("Available LUVE Environments:")
            environments = list_envs()
            for env in environments:
                print(env)
            if environments:  # Only prompt if there are environments
                chroot(input("Choose an Environment: "))
            else:
                print("No LUVE environments available.")
        elif selection == "3":
            print("LUVE Settings")
            environments = list_envs()
            for env in environments:
                print(env)
            if environments:  # Only prompt if there are environments
                settings(input("Choose an Environment: "))
            else:
                print("No LUVE environments available.")
        elif selection == "4":
            print("LUVE Package Installer")
            environments = list_envs()
            for env in environments:
                print(env)
            if environments:  # Only prompt if there are environments
                package = input("What packages do you want to install? (Separated by spaces): ")
                install(input("Choose an Environment: "), package)
            else:
                print("No LUVE environments available.")
        elif selection == "5":
            sys.exit()
        else:
            print("Invalid selection. Please try again.")

if __name__ == "__main__":
    main()
