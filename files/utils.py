from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

def encrypt_file(file_bytes):
    key = os.urandom(32)
    iv = os.urandom(12)
    encryptor = Cipher(algorithms.AES(key), modes.GCM(iv)).encryptor()
    encrypted_data = encryptor.update(file_bytes) + encryptor.finalize()
    return encrypted_data, key, iv, encryptor.tag

def decrypt_file(encrypted_data, key, iv, tag):
    decryptor = Cipher(algorithms.AES(key), modes.GCM(iv)).decryptor()
    return decryptor.update(encrypted_data) + decryptor.finalize()