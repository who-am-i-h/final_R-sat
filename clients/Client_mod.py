import json
from crypton import Crypto


class Client:
    def __init__(self, key, conn, key_algo,status = True,addr = None, os = None):
        self.key = key
        self.status = status
        self.addr = addr
        self.socket = conn
        self.crypto = Crypto(self.key)
        self.os = os
        self.key_algo = key_algo

    def set_id(self, id):
        self.id = id
    def mark_offline(self):
        self.status = False 
    def mark_online(self):
        self.status = True

    def recv(self) -> str:
        data = b""
        try:
            while True:
                chunk = self.socket.recv(1024)
                if not chunk:
                    break
                data += chunk
                # print(data)
                try:
                    decrypted = self.crypto.aes_decrypt(data)
                    return json.loads(decrypted)
                except ValueError:
                    continue
        except Exception as e:
            raise e    
    def send(self, data):
        try:
            msg = json.dumps(data)
            encrypted_msg = self.crypto.aes_encrypt(msg)
            self.socket.send(encrypted_msg)
        except (TypeError, ValueError) as e:
            raise e
        except Exception as e:
            raise e
