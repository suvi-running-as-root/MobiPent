# MobiPent Security Scanner

A mobile security testing platform that lets you upload Android APKs and performs OWASP MASVS/MASTG–compliant static analysis under the hood.  
Built with a FastAPI backend and an Expo React Native frontend.

---

## 🔍 Features

- **User Authentication**  
  - Sign up & login with JSON Web Tokens (JWT)  
- **APK Analysis**  
  - Upload `.apk` files  
  - Extract permissions, search for hard‑coded secrets (e.g. `API_KEY`)  
  - Generate a quick summary report  
- **Mobile App**  
  - Expo‑powered React Native interface  
  - Secure login screen, APK uploader, and results viewer  
  - Cross‑platform (iOS, Android, Web)

---

## 📁 Project Structure

```
MobiPent-main/
├─ backend/               # FastAPI service
│  ├─ main.py             # App entrypoint & router setup
│  ├─ auth.py             # Signup/login endpoints (JWT + SQLite)
│  ├─ analyzer.py         # `/analyze` endpoint using Androguard
│  ├─ requirements.txt    # Python dependencies
│  └─ users.db            # SQLite user store
└─ frontend/              # Expo React Native client
   ├─ App.tsx             # Main app component
   ├─ src/
   │  ├─ screens/         # Login, Home, Upload, Tools, etc.
   │  ├─ components/      # UI & helper components
   │  └─ api/             # Axios wrappers for auth & upload
   ├─ package.json        # JS dependencies & scripts
   └─ tsconfig.json       # TypeScript config
```

---

## ⚙️ Tech Stack

- **Backend**  
  - Python 3.9+  
  - FastAPI  
  - Uvicorn  
  - Androguard (APK decompilation & analysis)  
  - PyJWT / python‑jose for JWT  
  - SQLite (simple user store)

- **Frontend**  
  - Expo (React Native)  
  - TypeScript  
  - Axios for HTTP requests  
  - React Navigation (bottom tabs)  
  - Expo File System / WebView

---

## 🚀 Getting Started

### 1. Backend

1. Create & activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. (Optional) Edit `APKTOOL_BAT_PATH` in `backend/main.py` if you want to integrate with Apktool.
4. Run the server:
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```
   → API now lives at `http://localhost:8000`

### 2. Frontend

1. Install Expo CLI (if not already):
   ```bash
   npm install -g expo-cli
   ```
2. Install dependencies and start:
   ```bash
   cd frontend
   npm install
   expo start
   ```
3. Choose your target (Android, iOS simulator, or web).

---

## 🔌 API Reference

### Auth

- **POST** `/signup`  
  ```json
  {
    "email": "you@example.com",
    "password": "yourPassword"
  }
  ```
  → `{ "message": "User created successfully" }`

- **POST** `/login`  
  ```json
  {
    "email": "you@example.com",
    "password": "yourPassword"
  }
  ```
  → `{ "access_token": "<JWT token>" }`

### Analysis

- **POST** `/analyze`  
  - Form‑data field: `file` (the `.apk` to scan)  
  - Headers: `Authorization: Bearer <JWT token>`  
  → JSON with `permissions`, `secrets`, and a `summary`.

---

## 🤝 Contributing

1. Fork this repo  
2. Create a feature branch (`git checkout -b feature/name`)  
3. Commit your changes (`git commit -m "feat: add XYZ"`)  
4. Push to your branch (`git push origin feature/name`)  
5. Open a Pull Request

Please keep code style consistent, write clear commit messages, and add tests where applicable.

---



---

*What this really means is:* you can spin up a local server, log in via the mobile app, upload any Android APK, and get back a quick rundown of its permissions and any string constants that look like secrets. Perfect for a first‑pass pentest or for educational demos.

