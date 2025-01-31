from Crypto.Util.number import getPrime, getRandomInteger


class Dfh_client:
    def __init__(self):
        self.a = getPrime(1024)
        self.mod = getPrime(1024)
    def ret_known(self):
        return self.a, self.mod
    def private_expo(self):
        self.sec_a = getRandomInteger(1024)
        return pow(self.a, self.sec_a, self.mod)
    def genrate_secret(self, sec_b:int):
        return pow(sec_b, self.sec_a, self.mod)
    
class Dfh_server:
    def __init__(self, a, mod):
        self.a = a
        self.mod = mod
    def private_expo(self):
        self.sec_a = getRandomInteger(1024)
        return pow(self.a, self.sec_a, self.mod)
    def genrate_secret(self, sec_b):
        return pow(sec_b, self.sec_a, self.mod)