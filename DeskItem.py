'''
    defines an item in the filesystem (file, symlink, directory)
'''

from dataclasses import dataclass

@dataclass
class DeskItem:
    def __init__(self, filename, path, type):
        self.filename = filename
        self.path = path
        self.type = type # f=file, d=dir

