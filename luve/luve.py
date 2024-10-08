import os
import subprocess
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LUVE:
    @staticmethod
    def run_command(command, check=True):
        """Runs a command in the subprocess and handles output and errors."""
        try:
            logging.info(f"Running command: {' '.join(command)}")
            subprocess.run(command, check=check)
        except subprocess.CalledProcessError as e:
            logging.error(f"Command '{' '.join(command)}' failed with return code {e.returncode}")
            logging.error(f"Output: {e.output}")
            raise  # Re-raise exception for further handling if necessary

    @staticmethod
    def mount(mountpoint, image):
        """Mounts an image to a specified mountpoint."""
        LUVE.run_command(['mount', image, mountpoint])

    @staticmethod
    def umount(mountpoint):
        """Unmounts a specified mountpoint."""
        LUVE.run_command(['umount', '-l', mountpoint])

    @staticmethod
    def imagebuilder(image, size, name):
        """Creates a disk image of specified size and formats it as ext4."""
        try:
            logging.info(f"Creating a {size}MB image at {image} with name '{name}'")
            LUVE.run_command(['dd', 'if=/dev/zero', f'of={image}', 'bs=1M', f'count={size}'])
            LUVE.run_command(['mkfs.ext4', image])
            logging.info(f"Successfully created and formatted {image} as ext4 with {size}MB")
        except Exception as e:
            logging.error(f"Error during image creation: {e}")

    @staticmethod
    def installsystem(image, mountpoint, distribution):
        """Installs a Linux distribution in the mounted image."""
        try:
            LUVE.mount(mountpoint, image)
            if distribution == "debian":
                LUVE.run_command(['debootstrap', 'bookworm', mountpoint])
                logging.info(f"Installed Debian Bookworm on {mountpoint}")
            elif distribution == "arch":
                LUVE.run_command(['pacstrap', '-K', mountpoint])
                logging.info(f"Installed Arch on {mountpoint}")
            else:
                logging.error("Invalid distribution specified; must be 'arch' or 'debian'")
        except Exception as e:
            logging.error(f"Error during system installation: {e}")

    @staticmethod
    def chrootsys(mountpoint, command="/bin/bash"):
        """Enters a chroot environment at the specified mountpoint."""
        try:
            logging.info(f"Entering chroot environment at {mountpoint} with command: {command}")
            LUVE.run_command(['chroot', mountpoint, command])
        except Exception as e:
            logging.error(f"Error entering chroot environment: {e}")

def main():
    logging.info("LUVE is not designed to be executed as a standalone application.")
    logging.info("Please use a LUVE Frontend, like vL.")

if __name__ == "__main__":
    main()
