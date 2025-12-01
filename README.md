# MobiPent Security Scanner (Work in Progress)

A mobile security testing platform that lets you upload Android APKs and performs **OWASP MASVS/MASTG-compliant static analysis**.  
Built with a **FastAPI backend** and an **Expo React Native frontend**.

---

## 🔍 Features

- **User Authentication**
  - Sign up & login with **JWT**
- **APK Analysis**
  - Upload `.apk` files
  - Extract permissions, detect hard-coded secrets (e.g., `API_KEY`)
  - Generate a quick summary report
- **Mobile App**
  - Expo-powered React Native interface
  - Secure login screen, APK uploader, and results viewer
  - Cross-platform: iOS, Android, and Web

---

## 📁 Project Structure

MobiPent/
├─ backend/ # FastAPI service
│ ├─ main.py # App entrypoint & router setup
│ ├─ auth.py # Signup/login endpoints (JWT + SQLite)
│ ├─ analysis/ # Analysis modules (crypto, permissions, etc.)
│ ├─ requirements.txt # Python dependencies
│ └─ users.db # SQLite user store
└─ frontend/ # Expo React Native client
├─ App.tsx # Main app component
├─ src/
│ ├─ screens/ # Login, Home, Tools, WholeTest, etc.
│ ├─ components/ # UI & helper components
│ └─ api/ # Axios wrappers for auth & upload
├─ package.json # JS dependencies & scripts
└─ tsconfig.json # TypeScript config

yaml
Copy code

---

## ⚙️ Tech Stack

- **Backend**
  - Python 3.10+
  - FastAPI
  - Uvicorn
  - Androguard (APK decompilation & analysis)
  - PyJWT / python-jose for JWT
  - SQLite (user store)
- **Frontend**
  - Expo (React Native)
  - TypeScript
  - Axios
  - React Navigation
  - Expo FileSystem / WebView

---

## 🚀 Getting Started

### Backend

1. Create & activate a virtual environment:
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Run the server:

bash
Copy code
uvicorn main:app --reload --host 0.0.0.0 --port 8000
API will be accessible at http://localhost:8000. Make sure your device is on the same network.

Frontend
Install Expo CLI if needed:

bash
Copy code
npm install -g expo-cli
Install dependencies and start:

bash
Copy code
cd frontend
npm install
expo start
Open the app via Expo Go, iOS simulator, or Android emulator.

🔌 API Reference
Auth
POST /signup

json
Copy code
{
  "email": "you@example.com",
  "password": "yourPassword"
}
→ { "message": "User created successfully" }

POST /login

json
Copy code
{
  "email": "you@example.com",
  "password": "yourPassword"
}
→ { "access_token": "<JWT token>" }

Analysis
POST /analyze/tool

Form-data field: file (APK file)

Query param: tool_name (e.g., permissions, crypto)

Headers: Authorization: Bearer <JWT>
→ JSON with result and summary.

POST /analyze/whole

Form-data field: file (APK file)

Headers: Authorization: Bearer <JWT>
→ Full OWASP MASVS report in JSON.

🤝 Contributing
Fork the repository

Create a feature branch: git checkout -b feature/xyz

Commit your changes: git commit -m "feat: add XYZ"

Push your branch: git push origin feature/xyz

Open a Pull Request

Notes
APK files are temporarily stored for analysis and deleted afterward.

Full scans may take 30–120 seconds depending on APK size.

Update API_URL in frontend/src/config.ts to point to your backend server.

