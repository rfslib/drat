'''
file: drat.py
author: rfslib
purpose: reset equipment computer desktops in the RFSL

    0. verify that this is running as the patron account
    1. show some system information
    2. delete all files (including shortcuts) on the patron desktop (except the desktop.ini)
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

user = os.getlogin()
target_user = 'rfsl' # 'Patron'
target_dir = f'C:/Users/{user}/Desktop/'
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

def main():
    # 0. verify that this is running as the patron account
    if user.lower() != target_user.lower():
        print('This is for the Patron accout only')
        exit()

    # 1. show some system information
    print(f'This is "{platform.node()}" running {platform.system()} {platform.release()} for {os.getlogin()}')

    # gather the template directory items
    full_source_dir = os.path.abspath(source_dir)
    expected_items = scanDir(full_source_dir)

    # gather the current desktop (directory) items
    desktop_items = scanDir(target_dir)

    # 2. delete all files (including shortcuts) on the patron desktop (except the desktop.ini)
    # 2a. delete all folders not matching ones in the template
    print('Cleaning up the desktop')
    for fn in desktop_items:
        target = desktop_items[fn].path
        if fn == 'desktop.ini':
            pass
        elif desktop_items[fn].type == 'f':
            print(f'  {fn} - file to be deleted')
            os.chmod(target, stat.S_IWRITE) # remove read-only
            os.remove(target)
        elif desktop_items[fn].type == 'd':
            os.system(f'attrib -h "{target}"') # unhide just in case
            if fn not in expected_items:
                print(f'  {fn} - folder to be deleted')
                os.chmod(target, stat.S_IWRITE) # remove read-only
                shutil.rmtree(target)
        else:
            print(f'  {fn} ok')

    # 3. copy the correct set of files to the patron desktop
    print('Restoring the desktop')
    for fn in expected_items:
        target = os.path.join(target_dir, fn)
        if expected_items[fn].type == 'f':
            print(f'  {fn} - file to be copied')
            shutil.copy(expected_items[fn].path, target)
            os.chmod(target, stat.S_IREAD) # set read-only
        elif expected_items[fn].type == 'd':
            if fn not in desktop_items:
                print(f'  {fn} - folder to be copied')
                shutil.copytree(expected_items[fn].path, target)
                os.chmod(target, stat.S_IREAD) # set read-only


    # reset registry stuff


if __name__ == '__main__':
    main()