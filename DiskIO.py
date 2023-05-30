import os
from DiskItem import DiskItem
from send2trash import send2trash
import stat
import shutil


class DiskIO:

    verbose = True

    def __init__(self, verbosity):
        self.verbose = verbosity

    #---
    # scan a directory and return a list of items in it (f=file or shortcut, d=directory)
    def scanDir(self, dir, type=''):
        dir_items = []
        try:
            for i in os.scandir(dir):
                if (i.is_file() or i.is_symlink()) and (type=='' or type=='f'):
                    item = DiskItem(i.name, i.path, "f")
                    dir_items.append(item)
                elif i.is_dir() and (type == '' or type == 'd'):
                    item = DiskItem(i.name, i.path, "d")
                    dir_items.append(item)
        except:
            print(f'>>> Error: couldn\'t scan {dir}')
        
        return dir_items

    # ---
    # delete everything in the target dir
    def clear_dir(self, target_dir):
        # gather the current target directory items
        target_items = self.scanDir(target_dir)
        # 2. delete all files (including shortcuts) and folders in the current directory (except the desktop.ini)
        if self.verbose: print(f'Clearing {target_dir}')
        for fn in target_items:
            #target = target_items[fn].path
            if fn.filename == 'desktop.ini':
                if self.verbose: print(f'  {fn.filename} - skipped')
            elif fn.type == 'f' or fn.type == 'd':
                if self.verbose: 
                    if fn.type == 'f': print(f'  {fn.filename} - file to be deleted')
                    elif fn.type == 'd': print(f'  {fn.filename} - folder to be deleted')
                os.system(f'attrib -h "{fn.path}"') # unhide just in case
                os.chmod(fn.path, stat.S_IWRITE) # remove read-only
                send2trash(fn.path)
            else:
                if self.verbose: print(f'  {fn.filename} ok')

    # ---
    # copy items from one directory to another
    def copy_dir(self, source_dir, target_dir, readonly=False):

        if self.verbose: print(f'Restoring {target_dir}')

        expected_items = self.scanDir(source_dir)
        #expected_filenames = []
        #for item in expected_items:
        #    expected_filenames.append(item.filename)

        for fn in expected_items:
            target = os.path.join(target_dir, fn.filename)
            if fn.filename == 'desktop.ini':
                if self.verbose: print(f'  {fn.filename} - skipped')
                pass
            elif fn.type == 'f':
                if self.verbose: print(f'  {fn.filename} - file to be copied')
                shutil.copy(fn.path, target)
                if readonly: os.chmod(target, stat.S_IREAD) # set read-only
            elif fn.type == 'd':
                if self.verbose: print(f'  {fn.filename} - folder to be copied')
                shutil.copytree(fn.path, target)
                if readonly: os.chmod(target, stat.S_IREAD) # set read-only


