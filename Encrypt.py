from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from base64 import urlsafe_b64encode
import os
from typing import Tuple

# This class encrypts and decrypts passwords using a master password
class Encrypt:
    def __init__(self, master_password: str):
        self.master_password = master_password

    def derive_key(self, salt: bytes) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=200_000
        )
        return urlsafe_b64encode(kdf.derive(self.master_password.encode()))
    
    def getSalt(self):
        return os.urandom(16)
    
    def toEncrypt(self, salt: bytes, raw_values: list[str]) -> tuple[bytes, ...]:
        key = self.derive_key(salt)
        f = Fernet(key)
        encrypted_values = []
        for index, value in enumerate(raw_values):
            encrypted_values.append(f.encrypt(value.encode()))
        return tuple(encrypted_values)

    def toDecrypt(self, salt: bytes, encrypted_values: list[bytes]) -> tuple[str, ...]:
        key = self.derive_key(salt)
        f = Fernet(key)
        raw_values = []
        for index, value in enumerate(encrypted_values):
            raw_values.append(f.decrypt(value).decode())
        return tuple(raw_values)
    