import os
from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY").encode()[:32]  # Use first 32 bytes

def encrypt_note(note: str) -> str:
    aesgcm = AESGCM(SECRET_KEY)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, note.encode(), None)
    return b64encode(nonce + ct).decode()

def decrypt_note(ciphertext: str) -> str:
    data = b64decode(ciphertext.encode())
    nonce = data[:12]
    ct = data[12:]
    aesgcm = AESGCM(SECRET_KEY)
    return aesgcm.decrypt(nonce, ct, None).decode()
