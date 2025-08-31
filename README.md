# PrivShare

PrivShare is a secure file sharing application that allows users to upload and download encrypted files. Files are encrypted using AES-256 GCM, and each file has a unique download token. Files also have an expiry time after which they are no longer accessible.  

The project consists of a **Django backend** and a **Streamlit frontend**.

---

## Features

- **Secure File Upload**: Files are encrypted before storage.  
- **Download with Token**: Each file has a unique UUID token for downloading.  
- **File Expiry**: Uploaded files automatically expire after a set duration.  
- **Web Interface**: Simple UI with upload and download buttons.  

---

## Tech Stack

- **Backend**: Django, Django REST Framework  
- **Database**: PostgreSQL (NeonDB)  
- **Frontend**: Streamlit  
- **Encryption**: AES-256 GCM via Cryptography Python library  
- **Deployment**: Render (Backend), Streamlit Cloud (Frontend)  

---

## Live Demo

You can try the application online here: [PrivShare Live Demo](https://privshare.streamlit.app/)

---

## Installation (Local Setup)

1. Clone the repository:
    ```bash
    git clone https://github.com/<your-username>/privshare.git
    cd privshare
    ```

2. Create a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up environment variables:
    ```env
    DEBUG=True
    SECRET_KEY=<your-secret-key>
    DATABASE_NAME=<db_name>
    DATABASE_USER=<db_user>
    DATABASE_PASSWORD=<db_password>
    DATABASE_HOST=<db_host>
    ```

5. Apply migrations:
    ```bash
    python manage.py migrate
    ```

6. Run the development server:
    ```bash
    python manage.py runserver
    ```

---

## Usage

- Access the Streamlit frontend:
    ```bash
    streamlit run app.py
    ```
- Use the **Upload** button to upload files.  
- Copy the download URL generated for each file.  
- Paste the URL in your browser to download the file before expiry.  

---

## Deployment
- **Backend**: Deployed on [Render](https://render.com)  
- **Frontend**: Deployed on [Streamlit Cloud](https://privshare.streamlit.app/)  
- Update the `BACKEND_URL` in `app.py` to point to your Render deployment:
    ```python
    BACKEND_URL = "https://privshare.onrender.com/api"
    ```

---

## Project Structure
privshare/
    core/ # Django core settings
    files/ # Django app for file encryption and storage
    app.py # Streamlit frontend
    requirements.txt # Python dependencies
    README.md

---

## License

This project is licensed under the MIT License.  

---
