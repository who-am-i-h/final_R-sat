from tinyec import registry
import secrets
from tinyec.ec import Point
curve = registry.get_curve("brainpoolP256r1")

class ECDH:
    def __init__(self):
        self.G = curve.g
        self.private_key = secrets.randbelow(curve.field.n)
        self.public_key = self.G * self.private_key

    def generate_secret(self, other_public_key_x, other_public_key_y):
        other_public_key = Point(curve, other_public_key_x, other_public_key_y)
        key = other_public_key*self.private_key
        return key.x
    




        


