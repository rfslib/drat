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
    5. clear content of directories listed in the folders template
    6. copy content of directories list in the folders template
    7. delete appdata directories listed in the appdata template
    8. copy appdata directories listed in the appdata template
    9. load the registry with default values for the apps, and copy AppData config files
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
import subprocess
import psutil

from diskItem import DiskItem
from diskio import DiskIO

class Drat:
    version = '20240626'
    debug = False # -d on the command line to set True
    verbose = False # -v on the command line to override
    reset_configs = True # -c on the command line to override
    clear_user_data = True # -u on the command line to override

    source_base = 'C:\\FSC\\drat\\' # where the template files are kept

    target_base_dir = 'C:\\Users\\' # add username to get the target base
    folders_src_dir = 'folders\\'
    appdata_src_dir = 'appdata\\'
    configs_src_dir = 'configs\\'
    appdata_target_add = 'AppData\\Roaming\\'

    program_list = {'fastfoto.exe':     'FastFoto', 
                    'scansmart.exe':    'ScanSmart', 
                    'escndv.exe':       'Epson Scan', 
                    'es2launcher.exe':  'Epson Scan 2',
                    'audacity.exe':     'Audacity',
                    'czur aura.exe':    'CZUR',
                    'handbrake.exe':    'HandBrake',
                    'paintstudio.view.exe': 'Paint 3D',
                    #'explorer.exe':     'File Explorer', # 20240526: cuz it may be blocking file/dir removal
                    #  ah, but explorer.exe continues to run even after all windows are closed :P
                    }

    def __init__(self, argv):
        self.process_command_args(argv)

        self.fatal_error = False

        # 0. show some system information
        user = os.getlogin() # get the current username
        print(f'\n'
              f'oh drat!            version {self.version}\n'
              f'     computer name: {platform.node()}\n'
              f'  operating system: {platform.system()} {platform.release()}\n'
              f'        login name: {user}\n'
              f'           verbose: {self.verbose}\n'
              f'  delete user data: {self.clear_user_data}\n'
              f'     reset configs: {self.reset_configs}\n'
            )

        # 1. verify that there is a template for this user, and process it if so
        template_dir = os.path.join(self.source_base, user)
        if(os.path.exists(template_dir) == False):
            print(f'ERROR: A template does not exist for the "{user}" ({template_dir}) user. Aborting...')
            self.fatal_error = True
        else:
            # template exists
            # get all apps cleared
            self.check_running_apps()
            # standard folders?
            if self.clear_user_data:
                folder_pattern_dir = os.path.join(template_dir, self.folders_src_dir)
                if(os.path.exists(folder_pattern_dir)):
                    if self.verbose: print('- The template has a pattern for standard folders')
                    print('- moving user data to the Recycle Bin')
                    folder_target_dir = os.path.join(self.target_base_dir, user)
                    self.process_folder_pattern(folder_pattern_dir, folder_target_dir)
                else:
                    print('No user template directory provided')
            
            # reset configuration?
            
            if self.reset_configs:
                appdata_pattern_dir = os.path.join(template_dir, self.appdata_src_dir)
                # appdata folders?
                if os.path.exists(appdata_pattern_dir):
                    if self.verbose: print('- The template has a pattern for appdata folders')
                    print('- resetting program configurations stage 1')
                    appdata_target_dir = os.path.join(self.target_base_dir, user, self.appdata_target_add)
                    self.process_appdata_pattern(appdata_pattern_dir, appdata_target_dir)
                else:
                    print('No appdata template directory provided')
                # registry files?
                config_pattern_dir = os.path.join(template_dir, self.configs_src_dir)
                if os.path.exists(config_pattern_dir):
                    if self.verbose: print('- The template has a config folder for registry files')
                    print('- resetting program configurations stage 2')
                    self.process_reg_files(config_pattern_dir)
                else:
                        print('No registry template directory provided')
            
            # done, reminders to the operator:
            print()
            if self.clear_user_data: 
                print('REMEMBER TO EMPTY THE RECYCLE BIN (unless a patron needs to copy data)!\n'
                      '(Right-click on the Recycle Bin icon and choose "Empty Recycle Bin")\n'
                      '')
            if self.verbose: print('NOTE: click on the desktop and press F5 if folders are not showing as expected')

        return
    
    # ---
    # 
    def process_appdata_pattern(self, template_dir, target_folders_base):
        if self.verbose: print(f'ok, use {template_dir} to fix {target_folders_base}')
        diskio = DiskIO(self.verbose)
        # get a list of the pattern directory items (first-level only)
        source_folders = diskio.scanDir(template_dir, 'd')
        # for each directory in the pattern, clear everything the matching user directory
        for folder in source_folders:
            target_folder = os.path.join(target_folders_base, folder.filename)
            if self.verbose: print(f'- moving *everything* in {target_folder} to the Recycle Bin')
            diskio.delete_dir_content(target_folder) # first delete the existing entries in the directory
            if self.verbose: print(f'- copy everything from {folder.path} to {target_folder}')
            diskio.copy_dir(folder.path, target_folder, False) # then copy the correct set of files to the target directory
    
    # ---
    # 
    def process_folder_pattern(self, template_dir, target_folders_base):
        if self.verbose: print(f'ok, use {template_dir} to fix {target_folders_base}')
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
                if folder.filename.lower() == 'desktop': 
                    time.sleep(1) # these sleeps are to see if the screen icons will auto-update i
                                # (currently they disappear and don't re-appear until reboot or F5 on the screen)
                if self.verbose: print(f'- copy everything from {folder.path} to {target_folder}')
                diskio.copy_dir(folder.path, target_folder, True) # then copy the correct set of files to the target directory
                if folder.filename.lower() == 'desktop': 
                    time.sleep(1) # these sleeps seem to help; not sure why

    # ---
    # check if an app is running
    # check the entire list of apps that are used, since 
    #   if something is running in the wrong machine that should be noticed as well
    def check_running_apps(self):
        all_clear = False
        while not all_clear:
            all_clear = True
            for proc in psutil.process_iter():
                #print(f'{proc.name()} is {proc.status()}') #, proc.pid)
                proc_name = proc.name().lower()
                proc_status = proc.status().lower()
                try:
                    if proc_name in self.program_list and proc_status == 'running':
                        print(f'>> the {self.program_list[proc_name]} program is running')
                        all_clear = False
                except: # Exception as err:
                    pass # print(err)
            if not all_clear:
                print(f'>> All Windows of the above program(s) must be closed so configurations can be reset!')
                print(f'>> Close all other applications as well to expedite the reset process.')
                input('>> Press ENTER when they are closed . . . ')
                print()
        return

    # ---
    # apply registry config files to the active registry
    def process_reg_files(self, config_dir):
        if self.verbose: print(f'ok, gonna apply .reg files from {config_dir}')
        diskio = DiskIO(self.verbose)
        # get a list of the pattern directory items (first-level only)
        reg_files = diskio.scanDir(config_dir, 'f')
        for reg_file in reg_files:
            if self.debug: print(f'process_reg_files: {reg_file}')
            try:
                subprocess.run(["reg", "import", reg_file.path], check=True)
            except Exception as err:
                print(f'registry load of {reg_file.path} went boom')
        return                

    # ---
    # process the command line and set control variables as needed
    def process_command_args(self, argv):
        usage = 'usage: drat.py [-u] [-c] [-v]\n' \
                '       -u  do NOT clear patron data\n' \
                '       -c  do NOT reset app configurations\n' \
                '       -v  verbose output\n'

        try:
            opts, args = getopt.getopt(argv, "hvcud", [])
        except getopt.GetoptError as error:
            print(f'\nERROR: {error}\n')
            print (usage)
            input('Press ENTER to close . . .')
            sys.exit()

        for opt, arg in opts:
            if opt == '-h':
                print(usage)
                input('Press ENTER to close . . .')
                sys.exit()
            elif opt == '-v':
                self.verbose = True
            elif opt == '-c':
                self.reset_configs = False
            elif opt == '-u':
                self.clear_user_data = False
            elif opt == '-d':
                self.debug = True
            else:
                print(f'option {opt} not recognized')
        return

if __name__ == '__main__':
    # go do the work
    drat = Drat(sys.argv[1:])

    if drat.fatal_error:
        print('ERROR: create an incident log with full text of the error above')
        intext = input('Press ENTER to close . . .')
    else:
        # give them a chance to empty the recycle bin
        intext = input('All done. Press ENTER to close . . . . . ')
        if intext == 'r':
            print('Restarting . . .')
            os.system('shutdown /r /t 3 /c "drat restart"')
        
