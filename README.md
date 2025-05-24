# bebushos
BebushOS Linux distro [Arch-based]

## Description
I made custom tool for installing Arch Linux. Tool is based on `archinstall` logic, with some preconfigured options.
This tools comes pre-installed in custom `Archiso` for BebushOS Linux distro.
> BebushOS ISO file is not ready yet (need some tweaks).

## How to use
1. Download the scripts via `wget https://github.com/qewaru/bebushos/releases/download/v0.1/bebushos-v0.1.zip`.
   > Note: Structure will be `/installer/<scripts_here>`
2. Unzip the archive via `unzip bebushos-v0.1.zip`
   > Note: Make sure that you have `unzip` installed
3. Move the archive output to /root directory via `mv installer /root/`
4. Set proper permissions via `chmod +x /root/installer/start_installer.sh`
5. Run the script via `/root/installer/start_installer.sh`

## How it works
`start_installer.sh` - prepares environment for Python script to execute:
  * Installs virtual environment
  * Prepares log file
  * Installs necessary libraries (rich, Babel, questionary)
`installer.py` - main script for installation configuration
  * Initializes JSON config for `archinstall`
  * Fetching necessary data via terminal commands (GPUs, disks, timezones, locales)
  * Lets user configure the system
  * Upon finishing configuration, script will tweak `archinstall`, so it will work in silent mode.

## Future plans
* Rewrite the code, so it will manually install the OS (without interaction with `archinstall`)
* Make systemd service, so script will be executed automatically
* Finish the Live ISO, so users will be able to check the BebushOS
* Add the DE for Live ISO
