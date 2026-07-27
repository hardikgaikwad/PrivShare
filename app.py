import streamlit as st
import requests
import os
import base64
from Crypto.Cipher import AES

BACKEND_URL = 'http://127.0.0.1:8000/api'

# ── Logo Base64 ────────────────────────────────────────────────────────

import base64

def get_logo_base64():
    with open("logo.png", "rb") as f:
        return base64.b64encode(f.read()).decode()

# ── Encryption helpers ────────────────────────────────────────────────────────

NONCE_SIZE = 16   # pycryptodome GCM default
TAG_SIZE = 16

def client_encrypt(file_bytes):
    key = os.urandom(32)
    nonce = os.urandom(NONCE_SIZE)  # explicit 16-byte nonce
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(file_bytes)
    # Pack as: [16-byte nonce] + [ciphertext] + [16-byte tag]
    blob = nonce + ciphertext + tag
    return blob, key.hex()

def client_decrypt(encrypted_bytes, hex_key):
    key = bytes.fromhex(hex_key)
    nonce = encrypted_bytes[:NONCE_SIZE]          # first 16 bytes
    tag = encrypted_bytes[-TAG_SIZE:]             # last 16 bytes
    ciphertext = encrypted_bytes[NONCE_SIZE:-TAG_SIZE]  # everything in between
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)

def make_share_code(token, hex_key):
    """Combine token and key into a single copyable string."""
    combined = f"{token}:{hex_key}"
    return base64.urlsafe_b64encode(combined.encode()).decode()

def parse_share_code(share_code):
    """Decode share code back into (token, hex_key)."""
    combined = base64.urlsafe_b64decode(share_code.encode()).decode()
    token, hex_key = combined.split(":", 1)
    return token, hex_key

# ── Page Config ───────────────────────────────────────────────────────────────

st.set_page_config(page_title="PrivShare", page_icon="logo.png")

logo_b64 = get_logo_base64()
st.markdown(
    f"""
    <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 0.5rem;">
        <img src="data:image/png;base64,{logo_b64}" width="52" style="border-radius: 8px;">
        <h1 style="margin: 0; padding: 0; font-size: 2.2rem;">PrivShare</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.caption("End-to-End Encrypted • Files expire in 6 hours • Max 200 MB")

# ── Upload Section ────────────────────────────────────────────────────────────

st.header("📤 Upload a File")
uploaded_file = st.file_uploader("Choose a file to share", type=None)

if uploaded_file is not None:
    if st.button("Encrypt & Upload"):
        with st.spinner("Encrypting and uploading..."):
            file_bytes = uploaded_file.read()
            encrypted_blob, hex_key = client_encrypt(file_bytes)
            response = requests.post(
                f"{BACKEND_URL}/upload/",
                files={'file': (uploaded_file.name + '.enc', encrypted_blob, 'application/octet-stream')}
            )

        if response.status_code == 201:
            data = response.json()
            share_code = make_share_code(data.get("token", ""), hex_key)
            st.session_state['share_code'] = share_code
        else:
            st.error(f"Upload failed: {response.text}")

# Persist share code across reruns
if 'share_code' in st.session_state:
    st.success("✅ File encrypted and uploaded!")
    st.warning("⚠️ Copy this share code and send it to the recipient. It contains everything needed to decrypt the file.")
    st.text_area("🔗 Share Code (copy this entire string)", value=st.session_state['share_code'], height=100)

# ── Download Section ──────────────────────────────────────────────────────────

st.divider()
st.header("📥 Download a File")

share_code_input = st.text_area("Paste Share Code here", height=100)

if st.button("Download & Decrypt"):
    if not share_code_input.strip():
        st.warning("Please paste the share code.")
    else:
        try:
            token, hex_key = parse_share_code(share_code_input.strip())
        except Exception:
            st.error("❌ Invalid share code. Please make sure you copied the entire string.")
            st.stop()

        with st.spinner("Fetching and decrypting..."):
            response = requests.get(f"{BACKEND_URL}/download/{token}/", stream=True)

        if response.status_code == 200:
            encrypted_bytes = b"".join(response.iter_content(chunk_size=8192))
            try:
                decrypted_bytes = client_decrypt(encrypted_bytes, hex_key)
                raw_name = response.headers.get("Content-Disposition", "file.enc").split('filename="')[-1].strip('"')
                original_name = raw_name.removesuffix(".enc")
                st.success("✅ File decrypted successfully!")
                st.download_button(
                    label="⬇️ Save File",
                    data=decrypted_bytes,
                    file_name=original_name,
                    mime="application/octet-stream"
                )
            except (ValueError, KeyError):
                st.error("❌ Decryption failed. The share code may be incorrect or the file tampered with.")
        elif response.status_code == 410:
            st.error("❌ This file has expired and been deleted.")
        elif response.status_code == 404:
            st.error("❌ File not found. Check that the share code is correct.")
        else:
            st.error(f"Download failed: {response.text}")