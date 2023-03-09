'''
file: drat.py
author: rfslib
purpose: reset equipment computer desktops in the RFSL

    0. show some system information
    1. verify that this is running as the patron account
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
from send2trash import send2trash

debug = True

target_base = 'C:\\Users\\'
source_dir = 'C:\\FSC\\drat\\template\\'
#source_dir = 'C:\\Users\\rfsl\\rfslib\\drat\\template\\'

def scanDir(dir, type=''):
    items = []
    for i in os.scandir(dir):
        if (i.is_file() or i.is_symlink()) and (type=='' or type=='f'):
            item = DeskItem(i.name, i.path, "f")
            items.append(item)
        elif i.is_dir() and (type == '' or type == 'd'):
            item = DeskItem(i.name, i.path, "d")
            items.append(item)
    return(items)

def main():

    user = os.getlogin() # get the current username

    # 0. show some system information
    print(f'This is computer "{platform.node()}" running {platform.system()} {platform.release()} for user "{user}"')

    # 1. verify that this is running as a configured account
    template_dirs = scanDir(source_dir, 'd') # get a list of the user templates
    target_foo = ''
    for item in template_dirs:
        if item.filename == user:
            target_foo = os.path.join(target_base, user)
            source_foo = os.path.join(source_dir, user)
            break
    if target_foo == '':
        print(f'A template does not exist for the "{user}" user. Aborting...')
        return()
    else:
        if debug: print(f'Ok, processing stuff in {target_foo}')
        if debug: print(f'    getting stuff from {source_foo}')


    # gather the template directory items (directories to be cleaned up, usually Desktop)
    dirs_to_clean = scanDir(source_foo, 'd')

    for item in dirs_to_clean:
        target_dir = os.path.join(target_foo, item.filename)
        clean_dir(item.path, target_dir)

    print('\nREMEMBER TO EMPTY THE RECYCLE BIN!')

    # TODO: registry

    return

def clean_dir(source_dir, target_dir):
    if debug: print(f'Cleaning {target_dir} from {source_dir}')

    # gather the current target directory items
    target_items = scanDir(target_dir)
    target_filenames = []
    for item in target_items:
        target_filenames.append(item.filename)
    expected_items = scanDir(source_dir)
    expected_filenames = []
    for item in expected_items:
        expected_filenames.append(item.filename)

    # 2. delete all files (including shortcuts) in the current directory (except the desktop.ini)
    # 2a. delete all folders not matching ones in the template
    print(f'Clearing {target_dir}')
    for fn in target_items:
        #target = target_items[fn].path
        if fn.filename == 'desktop.ini':
            print(f'  {fn.filename} - skipped')
            pass
        elif fn.type == 'f':
            print(f'  {fn.filename} - file to be deleted')
            os.chmod(fn.path, stat.S_IWRITE) # remove read-only
            send2trash(fn.path) ##** os.remove(target)
        elif fn.type == 'd':
            os.system(f'attrib -h "{fn.path}"') # unhide just in case
            if fn.filename not in expected_filenames:
                print(f'  {fn.filename} - folder to be deleted')
                os.chmod(fn.path, stat.S_IWRITE) # remove read-only
                send2trash(fn.path) ##**shutil.rmtree(target)
        else:
            print(f'  {fn.filename} ok')

    # 3. copy the correct set of files to the patron desktop
    print(f'Restoring {target_dir}')
    for fn in expected_items:
        target = os.path.join(target_dir, fn.filename)
        if fn.type == 'f':
            print(f'  {fn.filename} - file to be copied')
            shutil.copy(fn.path, target)
            os.chmod(target, stat.S_IREAD) # set read-only
        elif fn.type == 'd':
            if fn.filename not in target_filenames:
                print(f'  {fn.filename} - folder to be copied')
                shutil.copytree(fn.path, target)
                os.chmod(target, stat.S_IREAD) # set read-only

    return()
    


if __name__ == '__main__':
    main()
    input('Press ENTER when done . . . . . ')
    print()