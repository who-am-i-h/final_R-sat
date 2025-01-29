from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class Crypto:
    def __init__(self, key):
        self.key = key

    def aes_encrypt(self, plaintext):
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
        return cipher.iv + ct_bytes

    def aes_decrypt(self, ciphertext):
        iv = ciphertext[:AES.block_size]
        ct = ciphertext[AES.block_size:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(ct), AES.block_size)
        return decrypted.decode()
    def aes_encrypt_file(self, chunks):
        cipher = AES.new(self.key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(chunks, AES.block_size))
        return cipher.iv + ct_bytes
    def aes_decrypt_file(self, cipher_chunk):
        iv = cipher_chunk[:AES.block_size]
        ct = cipher_chunk[AES.block_size:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(ct), AES.block_size)
        return decrypted

