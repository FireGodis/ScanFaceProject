# encryption_utils.py
import os
import json
import base64
import secrets
from pathlib import Path
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend

BACKEND = default_backend()
ITERATIONS = 390000  # ajustável conforme necessidade

def _derive_key(password: str, salt: bytes) -> bytes:
    """Deriva chave (base64) a partir de senha + salt para uso com Fernet."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
        backend=BACKEND,
    )
    key = kdf.derive(password.encode("utf-8"))
    return base64.urlsafe_b64encode(key)

def init_encrypted_folder(folder_path: str, password: str):
    """
    Inicializa a pasta para uso criptografado.
    Cria folder_path se necessário e escreve .meta.json com salt e mapping vazio.
    """
    os.makedirs(folder_path, exist_ok=True)
    meta_path = os.path.join(folder_path, ".meta.json")
    if os.path.exists(meta_path):
        return  # já inicializada

    salt = secrets.token_bytes(16)
    meta = {
        "salt": base64.b64encode(salt).decode("utf-8"),
        "mapping": {},   # opcional para ofuscar nomes
        "version": 1
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f)

def load_meta(folder_path: str) -> dict:
    meta_path = os.path.join(folder_path, ".meta.json")
    if not os.path.exists(meta_path):
        raise FileNotFoundError("Meta não encontrado. Pasta não inicializada.")
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_meta(folder_path: str, meta: dict):
    meta_path = os.path.join(folder_path, ".meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f)

def get_fernet_for_folder(folder_path: str, password: str) -> Fernet:
    meta = load_meta(folder_path)
    salt = base64.b64decode(meta["salt"])
    key = _derive_key(password, salt)
    return Fernet(key)

def encrypt_bytes(folder_path: str, password: str, data: bytes) -> bytes:
    f = get_fernet_for_folder(folder_path, password)
    return f.encrypt(data)

def decrypt_bytes(folder_path: str, password: str, token: bytes) -> bytes:
    f = get_fernet_for_folder(folder_path, password)
    return f.decrypt(token)

def save_encrypted_file(file_path: str, folder_path: str, password: str, data: bytes):
    """
    Salva bytes criptografados em file_path.
    file_path deve ser um path completo (p.ex. folder_path/alguma.ext)
    """
    enc = encrypt_bytes(folder_path, password, data)
    with open(file_path, "wb") as f:
        f.write(enc)

def read_encrypted_file(file_path: str, folder_path: str, password: str) -> bytes:
    with open(file_path, "rb") as f:
        token = f.read()
    return decrypt_bytes(folder_path, password, token)
