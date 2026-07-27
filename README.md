# PrivShare 🔐

> **End-to-End Encrypted file sharing. Your files are encrypted before they leave your device — the server never sees your data.**

PrivShare is a secure, ephemeral file-sharing web application. Upload any file up to 200MB, receive a single share code, and share it with your recipient. Files are encrypted on the client side using **AES-GCM-256** before upload, stored on **AWS S3**, and automatically deleted after **6 hours**. The decryption key is embedded in the share code and is never transmitted to or stored on the server.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit%20Cloud-FF4B4B?style=for-the-badge&logo=streamlit)](https://privshare.streamlit.app/)
[![Backend](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render)](https://privshare.onrender.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

---

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                        UPLOAD FLOW                              │
│                                                                 │
│  User picks file → AES-GCM-256 key generated in browser        │
│       → File encrypted locally → Encrypted blob sent to API     │
│       → Blob stored in AWS S3 → Metadata saved in PostgreSQL    │
│       → Share Code (Base64[token:key]) shown to user           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       DOWNLOAD FLOW                             │
│                                                                 │
│  User pastes Share Code → Decoded to (token, key)              │
│       → Encrypted blob streamed from S3 via API                │
│       → File decrypted locally using key                       │
│       → Original file offered as download                      │
└─────────────────────────────────────────────────────────────────┘
```

The server is **cryptographically blind** — it stores only the encrypted blob and metadata. Without the share code, no one (including the server operator) can decrypt the file.

---

## Features

- 🔐 **True End-to-End Encryption** — AES-GCM-256 with a random 256-bit key, generated client-side for every upload
- ☁️ **AWS S3 Storage** — Encrypted blobs stored in S3; the database holds only lightweight metadata
- ⏱️ **Auto-expiry** — Files are automatically deleted after 6 hours
- 🔗 **Single Share Code** — Token and decryption key combined into one Base64 string for easy sharing
- 🌊 **Streaming Transfers** — Files are streamed to/from S3 without loading the entire file into server memory
- 🛡️ **Tamper Detection** — The GCM authentication tag will reject any file that has been modified in storage

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit (Python) |
| **Backend** | Django 5 + Django REST Framework |
| **Database** | PostgreSQL (metadata only) |
| **File Storage** | AWS S3 via `django-storages` + `boto3` |
| **Encryption** | AES-GCM-256 via `pycryptodome` (client-side) |
| **Background Tasks** | `django-background-tasks` |
| **Backend Deployment** | Render (Gunicorn) |
| **Frontend Deployment** | Streamlit Cloud |

---

## Architecture

```
┌──────────────────┐        HTTPS         ┌──────────────────────┐
│  Streamlit App   │ ──POST /api/upload/─▶ │    Django Backend     │
│  (Client-side    │                       │    (REST API)         │
│   AES-GCM-256)   │ ◀─ {token} ───────── │                       │
│                  │                       │  ┌────────────────┐   │
│  Share Code =    │        HTTPS          │  │  PostgreSQL DB │   │
│  base64(         │ ──GET /api/download/─▶│  │  (metadata)    │   │
│    token:key     │ ◀─ encrypted blob ─── │  └────────────────┘   │
│  )               │                       │          │             │
└──────────────────┘                       │          ▼             │
                                           │  ┌────────────────┐   │
                                           │  │    AWS S3      │   │
                                           │  │ (encrypted     │   │
                                           │  │  blobs)        │   │
                                           │  └────────────────┘   │
                                           └──────────────────────┘
```

---

## Local Setup

### Prerequisites
- Python 3.11 or 3.12
- PostgreSQL database (local or hosted, e.g. [Neon](https://neon.tech))
- AWS account with an S3 bucket

### 1. Clone the repository
```bash
git clone https://github.com/hardikgaikwad/PrivShare.git
cd PrivShare
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your-django-secret-key
DEBUG=True

# PostgreSQL
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host

# AWS S3
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=your_region
```

### 5. Apply database migrations
```bash
python manage.py migrate
```

### 6. Run the Django backend
```bash
python manage.py runserver
```

### 7. Run the Streamlit frontend
In a separate terminal (with the venv activated):
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

> **Note:** Make sure the `BACKEND_URL` in `app.py` is set to `http://127.0.0.1:8000/api` for local development.

---

## Deployment

### Backend → Render
1. Push this repository to GitHub.
2. Create a new **Web Service** on [Render](https://render.com).
3. Connect your GitHub repository.
4. Set the **Build Command**: `pip install -r requirements.txt && python manage.py migrate`
5. Set the **Start Command**: `gunicorn core.wsgi`
6. Add all environment variables from your `.env` file in Render's dashboard (set `DEBUG=False`).
7. Add your Render URL to `ALLOWED_HOSTS` in `core/settings.py`.

### Frontend → Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io).
2. Connect your GitHub repository and select `app.py` as the main file.
3. In **Advanced Settings → Secrets**, add:
   ```toml
   # No secrets needed — the frontend is stateless.
   # Just ensure BACKEND_URL in app.py points to your Render URL.
   ```
4. Deploy. Done!

---

## Security Design Notes

| Concern | How PrivShare handles it |
|---|---|
| Key exposure | Key is generated client-side and never sent to the server |
| IDOR / enumeration | Download tokens are UUID4 (128-bit random, not guessable) |
| Tamper detection | AES-GCM authentication tag rejects modified ciphertexts |
| Credentials | All secrets in environment variables, never in source code |
| Transport security | HTTPS/TLS enforced end-to-end |
| Data at rest | Files encrypted at application layer before reaching S3 |

---

## Encryption Format

Each uploaded file is stored as a single binary blob with the following structure:

```
[ 16 bytes: nonce ] [ N bytes: AES-GCM ciphertext ] [ 16 bytes: authentication tag ]
```

The share code given to the user is:
```
base64_url_encode( uuid_token + ":" + hex(aes_key) )
```

---

## License

This project is licensed under the [MIT License](LICENSE).
