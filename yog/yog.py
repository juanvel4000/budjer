import os
import subprocess
import sys

user_dir = os.path.expanduser('~')
yogdir = os.path.join(user_dir, '.yog')

# Ensure the .yog directory exists
if not os.path.isdir(yogdir):
    os.mkdir(yogdir)

# Prevent running as root
if os.getuid() == 0:
    print("E: yogurt will not work as sudo/root")
    sys.exit(1)

def makepkg():
    try:
        subprocess.run(['makepkg', '-si'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error while making package: {e}")

def download(package, server):
    try:
        subprocess.run(['git', 'clone', f'{server}/{package}.git'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error while downloading package: {e}")

def install(package, server):
    download(package, server)
    os.chdir(package)
    makepkg()

def remove(package):
    try:
        subprocess.run(['sudo', 'pacman', '-Rns', package], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error while removing package: {e}")

def main():
    if len(sys.argv) < 3:
        print("Usage: yog <install|remove|install-other> <package> [server]")
        sys.exit(1)

    action = sys.argv[1]
    package = sys.argv[2]

    os.chdir(yogdir)

    if action == "install":
        install(package, 'https://aur.archlinux.org')
    elif action == "remove":
        remove(package)
    elif action == "install-other":
        if len(sys.argv) < 4:
            print("Usage: yog install-other <package> <server>")
            sys.exit(1)
        server = sys.argv[3]
        install(package, server)
    elif action == "-v":
        print("yogurt AUR Helper")
        print("Version: 0.2")
    else:
        print("Usage: yog <install|remove|install-other> <package> [server]")

if __name__ == "__main__":
    main()
