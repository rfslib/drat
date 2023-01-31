'''
file: drat.py
author: rfslib
purpose: reset equipment computer desktops in the RFSL

    1. get the name of the system to be reset
    2. delete all files (including shortcuts) on the patron desktop
    2a. delete all folders not matching ones in the template
    3. copy the correct set of files to the patron desktop
    4. if requested, delete all files in all folders on the desktop
    5. TODO load the registry with default values for the patron user
    6. log what was done
'''

import platform
import os
import shutil

from DeskItem import DeskItem

target_dir = r'C:\\Users\\rfsl\\Desktop'
source_dir = r'template\\'


def scanDir(dir):
    items = {}
    for i in os.scandir(dir):
        if i.is_file() or i.is_symlink():
            item = DeskItem(i.name, i.path, "f")
        elif i.is_dir():
            item = DeskItem(i.name, i.path, "d")
        items[i.name] = item 
    return(items)

# 1. get the name of the system to be reset
hostname = platform.node()
platform = print (platform.platform())
print(f'This machine is named {hostname}.')

# gather the template directory items
full_source_dir = os.path.abspath(source_dir)
expected_items = scanDir(full_source_dir)

# gather the current desktop (directory) items
desktop_items = scanDir(target_dir)

# 2. delete all files (including shortcuts) on the patron desktop
# 2a. delete all folders not matching ones in the template
#  except the desktop.ini

for fn in desktop_items:
    if fn == 'desktop.ini':
        pass
    elif desktop_items[fn].type == 'f':
        print(f'{fn} file to be deleted')
        os.unlink(desktop_items[fn].path)
    elif desktop_items[fn].type == 'd' and fn not in expected_items:
        print(f'{fn} dir to be deleted')
        shutil.rmtree(desktop_items[fn].path)
    else:
        print(f'{fn} ok')

# 3. copy the correct set of files to the patron desktop
for fn in expected_items:
    if expected_items[fn].type == 'f':
        shutil.copy(expected_items[fn].path, target_dir)
    elif expected_items[fn].type == 'd':
        if fn not in desktop_items:
            shutil.copy(expected_items[fn].path, target_dir)


# reset registry stuff