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
from send2trash import send2trash

class Drat:
    debug = False
    verbose = False # -v on the command line to override
    reset_configs = False # -c on the command line to override

    user = ""
    d = None

    target_base = 'C:\\Users\\'
    source_base = 'C:\\FSC\\drat\\'
    target_dir = ""
    source_dir = ""
    folders_src = "folders\\"
    appdata_src = "appdata\\"
    configs_src = "configs\\"

    def __init__(self, argv):
        self.process_command_args(argv)

        self.d = DiskIO(self.verbose)

        # 0. show some system information
        self.user = os.getlogin() # get the current username
        print(f'This is computer "{platform.node()}" running {platform.system()} {platform.release()} for user "{self.user}"\n')

        # 1. verify that there is a template for this user
        self.source_dir = os.path.join(self.source_base, self.user, self.folders_src)
        if(os.path.exists(self.source_dir)):
            # template exists, set up folder paths
            self.target_dir = os.path.join(self.target_base, self.user)
            # and now go...
            self.doIt()
            print(  '\nREMEMBER TO EMPTY THE RECYCLE BIN!\n'
                    'NOTE: click on the desktop and press F5 if folders are not showing as expected')
        else:
            print(f'A template does not exist for the "{self.user}" user. Aborting...')

        return

    #---
    # main starts here
    def doIt(self):

        # a) process the User folders
        self.process_folders()
        print()

        # b) process the AppData folders
        self.process_appdata()
        print()

        # c) process the .reg files
        self.process_configs
        print()

        return

    # ---
    # for each folder in the template, make the user's folder with the same name match:
    #   a: delete everything in the matching user's folders and 
    #   b: populate them with whatever's in the source template folders
    def process_folders(self):
        # gather the template directory items (directories to be cleaned up)
        source_folders = self.d.scanDir(self.source_dir, 'd')
        # clean each directory in the template: delete everything in it and copy back from the template
        for folder in source_folders:
            target_folder = os.path.join(self.target_dir, folder.filename)
            if folder.filename.lower() == 'appdata': # always skip appdata here, in case it gets added accidentally
                pass
            else:
                if self.debug: print(f'Cleaning {folder.path} from {target_folder}')
                # a: delete ...
                self.d.clear_dir(target_folder) # first delete the existing entries in the directory
                time.sleep(1) # these sleeps are to see if the screen icons will auto-update i
                                # (currently they disappear and don't re-appear until reboot or F5 on the screen)
                self.d.copy_dir(folder.path, target_folder) # then copy the correct set of files to the target directory
                time.sleep(1) # these sleeps seem to help; not sure why

    def process_appdata(self):
        # gather the names of thedirectories to replace in appdata
        # for each directory name
            # remove the existing directory in appdata
            # copy the template directory into appdata
        pass

    def process_configs(self):
        pass

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
    #main(sys.argv[1:])

    # give them the chance to empty the recycle bin
    input('Press ENTER when done . . . . . ')
    print()
