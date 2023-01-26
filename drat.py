'''
file: drat.py
author: rfslib
purpose: reset equipment computer desktops in the RFSL
'''

# get the name of the system to be reset

# delete all files (including shortcuts) on the patron desktop

# copy the correct set of files to the patron desktop

import platform
import os
import shutil

# boo

source_dir = r'S:\\' # source for icons and folders
source_dir = r'C:\Users\\rfsl\\rfslib\\drat\\source\\'
base_dir = r'C:\\Users\\Patron\\' # user directory
base_dir = r'C:\\Users\\rfsl\\'
# specified as k_dir instead: work_dir = r'Desktop' # usual location of icons and folders
k_icons = 'icons'
k_folders = 'folders'
k_dir = 'dir'

machines = {
    'serve': {
        k_icons: 'serveicons',
        k_folders: 'servefolders',
        k_dir: 'Desktop'
    },
    'FS-50P7DS2s': {
        k_icons: 'testicons1',
        k_folders: 'testfolders1',
        k_dir: 'Desktop'
    },
    'ROB-STAFF-04': {
        k_icons: 'testicons2',
        k_folders: 'testfolders2',
        k_dir: 'Desktop'
    },
    'unknown': {
        k_icons: '',
        k_folders: '',
        k_dir: ''
    }
}


# get this machine's information
hostname = platform.node()
platform = print (platform.platform())
hostinfo = machines['unknown']
if hostname in machines:
    hostinfo = machines[hostname]

print(f'This machine is named {hostname}.\n Icons come from {hostinfo[k_icons]}.\n Folders to create are in {hostinfo[k_folders]}')

# delete everything in the target directory except the recycle bin
target_dir = os.path.join(base_dir, hostinfo[k_dir])
print(f'Target dir: {target_dir}')
for i in os.scandir(target_dir):
    if i.is_file() or i.is_symlink():
        if i.name == 'desktop.ini':
            print('skipping desktop.ini')
        else:
            print(f'File: {i.name}')
    elif i.is_dir():
        print(f'Dir: {i.name}')
    else:
        print(f'huh? {i.name}')



# copy from the template directory to the target directory

# reset registry stuff