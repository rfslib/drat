'''
    defines an item in the filesystem (file, symlink, directory)
'''

from dataclasses import dataclass

@dataclass
class DeskItem:
    filename: str
    path: str
    type: str # f=file or symlink, d=directory

