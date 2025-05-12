import sys
import subprocess
import re
import json
import uuid
import os

from babel import Locale
from babel.core import UnknownLocaleError
from rich.console import Console
from rich.prompt import Prompt
from rich.markdown import Markdown
import questionary



console = Console()
name_locale = {} # Contains both - locale display name & system name
user_gpu = ""
running = True

choices = ['Language', 'Timezone', 'User & Root', 'Bundles', 'Drivers', 'Install', 'Abort']

# Bundle options
# Can be adjusted for any needs
bundles = {
    "Pure": [],
    "Gaming": ['discord', 'fastfetch', 'spotify-launcher', 'steam', 'wine', 'nano', 'firefox', 'python'],
    "Office": ['nano', 'firefox', 'spotify-launcher'],
}

# Driver options
# Made as in archinstall
drivers = {
    "Generic drivers (Mesa)": ['mesa', 'mesa-utils', 'vulkan-icd-loader'],
    "NVIDIA (Properitary)": ['nvidia', 'nvidia-settings', 'nvidia-utils', 'lib32-nvidia-utils'],
    "NVIDIA (Open Source) [Recommended for NVIDIA]": ['xf86-video-nouveau', 'vulkan-nouveau', 'mesa-utils'],
    "AMD (Open Source)": ['xf86-video-amdgpu', 'xf86-video-ati', 'mesa-utils', 'vulkan-radeon', 'vulkan-icd-loader'],
    "Intel (Open Source)": ['xf86-video-intel', 'mesa-utils', 'vulkan-intel', 'vulkan-icd-loader'],
}

# JSON config for archinstall `--config` flag
jconfig = {
    "archinstall-language": "English",
    "audio_config": {
      "audio": "pipewire"
    },
    "bootloader": "Grub", # or "Systemd-boot", depends on system
    "custom_commands": [],
    "debug": False,
    "disk_config": {
        "config_type": "default_layout",
        "device_modifications": [
            {
                "device": "", # set_diskpath()
                "partitions": [ # UPD HERE - adjust the size of the home partition
                    {
                        "btrfs": [],
                        "dev_path": None,
                        "flags": [
                            "boot"
                        ],
                        "fs_type": "fat32",
                        "mount_options": [],
                        "mountpoint": "/boot",
                        "obj_id": str(uuid.uuid4()), # [!]Creating unique ID for each partition
                        "size": {
                            "sector_size": {
                                "unit": "B",
                                "value": 512
                            },
                            "unit": "GiB",
                            "value": 1
                        },
                        "start": {
                            "sector_size": {
                                "unit": "B",
                                "value": 512
                            },
                            "unit": "MiB",
                            "value": 3
                        },
                        "status": "create",
                        "type": "primary"
                    },
                    {
                        "btrfs": [],
                        "dev_path": None,
                        "flags": [],
                        "fs_type": "ext4",
                        "mount_options": [],
                        "mountpoint": "/",
                        "obj_id": str(uuid.uuid4()),
                        "size": {
                            "sector_size": {
                                "unit": "B",
                                "value": 512
                            },
                            "unit": "GiB",
                            "value": 32
                        },                        
                        "start": {
                            "sector_size": {
                                "unit": "B",
                                "value": 512
                            },
                            "unit": "B",
                            "value": 1076887552
                        },
                        "status": "create",
                        "type": "primary"
                    },
                    {
                        "btrfs": [],
                        "dev_path": None,
                        "flags": [],
                        "fs_type": "ext4",
                        "mount_options": [],
                        "mountpoint": "/home",
                        "obj_id": str(uuid.uuid4()),
                        "size": {
                            "sector_size": {
                                "unit": "B",
                                "value": 512
                            },
                            "unit": "GiB",
                            "value": 30
                        },
                        "start": {
                            "sector_size": {
                                "unit": "B",
                                "value": 512
                            },
                            "unit": "B",
                            "value": 35436625920
                        },
                        "status": "create",
                        "type": "primary"
                    }
                ],
                "wipe": True
            }
        ],
    },
    "hostname": "bebushos", # UPD HERE - change hostname for yours
    "kernels": [
      "linux",
      "linux-lts"
    ],
    "locale_config": {
      "kb_layout": "us", # fetch_locales()
      "sys_enc": "UTF-8", # fetch_locales()
      "sys_lang": "en_US" # fetch_locales()
    },
    "mirror_config": {
      "custom_servers": [],
      "mirror_regions": { # UPD HERE - mirrors should be changed (check _ for more info about mirrors)
        "Sweden": [
            "https://mirror.braindrainlan.nu/archlinux/$repo/os/$arch",
            "http://ftp.myrveln.se/pub/linux/archlinux/$repo/os/$arch",
            "http://ftpmirror.infania.net/mirror/archlinux/$repo/os/$arch",
            "https://mirror.osbeck.com/archlinux/$repo/os/$arch",
            "http://ftp.lysator.liu.se/pub/archlinux/$repo/os/$arch",
            "https://mirror.accum.se/mirror/archlinux/$repo/os/$arch",
            "https://ftp.myrveln.se/pub/linux/archlinux/$repo/os/$arch",
            "http://mirror.bahnhof.net/pub/archlinux/$repo/os/$arch",
            "https://mirror.bahnhof.net/pub/archlinux/$repo/os/$arch",
            "http://mirror.accum.se/mirror/archlinux/$repo/os/$arch",
            "https://ftp.lysator.liu.se/pub/archlinux/$repo/os/$arch",
            "http://ftp.ludd.ltu.se/mirrors/archlinux/$repo/os/$arch",
            "https://ftp.ludd.ltu.se/mirrors/archlinux/$repo/os/$arch"
        ]
      },
      "optional_repositories": [],
      "custom_repositories": [
        "multilib" # Enabled in order to download additional packages (steam/discord/etc)
      ]
    },
    "network_config": {
      "type": "nm"
    },
    "no_pkg_lookups": False,
    "ntp": True,
    "offline": False,
    "packages": [
        # Lines 425 & 434
    ],
    "parallel downloads": 0,
    "profile_config": {
      "gfx_driver": "All open-source",
      "greeter": "sddm",
      "profile": {
        "custom_settings": {
            "KDE Plasma": {}
        },
        "details": [
          "KDE Plasma"
        ],
        "main": "Desktop"
      }
    },
    "swap": False, # UPD HERE - change if needed
    "timezone": "", # UPD HERE
    "version": None
}

