from Advising.APIs import URL
import os, sys

def findFilePath():
    path = os.path.abspath(__file__)
    directory = os.path.dirname(path)
    print(directory)
    sys.exit(0)

def encryptURL():
    URL.encrypt("APIs/config/config.txt", "APIs/config/.gitignore.key")
    sys.exit(0)
