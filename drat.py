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
    5. TODO load the registry with default values for the apps, and copy AppData config files
    6. TODO recursively clear directories
    7. TODO recursively copy directories (already done?)
    z. log what was done
'''

# https://pypi.org/project/Send2Trash/, https://www.geeksforgeeks.org/how-to-delete-files-in-python-using-send2trash-module/
# https://pyinstaller.org/en/stable/operating-mode.html#bundling-to-one-file
# https://medium.com/swlh/easy-steps-to-create-an-executable-in-python-using-pyinstaller-cc48393bcc64
# 

TODO: FIX APPDATA COPY: DON'T COPY, but use a separate AppData directory parallel to the template directory
TODO: cuz the appdata logic should only delete the ones to be replaced
TODO: and the registry directory contains 0 or more .reg files to be applied
i.e.:
drat 
    templates 
        userid
            folders (to check)
                files and folders to copy into the user folder
    appdata 
        userid 
            app folders to delete from user's appdata and copy in place
    configs 
        userid 
            .reg files to apply with reg 

import platform
import os
import stat
import shutil
import sys
import getopt

from DeskItem import DeskItem
from send2trash import send2trash

debug = False
verbose = False # -v on the command line to override
reset_configs = False # -c on the command line to override

target_base = 'C:\\Users\\'
source_dir = 'C:\\FSC\\drat\\template\\'
#source_dir = 'C:\\Users\\rfsl\\rfslib\\drat\\template\\'

#---
# main starts here
def main(argv):
    global verbose, debug, reset_configs

    process_command_line(argv) # set program control args from the command line

    # 0. show some system information
    user = os.getlogin() # get the current username
    print(f'This is computer "{platform.node()}" running {platform.system()} {platform.release()} for user "{user}"\n')

    # 1. verify that there is a template for this user
    source_foo = os.path.join(source_dir, user)
    target_foo = get_template_dir(user)
    if target_foo == '':
        print(f'A template does not exist for the "{user}" user. Aborting...')
        return()
    if debug: print(f'Ok, processing stuff in {target_foo}')
    if debug: print(f'    getting stuff from {source_foo}')
    
    # gather the template directory items (directories to be cleaned up)
    template_dirs = scanDir(source_foo, 'd')

    # clean each directory in the template: delete everything in it and copy back from the template
    for item in template_dirs:
        target_dir = os.path.join(target_foo, item.filename)
        if item.filename.lower() == 'appdata':
            copy_dir(item.path, target_dir)
        else:
            clear_dir(target_dir)
            copy_dir(item.path, target_dir)
            ##** reset_dir(item.path, target_dir)

    # TODO: registry and AppData files

    print('\nREMEMBER TO EMPTY THE RECYCLE BIN!\n'
            'NOTE: click on the desktop and press F5 if folders are not showing as expected')


    return

#---
# scan a directory and return a list of items in it (f=file or shortcut, d=directory)
def scanDir(dir, type=''):
    global verbose, debug
    items = []
    for i in os.scandir(dir):
        if (i.is_file() or i.is_symlink()) and (type=='' or type=='f'):
            item = DeskItem(i.name, i.path, "f")
            items.append(item)
        elif i.is_dir() and (type == '' or type == 'd'):
            item = DeskItem(i.name, i.path, "d")
            items.append(item)
    return(items)

# ---
# get the template directory for the current user
def get_template_dir(user):
    template_dirs = scanDir(source_dir, 'd') # get a list of the user templates
    for item in template_dirs:
        if item.filename.lower() == user.lower():
            return(os.path.join(target_base, user))
            break


# ---
# process the command line and set control variables as needed
def process_command_line(argv):
    global verbose, debug, reset_configs

    # process command-line arguments
    if debug: print('Number of arguments:', len(argv), 'arguments.')
    if debug: print('Argument List:', str(argv))
    opts, args = getopt.getopt(argv,"hv",[])
    for opt, arg in opts:
        if opt == '-h':
            print ('drat.py [-v]')
            sys.exit()
        elif opt == "-v":
            print('Setting Verbose mode')
            verbose = True
        elif opt == "-c":
            print('Resetting configuration files')
            reset_configs = True
    if debug: print(f'verbosity: {verbose}')
    return()

# ---
# copy items from one directory to another
def copy_dir(source_dir, target_dir):

    print(f'Restoring {target_dir}')

    expected_items = scanDir(source_dir)
    expected_filenames = []
    for item in expected_items:
        expected_filenames.append(item.filename)

    for fn in expected_items:
        target = os.path.join(target_dir, fn.filename)
        if fn.filename == 'desktop.ini':
            if (verbose): print(f'  {fn.filename} - skipped')
            pass
        elif fn.type == 'f':
            if verbose: print(f'  {fn.filename} - file to be copied')
            shutil.copy(fn.path, target)
            os.chmod(target, stat.S_IREAD) # set read-only
        elif fn.type == 'd':
            if verbose: print(f'  {fn.filename} - folder to be copied')
            shutil.copytree(fn.path, target)
            os.chmod(target, stat.S_IREAD) # set read-only

# ---
# delete everythin in the target dir
def clear_dir(target_dir):
    # gather the current target directory items
    target_items = scanDir(target_dir)
    target_filenames = []
    for item in target_items:
        target_filenames.append(item.filename)

    # 2. delete all files (including shortcuts) in the current directory (except the desktop.ini)
    # 2a. delete all folders not matching ones in the template
    print(f'Clearing {target_dir}')
    for fn in target_items:
        #target = target_items[fn].path
        if fn.filename == 'desktop.ini':
            if verbose: print(f'  {fn.filename} - skipped')
            pass
        elif fn.type == 'f' or fn.type == 'd':
            if verbose: 
                if fn.type == 'f': print(f'  {fn.filename} - file to be deleted')
                elif fn.type == 'd': print(f'  {fn.filename} - folder to be deleted')
            os.system(f'attrib -h "{fn.path}"') # unhide just in case
            os.chmod(fn.path, stat.S_IWRITE) # remove read-only
            send2trash(fn.path) ##** os.remove(target)
        else:
            if verbose: print(f'  {fn.filename} ok')

# ---
# delete everything in the target dir, copy everything from the source dir to the target dir
def reset_dir(source_dir, target_dir):
    global verbose, debug
    if debug: print(f'Cleaning {target_dir} from {source_dir}')

    # 2. delete ...
    clear_dir(target_dir)

    # 3. copy the correct set of files to the patron desktop
    copy_dir(source_dir, target_dir)

    print()

    return()
    


if __name__ == '__main__':
    # go do the work
    main(sys.argv[1:])

    # give them the chance to empty the recycle bin
    input('Press ENTER when done . . . . . ')
    print()
