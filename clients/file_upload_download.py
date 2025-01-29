from Client_mod import Client
import os
import socket
from pathlib import Path # https://stackoverflow.com/questions/8384737/extract-file-name-from-path-no-matter-what-the-os-path-format
from crypton import Crypto


class FileManagerServerside:
    def __init__(self, client:Client):
        self.client = client
    def file_upload(self, filepath):
        if not self.client.status:
            return "client offline"
        if not os.path.isfile(filepath):
            return "File not Exists"
        filename = Path(filepath).name
        self.client.send(f"upload {filename}")
        status = self.client.recv()
        if status == "Terminate":
            return ("Client server also have a file with the same name....")
        try:
            with open(filepath, "rb") as f:
                while chunk := f.read(1024):
                    self.client.socket.send(chunk)
            return "file sent succesfully"
        except:
            print("some error occured during sending of file")
            return("Error")

    def download(self, filename):
        self.client.socket.settimeout(1)
        if os.path.isfile(filename):
            print("file with same name already exists")
            return None
        if not self.client.status:
            print("client offline")
            return None
        self.client.send(f"download {filename}")
        status = self.client.recv()
        if status == "Terminate":
            print("file with same name already exist")
            return None
        with open(filename, "wb") as f:
            chunk = self.client.socket.recv(1024)
            while True:
                f.write(chunk)
                try:
                    chunk = self.client.socket.recv(1024)
                except socket.timeout:
                    break
            print("...............")
            self.client.socket.settimeout(None)
            f.close()
            return "file downloaded successfully"
class FileManagerClientside:
    def __init__(self, client:Client):
        self.client = client
    def upload_to_server(self, filename):
        if filename not in os.listdir():
            self.client.send("Terminate")
            return "file not exist"
        self.client.send("ready")
        try:
            with open(filename, "rb") as f:
                while chunk := f.read(1024):
                    self.client.socket.send(chunk)
            return "file uploaded"
        except:
            print("some error occured during sending of file")
            return("Error")

    def download_from_server(self, filename):
        self.client.socket
        self.client.socket.settimeout(1)
        if os.path.isfile(filename):
            print("file with same name already exists")
            self.client.send("Terminate")
            return None
        self.client.send("ready")
        with open(filename, "wb") as f:
            chunk = self.client.socket.recv(1024)
            while True:
                f.write(chunk)
                try:
                    chunk = self.client.socket.recv(1024)
                except socket.timeout:
                    break
            self.client.socket.settimeout(None)
            f.close()
            return "file downloaded"






        






