import os
from cryptography.fernet import Fernet
import traceback

def encrypt(path, keyPath):
    generateKey(keyPath)
    encryptFile(path, keyPath)


def generateKey(path):
    key = Fernet.generate_key()
    try:
        with open(path, "wb") as file:
            file.write(key)

        return key
    except Exception as e:
        traceback.print_exc()
        print("Key generation failed")

def loadKey(path):
    try:
        return open(path, "rb").read()
    except Exception as e:
        return "Failed to retrieve key"

def encryptFile(path, keyPath):
    key = loadKey(keyPath)
    f = Fernet(key)
    fileData = ""
    try:
        with open(path, "rb") as file:
            fileData = file.read()

    except Exception as e:
        print("Failed to read data")

    if(fileData != ""):
        encryptedData = f.encrypt(fileData)

        try:
            with open(path, "wb") as file:
                file.write(encryptedData)
        except Exception as e:
            print("Data write failed")

def decrypt(path, keyPath):
    key = loadKey(keyPath)
    f = Fernet(key)
    encryptedData = ""
    try:
        with open(path, "rb") as file:
            encryptedData = file.read()

    except Exception as e:
        print("Failed to read data")

    if(encryptedData != ""):
        decryptedData = f.decrypt(encryptedData)

    return decryptedData.decode('utf-8')

