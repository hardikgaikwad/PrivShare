import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from django.utils import timezone
from .models import EncryptedFile

def encrypt_file(file_bytes):
    key = os.urandom(32)   # AES-256
    iv = os.urandom(12)    # GCM standard
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()
    encrypted_data = encryptor.update(file_bytes) + encryptor.finalize()
    tag = encryptor.tag
    return encrypted_data, key, iv, tag

def decrypt_file(encrypted_data, key, iv, tag):
    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),   # Include tag
        backend=default_backend()
    ).decryptor()
    return decryptor.update(encrypted_data) + decryptor.finalize()

def cleanup():
    now = timezone.now()
    expired_files = EncryptedFile.objects.filter(expiry_time__lt=now)
    count = expired_files.count()
    if count > 0:
        expired_files.delete()
    return count
