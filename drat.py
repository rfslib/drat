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
import stat
import shutil

from DeskItem import DeskItem

target_dir = r'C:/Users/rfsl/Desktop/'
source_dir = r'C:/Users/rfsl/rfslib/drat/template/'
#source_dir = r'C:/Program Files/fsc/drat/template/'


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
#hostname = platform.node()
#platform = print (platform.platform())
print(f'This is "{platform.node()}" running {platform.platform()}')

# gather the template directory items
full_source_dir = os.path.abspath(source_dir)
expected_items = scanDir(full_source_dir)

# gather the current desktop (directory) items
desktop_items = scanDir(target_dir)

# 2. delete all files (including shortcuts) on the patron desktop
# 2a. delete all folders not matching ones in the template
#  except the desktop.ini

print('Cleaning up the desktop')
for fn in desktop_items:
    if fn == 'desktop.ini':
        pass
    elif desktop_items[fn].type == 'f':
        print(f'  {fn} - file to be deleted')
        os.chmod(desktop_items[fn].path, stat.S_IWRITE) # remove read-only
        os.remove(desktop_items[fn].path)
    elif desktop_items[fn].type == 'd' and fn not in expected_items:
        print(f'  {fn} - folder to be deleted')
        os.chmod(desktop_items[fn].path, stat.S_IWRITE) # remove read-only
        shutil.rmtree(desktop_items[fn].path)
    else:
        print(f'  {fn} ok')

# 3. copy the correct set of files to the patron desktop
print('Restoring the desktop')
for fn in expected_items:
    target = os.path.join(target_dir, fn)
    if expected_items[fn].type == 'f':
        print(f'  {fn} - file to be copied')
        shutil.copy(expected_items[fn].path, target)
    elif expected_items[fn].type == 'd':
        os.system(f'attrib -h {target}')
        if fn not in desktop_items:
            print(f'  {fn} - folder to be copied')
            shutil.copytree(expected_items[fn].path, target)


# reset registry stuff