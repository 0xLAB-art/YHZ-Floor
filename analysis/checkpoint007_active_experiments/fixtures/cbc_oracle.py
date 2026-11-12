from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
class LocalCBC:
    def __init__(self, key, iv):
        self.key=key; self.iv=iv
    def encrypt(self, pt):
        p=padding.PKCS7(128).pad(pt)
        c=Cipher(algorithms.AES(self.key),modes.CBC(self.iv)).encryptor()
        return c.update(p)+c.finalize()
    def decrypt_bytes(self, ct):
        d=Cipher(algorithms.AES(self.key),modes.CBC(self.iv)).decryptor()
        return d.update(ct)+d.finalize()
