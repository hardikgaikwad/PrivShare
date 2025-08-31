import streamlit as st
import requests
import os
from dotenv import load_dotenv

BACKEND_URL='https://privshare.onrender.com'
st.title("PrivShare")

# Upload section
st.header("Upload a file")
uploaded_file = st.file_uploader("Choose a file to share", type=None)

if uploaded_file is not None:
    if st.button("Upload"):
        files = {'file': uploaded_file.getvalue()}
        response = requests.post(f"{BACKEND_URL}/upload/", files={'file': uploaded_file})
        if response.status_code == 201:
            download_url = response.json()["download_url"]
            st.success("File uploaded successfully!")
            st.write(f"Download URL: {download_url}")
        else:
            st.error(f"Upload failed: {response.json()}")

# Download section
st.header("Download a File")
token = st.text_input("Enter Download Token (from the URL)")

if st.button("Download"):
    if token:
        response = requests.get(f"{BACKEND_URL}/download/{token}/")
        if response.status_code == 200:
            st.success("File acquired successfully!")
            file_name = response.headers.get("Content-Disposition", "file").split("filename=")[-1].strip('"')
            st.download_button(
                label="Download File",
                data=response.content,
                file_name=file_name,
                mime="applications/octet-stream"
            )
        else:
            st.error(f"Download failed: {response.json()}")