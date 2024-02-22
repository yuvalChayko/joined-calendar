import base64
from Cryptodome.Cipher import AES
from Cryptodome import Random
import hashlib

class Encryption:
     def __init__(self, key):
         self.bs = AES.block_size
         self.key = hashlib.sha256(key.encode()).digest()

     def encrypt(self, raw):
         """
         encrypt msg
         :param raw:
         :return:
         """
         raw = self._pad(raw)
         iv = Random.new().read(AES.block_size)
         cipher = AES.new(self.key, AES.MODE_CBC, iv)
         return base64.b64encode(iv + cipher.encrypt(raw.encode()))

     def decrypt(self, enc):
         """
         decrypt msg
         :param enc:
         :return:
         """
         enc = base64.b64decode(enc)
         iv = enc[:AES.block_size]
         cipher = AES.new(self.key, AES.MODE_CBC, iv)
         return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

     def _pad(self, s):
         """
         pad msg
         :param s:
         :return:
         """
         return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)


     @staticmethod
     def _unpad(s):
         """
         unpad mag
         :param s:
         :return:
         """
         return s[:-ord(s[len(s)-1:])]


if __name__ == '__main__':

    cry = Encryption("Merry")
    length = cry.encrypt("5")
    print(length)
    print(cry.decrypt(length))
    msg = cry.encrypt("My name is meryy")
    print(msg)
    print(cry.decrypt(msg))


