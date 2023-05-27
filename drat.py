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
    5. TODO: clear content of directories listed in the folders template
    6. TODO: copy content of directories list in the folders template
    7. TODO: delete appdata directories listed in the appdata template
    8. TODO: copy appdata directories listed in the appdata template
    9. TODO: load the registry with default values for the apps, and copy AppData config files
    z. log what was done
'''

# https://pypi.org/project/Send2Trash/, https://www.geeksforgeeks.org/how-to-delete-files-in-python-using-send2trash-module/
# https://pyinstaller.org/en/stable/operating-mode.html#bundling-to-one-file
# https://medium.com/swlh/easy-steps-to-create-an-executable-in-python-using-pyinstaller-cc48393bcc64
# 

"""
to new folder structure (within c:\FSC\)
drat
    userid
        folders
            folders (to check)
                files and folders to copy into the user folder
        configs
            .reg files to apply with reg 
        appdata
            app folders to delete from user's appdata and copy in place
"""

import platform
import os
import sys
import getopt
import time

from DiskItem import DiskItem
from DiskIO import DiskIO

class Drat:
    debug = False
    verbose = True # -v on the command line to override
    reset_configs = False # -c on the command line to override

    source_base = 'C:\\FSC\\drat\\'
    target_base_dir = 'C:\\Users\\'
    appdata_target_add = 'AppData\\Roaming\\'
    folders_src_dir = "folders\\"
    appdata_src_dir = "appdata\\"
    configs_src_dir = "configs\\"

    def __init__(self, argv):
        self.process_command_args(argv)

        # 0. show some system information
        user = os.getlogin() # get the current username
        print(f'This is computer "{platform.node()}" running {platform.system()} {platform.release()} for user "{user}"\n')

        # 1. verify that there is a template for this user
        template_dir = os.path.join(self.source_base, user)
        if(os.path.exists(template_dir) == False):
            print(f'A template does not exist for the "{user}" user. Aborting...')
        else:
            # template exists, let's see what's in it

            # standard folders?
            folder_pattern_dir = os.path.join(template_dir, self.folders_src_dir)
            if(os.path.exists(folder_pattern_dir)):
                if(self.verbose): print('The template has a pattern for standard folders')
                folder_target_dir = os.path.join(self.target_base_dir, user)
                self.process_folder_pattern(folder_pattern_dir, folder_target_dir)
            
            # appdata folders?
            appdata_pattern_dir = os.path.join(template_dir, self.appdata_src_dir)
            if(os.path.exists(appdata_pattern_dir)):
                if(self.verbose): print('The template has a pattern for appdata folders')
                appdata_target_dir = os.path.join(self.target_base_dir, user, self.appdata_target_add)
                self.process_folder_pattern(appdata_pattern_dir, appdata_target_dir)
            
            # registry file?
            config_pattern_dir = os.path.join(template_dir, self.configs_src_dir)
            if(os.path.exists(config_pattern_dir)):
                if(self.verbose): print('The template has a config folder for registry files')
                self.process_reg_files(config_pattern_dir)
            
            # done, reminders to the operator:
            print(  '\nREMEMBER TO EMPTY THE RECYCLE BIN!\n'
            'NOTE: click on the desktop and press F5 if folders are not showing as expected')

        return
    
    # ---
    # 
    def process_folder_pattern(self, template_dir, target_folders_base):
        print(f'ok, use {template_dir} to fix {target_folders_base}')
        diskio = DiskIO(self.verbose)
        # get a list of the pattern directory items (first-level only)
        source_folders = diskio.scanDir(template_dir, 'd')
        # for each directory in the pattern, clear everything the matching user directory
        for folder in source_folders:
            target_folder = os.path.join(target_folders_base, folder.filename)
            # the AppData folder should NEVER occur at this level, but could be accidentally placed here,
            #  so avoid catastrophic user error by ignoring it
            if folder.filename.lower() == 'appdata':
                print(f'\n>>> ERROR: AppData is in the wrong place: {folder.path}\n')
            else:
                # a: delete ...
                if self.verbose: print(f'- moving *everything* in {target_folder} to the Recycle Bin')
                diskio.clear_dir(target_folder) # first delete the existing entries in the directory
                time.sleep(1) # these sleeps are to see if the screen icons will auto-update i
                                # (currently they disappear and don't re-appear until reboot or F5 on the screen)
                if self.verbose: print(f'- copy everything from {folder.path} to {target_folder}')
                diskio.copy_dir(folder.path, target_folder) # then copy the correct set of files to the target directory
                time.sleep(1) # these sleeps seem to help; not sure why
        print()


    # ---
    #
    def process_reg_files(self, config_dir):
        print(f'ok, gonna apply .reg files from {config_dir}')
        print()
    
    # ---
    # process the command line and set control variables as needed
    def process_command_args(self, argv):
        if self.debug: print('Number of arguments:', len(argv), 'arguments.')
        if self.debug: print('Argument List:', str(argv))
        opts, args = getopt.getopt(argv,"hv",[])
        for opt, arg in opts:
            if opt == '-h':
                print ('drat.py [-v]')
                sys.exit()
            elif opt == "-v":
                print('Setting Verbose mode')
                self.verbose = True
            elif opt == "-c":
                print('Resetting configuration files')
                self.reset_configs = True
        if self.debug: print(f'verbosity: {self.verbose}')
        return

if __name__ == '__main__':
    # go do the work
    drat = Drat(sys.argv[1:])

    # give them a chance to empty the recycle bin

    input(  'Press ENTER when done . . . . . ')
