from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from base64 import urlsafe_b64encode, urlsafe_b64decode
import os

class AESEncryptor:
    
    def _derive_key(self, sal, password) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=sal,
            iterations=100000,
        )
        return kdf.derive(password.encode())

    def encrypt(self, plaintext: str, password: str) -> str:
        salt = os.urandom(16)
        key = self._derive_key(salt, password)
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
        # Include salt + nonce + ciphertext in output
        return urlsafe_b64encode(salt + nonce + ciphertext).decode()

    def decrypt(self, token: str, password: str) -> str:
        data = urlsafe_b64decode(token.encode())
        salt = data[:16]
        nonce = data[16:28]
        ciphertext = data[28:]

        key = self._derive_key(salt, password)
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode()