# JSON config for archinstall `--creds` flag
uconfig = {
    "!root-password": "",
    "!users": [
        {
            "!password": "",
            "sudo": True,
            "username": ""
        }
    ]
}

# Fetching locales via bash command
def fetch_locales():
    global name_locale

    result = subprocess.run(
        ["ls", "/usr/share/i18n/locales"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    locales_raw = result.stdout.strip().split("\n")

    locales_clean = []
    for loc in locales_raw:
        # Dropping iso/non utf
        pattern = r"^[a-z]{1,3}_[A-Z]{1,3}$"

        match = re.match(pattern, loc)
        if not match:
            continue

        print(loc)
        try:
            l = Locale.parse(loc)
            display_name = l.get_display_name('en').capitalize()

            locales_clean.append((loc, display_name))

            name_locale[display_name.lower()] = loc

        except UnknownLocaleError:
            continue

    
    locales_clean.sort(key=lambda x: x[1])

    # UPD HERE - add most relevant locales
    locales_clean.remove(('en_US', "English (united states)"))
    locales_clean.insert(0, ('en_US', "English (united states)"))
    
    locales_clean.remove(("ru_RU", "Russian (russia)"))
    locales_clean.insert(1, ("ru_RU", "Russian (russia)"))

    return locales_clean


# Fetching timezones via bash command
def fetch_timezones():
    result = subprocess.run(
        ["timedatectl", "list-timezones"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    raw = result.stdout.strip().split("\n")

    i=0
    for tz in raw:
        # Placing ETC/GMT timezones on top
        if "Etc/GMT" in tz:
            raw.remove(tz)
            raw.insert(i, tz)

    return raw

# Fetching GPU(s) via bash command 
def fetch_gpu():
    try:
        result = subprocess.run(
            ["lspci"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # UNCOMMENT VGA_LIST FOR MULTI-GPU
        # vga_list = []
        for line in result.stdout.splitlines():
            if "VGA compatible controller" in line or "3D controller" in line:
                # vga_list.append(line)
                return line
    except Exception as e:
        return None


# Checking for most relevant drivers based on fetched GPU 
def fetch_drivers():
    global user_gpu
    gpu = fetch_gpu()

    if not gpu:
        return "Unknown"

    user_gpu = make_gpu_name(gpu)

    if "NVIDIA" in gpu:
        return drivers["NVIDIA (Open Source) [Recommended for NVIDIA]"]
    elif "AMD" in gpu or "ATI" in gpu:
        return drivers["AMD (Open Source)"]
    elif "Intel" in gpu:
        return drivers["Intel (Open Source)"]
    else:
        return drivers["Generic drivers (Mesa)"]


# Creating display names for locale list
def make_locale_list():
    list = fetch_locales()
    names = [item[1] for item in list]
    return names

# Creating display names for timezone list
def make_tz_list():
    list = fetch_timezones()
    return list

# Creating display name(s) for GPU list
def make_gpu_name(list):
    nvidia_regex = r"NVIDIA.*\[(.*?)\]"
    amd_regex = r"AMD.*\[(.*?)\]"

    if "NVIDIA" in list:
        match = re.search(nvidia_regex, list)
        if match:
            return f"NVIDIA [{match.group(1)}]"
    elif "AMD" in list:
        match = re.search(amd_regex, list)
        if match:
            return f"AMD [{match.group(1)}]"

    # FOR MULTI-GPU COMMENT IF-ELSE ABOVE & UNCOMMENT BELOW    
    # results = []

    # for line in list:
    #     if "NVIDIA" in line:
    #         match = re.search(nvidia_regex, line)
    #         if match:
    #             results.append(f"NVIDIA [{match.group(1)}]")
    #     elif "AMD" in line:
    #         match = re.search(amd_regex, line)
    #         if match:
    #             results.append(f"AMD [{match.group(1)}]")
    
    # return results


# Creating relevant diskpath
def set_diskpath():
    result = subprocess.run(
        ['lsblk', '-J', '-o', 'NAME,TYPE'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    output = json.loads(result.stdout)

    disks = []
    possible = ['sda', 'vda', 'nvme0n1']
    for d in output["blockdevices"]:
        if d["type"] == 'disk' and d["name"] in possible:
            disks.append("/dev/" + d["name"])

    return disks[0]

# Swtich function for user input
def switch(name): 
    if " +" in name:
        name = name.replace(" +", "").strip()

    if name == 'Language':
        choice = questionary.select(
            "Language: ",
            choices=make_locale_list()
        ).ask()

        if choice:
            jconfig["locale_config"]["sys_lang"] = name_locale.get(choice.lower())

    elif name == 'Timezone':
        choice = questionary.select(
            "Timezone: ",
            choices=make_tz_list()
        ).ask()

        if choice:
            jconfig["timezone"] = choice
        
    elif name == 'User & Root':
        username = questionary.text("Enter username: ").ask()
        password = questionary.password("Enter password: ").ask()
        confirm = questionary.password("Confirm password: ").ask()

        while password != confirm:
            confirm = questionary.password("""Passwords are not matching. 
            Confirm password: """).ask()

            if confirm is None:
                exit()

        uconfig["!users"][0]["username"] = username
        uconfig["!users"][0]["!password"] = password

        root = questionary.confirm("Set user password as a root password? [Recommended]").ask()
        if root == False:
            root_password = questionary.password("Root password: ").ask()
            uconfig["!root-password"] = root_password
        else:
            uconfig["!root-password"] = password

    elif name == 'Bundles':
        choice = questionary.select(
            "Bundles: ",
            choices=bundles
        ).ask()

        if choice:
            jconfig["packages"].extend(bundles[choice])

    elif name == 'Drivers':
        global drivers
        user_drivers = fetch_drivers()
        drivers = { f"Detected GPU: {user_gpu}": user_drivers, **drivers}
        choice = questionary.select(
            "GPU Drivers: ",
            choices=drivers
        ).ask()

        if choice:
            jconfig["packages"].extend(drivers[choice])

    elif name == "Install":
        install()

    if name in choices:
        index = choices.index(name)
        if not choices[index].endswith(" +"):
            choices[index] = choices[index] + " +"


#############################################################################################################
#                                              Patching archinstall                                         #
#############################################################################################################
#   In order to this script to work we need to tweak 2 files - disk_conf and profiles_handler.              #
#   This can be achieved by moving/inserting lines.                                                         #
#       1. Circular import error fix:                                                                       #
#           Without tweak archinstall will crash with error about `circular import` in "disk_conf" script.  #
#           In order to fix that, script will remove import of `arch_config_handler`, and move it to the    #
#           function that is using it.                                                                      #
#       2. Error `name '_' is undefined` fix:                                                               #
#          Due to specifics of the archinstall code it will load profiles only with TUI, which means that   #
#          even with config archinstall script will fail to use DE profile. It could be fixed with adding   #
#          2 lines that are importing `builtins` and setting a "fake" a translation function, so profile    #
#          will be loaded correctly.                                                                        #
#############################################################################################################

# Archinstall uses different indentation, so this function will find and use it
def detect_indentation(lines):
    for line in lines:
        stripped = line.lstrip()
        if stripped and line != stripped:
            indent = line[:len(line) - len(stripped)]
            return indent
    return '    '  # fallback: 4 spaces

def patch_archinstall():
    global console

    target_file1 = "/usr/lib/python3.13/site-packages/archinstall/lib/interactions/disk_conf.py"
    target_line1 = "from archinstall.lib.args import arch_config_handler"
    target_func = "def select_main_filesystem_format()"

    target_file2 = "/usr/lib/python3.13/site-packages/archinstall/lib/profile/profiles_handler.py"
    target_lines = ['import builtins', 'builtins._ = lambda x: x']

    # Patch circular import in disk config
    if not os.path.exists(target_file1) and not os.path.exists(target_file2):
        console.print("Target file for patching not found!")
        return

    with open(target_file1, 'r') as f:
        lines = f.readlines()

    indentation =  detect_indentation(lines)
    new_lines = []
    for line in lines:
        if target_line1 in line:
            continue

        new_lines.append(line)

    if indentation is None:
        print("Could not detect indentation style.")
        return

    for idx, line in enumerate(new_lines):
        if target_func in line:
            new_lines.insert(idx + 1, f"{indentation}{target_line1}\n")
            break

    with open(target_file1, 'w') as file:
        file.writelines(new_lines)


    # Patch `name '_' is undefined` error in profiles handler
    with open(target_file2, 'r') as file:
        lines = file.readlines()
    
    if len(lines) < 1:
        lines.extend([''] * (1 - len(lines)))

    for i, word in enumerate(target_lines):
        lines.insert(1 + i, word + '\n')

    with open(target_file2, 'w') as file:
        file.writelines(lines)


def install():
    global running, console

    jconfig["disk_config"]["device_modifications"][0]["device"] = set_diskpath()
    running = False

    # Uncomment for debug
    # console.print(jconfig)

    patch_archinstall()
    console.print("Pathcing done!")
    
    # with open('/tmp/user_configuration.json', 'w') as f:
    #     json.dump(jconfig, f, indent=2)

    # with open('/tmp/user_credentials.json', 'w') as f:
    #     json.dump(uconfig, f, indent=2)

    # subprocess.Popen(['/bin/bash', '-l', '-c', 'archinstall --config /tmp/config.json --creds /tmp/creds.json --silent'])

def main():
    global console, running

    while running:
        console.clear()
        console.print(r"""
         ____            __                       __      _____   ____       
        /\  _`\         /\ \                     /\ \    /\  __`\/\  _`\     
        \ \ \L\ \     __\ \ \____  __  __    ____\ \ \___\ \ \/\ \ \,\L\_\   
         \ \  _ <'  /'__`\ \ '__`\/\ \/\ \  /',__\\ \  _ `\ \ \ \ \/_\__ \   
          \ \ \L\ \/\  __/\ \ \L\ \ \ \_\ \/\__, `\\ \ \ \ \ \ \_\ \/\ \L\ \ 
           \ \____/\ \____\\ \_,__/\ \____/\/\____/ \ \_\ \_\ \_____\ `\____\
            \/___/  \/____/ \/___/  \/___/  \/___/   \/_/\/_/\/_____/\/_____/
        """)

        md = Markdown("# Use arrows [↑ or ↓] to navigate, Enter [↵] to select")
        console.print(md)

        choice = questionary.select(
            "Choose what to configure: ",
            choices=choices
        ).ask()

        if choice in ('Abort', None):
            console.print("[bold red]Aborting installation...[bold red]")
            break

        switch(choice)

if __name__ == "__main__":
    main()