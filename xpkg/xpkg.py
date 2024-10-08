import os
import sys
import subprocess
import platform
import logging
import tarfile
import configparser
import shutil

# Configure logging
xpkgdir = os.path.join(os.path.expanduser("~"), '.xpkg')
log_dir = os.path.join(xpkgdir, 'log')
log_file = os.path.join(log_dir, 'log.txt')
config = configparser.ConfigParser()

# Create directories if they don't exist
if not os.path.isdir(xpkgdir):
    os.mkdir(xpkgdir)

if not os.path.isdir(log_dir):
    os.mkdir(log_dir)

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("Starting XPKG")

# The Cross-Platform Package Manager

## Check System
current_os = platform.system()  # Fixed method call to get the OS
if current_os == "Darwin":
    os_type = "macos"
elif current_os == "Windows":
    os_type = "win32"
elif current_os == "Linux":
    os_type = "linux"
else:
    logging.error("Unsupported OS. Exiting.")
    sys.exit(1)

logging.info(f"Detected OS: {os_type}")

# Constants
home = os.path.expanduser("~")
software_dir = os.path.join(xpkgdir, 'software')

# Check Folders
if not os.path.isdir(xpkgdir):
    os.mkdir(f"{xpkgdir}/software")
    os.mkdir(f"{xpkgdir}/cfg")
    os.mkdir(f"{xpkgdir}/extra")
    logging.info(f"Created XPKG directory at {xpkgdir}")
    os.mkdir(software_dir)
    logging.info(f"Created software directory at {software_dir}")

    if os_type == "win32":
        current_path = os.environ['PATH']

        if xpkgdir in current_path:
            logging.warning(f"The XPKG directory is already in your PATH.")
        else:
            updated_path = current_path + ';' + xpkgdir
            subprocess.run(['setx', 'PATH', updated_path], shell=True)
            logging.info(f"Added {xpkgdir} to your PATH.")
    else:
        # For Unix-like systems (Linux, macOS)
        shell_config = ''
        if os_type == "macos":
            shell_config = os.path.join(home, '.zshrc')  # Assuming Zsh for macOS, adjust if needed
        else:  # Linux
            shell_config = os.path.join(home, '.bashrc')  # Assuming Bash for Linux

        # Check if the export command is already in the file
        with open(shell_config, 'r') as file:
            if f'export PATH="{xpkgdir}/bin:$PATH"' in file.read():
                logging.warning(f"The XPKG directory is already set in {shell_config}.")
            else:
                with open(shell_config, 'a') as file:
                    file.write(f'\nexport PATH="{xpkgdir}/bin:$PATH"\n')
                logging.info(f"Added {xpkgdir}/bin to your PATH in {shell_config}. Please run 'source {shell_config}' to apply the changes.")
else:
    logging.info(f"The XPKG directory ({xpkgdir}) already exists.")

# Set basic functions
def uncompress(package):
    # Check if the provided package is a valid .xpkg.tar.gz file
    if not package.endswith(".xpkg.tar.gz"):
        logging.error("The file is not a valid .xpkg.tar.gz package.")
        print("=> ERROR: The file is not a valid .xpkg.tar.gz package.")
        return
    
    # Get the directory to extract the package
    extract_dir = os.path.splitext(os.path.splitext(package)[0])[0]  # Remove both .tar and .gz

    # Create extraction directory if it doesn't exist
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)

    # Extract the package
    try:
        with tarfile.open(package, "r:gz") as tar:
            tar.extractall(path=extract_dir)
            print(f"=> Package {package} extracted to {extract_dir}.")  # Inform the user
            logging.info(f"Package {package} extracted to {extract_dir}.")
    except Exception as e:
        logging.error(f"Error while extracting {package}: {e}")
        print(f"Error while extracting {package}: {e}")

def install(packagefolder):
    # Check if XPKGMETA exists
    if os.path.isfile(f"{packagefolder}/XPKGMETA"):
        config.read(f'{packagefolder}/XPKGMETA')
        
        try:
            # Retrieve Useful data from the package
            print("=> Obtaining Data from the Package Metadata")
            name = config.get('XPKG', 'pkgname')
            maintainer = config.get('XPKG', 'maintainer')
            version = config.get('XPKG', 'version')
            binaryloc = config.get('XPKG', 'binaryloc')
            extrafiles = config.get('XPKG', 'extra')
            
            print(f"=> Installing {name} (Version: {version})")  # Inform the user
            shutil.move(binaryloc, f"{xpkgdir}/software")
            shutil.move(extrafiles, f"{xpkgdir}/extra")
            
            # Add package to registry
            with open(f"{xpkgdir}/pkglist.db", "a") as file:
                file.write(f'{name}-{version}\n')
            
            # Clean up the package folder
            shutil.rmtree(packagefolder)
            print(f"=> {name} installed successfully!")  # Inform the user
            logging.info(f"Installed package {name}, version {version}.")
        
        except configparser.NoSectionError as e:
            logging.error(f"Metadata Error: {e}")
            print(f"Metadata Error: {e}")
        except KeyError as e:
            logging.error(f"Metadata Error: Missing {e} field in XPKGMETA")
            print(f"Metadata Error: Missing {e} field in XPKGMETA")
    else:
        logging.error("Package Error: no XPKGMETA file found")
        print("Package Error: no XPKGMETA file found")

def lock():
    with open(f"{xpkgdir}/db.lck", 'w') as lock:
        lock.write('XPKG IS LOCKED')
    logging.info("Locked the XPKG database.")

def ulock():
    if os.path.isfile(f"{xpkgdir}/db.lck"):
        os.remove(f"{xpkgdir}/db.lck")
        logging.info("Unlocked the XPKG database.")

def chklock():
    if os.path.isfile(f"{xpkgdir}/db.lck"):
        logging.warning("XPKG is currently locked.")
        print("=> XPKG is in use")
        print(f"=> If you think this is an error, please remove {xpkgdir}/db.lck")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: xpkg <install|local> <package>")
        logging.error("Not enough arguments provided. Expected action and package.")
        sys.exit(1)
    action = sys.argv[1]
    package = sys.argv[2]

    if os_type == "win32":
        formal = "Windows"
    elif os_type == "macos":
        formal = "macOS"
    elif os_type == "linux":
        formal = "GNU/Linux"

    if action == "-v":
        print("xPKG - Cross platform Package Manager")
        print(f"xPKG Version 0.3")
        print(f"Running on {formal}")
        return

    chklock()

    if action == "install":
        logging.info(f"Attempting to install package: {package}")
        print("Network Install not yet available")
    elif action == "local":
        logging.info(f"Installing package from local file: {package}")
        lock()
        uncompress(package)
        install(f'{package}.xpkg')
        ulock()
    else:
        logging.error("Unknown action specified.")
        print("Package Error: no XPKGMETA file found")

if __name__ == "__main__":
    main()
