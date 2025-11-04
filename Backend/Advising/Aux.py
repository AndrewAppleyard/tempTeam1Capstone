from Advising.APIs import URL
import os, sys

def findFilePath():
    path = os.path.abspath(__file__)
    directory = os.path.dirname(path)
    return directory

def encryptURL():
    path = findFilePath()
    URL.encrypt(path + "/APIs/config/config.txt", path + "/APIs/config/.gitignore.key")
    sys.exit(0)