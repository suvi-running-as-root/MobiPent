# 🔐 MobiPent Security Scanner

> A comprehensive mobile security testing platform for Android APK analysis with OWASP MASVS/MASTG compliance

[![Work in Progress](https://img.shields.io/badge/status-work%20in%20progress-yellow)](https://github.com/suvi-running-as-root/mobipent)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com)
[![Expo](https://img.shields.io/badge/Expo-SDK%2049+-000020.svg)](https://expo.dev)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

MobiPent combines a powerful **FastAPI backend** with an intuitive **Expo React Native frontend** to deliver enterprise-grade security analysis for Android applications. Upload APKs, run OWASP-compliant scans, and get actionable security insights—all from your mobile device.

---

## ✨ Features

### 🔑 Secure Authentication
- JWT-based signup and login
- Token-protected API endpoints
- SQLite user management

### 📱 Comprehensive APK Analysis
- **Permission Analysis** - Identify dangerous and unnecessary permissions
- **Secret Detection** - Find hardcoded API keys, tokens, and credentials
- **Cryptography Review** - Detect weak crypto implementations
- **Full OWASP MASVS Scans** - Complete security assessment aligned with MASTG standards

### 📊 Mobile-First Interface
- Clean, intuitive React Native UI
- Real-time scan progress tracking
- Detailed, actionable reports
- Cross-platform support (iOS, Android, Web)

---

## 🏗️ Architecture

```
MobiPent/
│
├── 🔧 backend/                 # FastAPI Security Engine
│   ├── main.py                 # Application entry point
│   ├── auth.py                 # JWT authentication system
│   ├── analysis/               # Security analysis modules
│   │   ├── permissions.py      # Permission analyzer
│   │   ├── crypto.py           # Cryptography checker
│   │   ├── secrets.py          # Hardcoded secret detector
│   │   └── masvs.py            # OWASP MASVS compliance
│   ├── requirements.txt        # Python dependencies
│   └── users.db                # User database
│
└── 📱 frontend/                # Expo React Native Client
    ├── App.tsx                 # Root component
    ├── src/
    │   ├── screens/            # Application screens
    │   │   ├── LoginScreen.tsx
    │   │   ├── HomeScreen.tsx
    │   │   ├── ToolsScreen.tsx
    │   │   └── ResultsScreen.tsx
    │   ├── components/         # Reusable UI components
    │   ├── api/                # API integration layer
    │   └── utils/              # Helper functions
    ├── package.json
    └── tsconfig.json
```

---

## 🛠️ Technology Stack

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.10+** | Core language |
| **FastAPI** | High-performance web framework |
| **Uvicorn** | ASGI server |
| **Androguard** | APK decompilation and analysis |
| **PyJWT** | JSON Web Token authentication |
| **SQLite** | User data persistence |

### Frontend
| Technology | Purpose |
|------------|---------|
| **Expo SDK 49+** | React Native framework |
| **TypeScript** | Type-safe development |
| **Axios** | HTTP client |
| **React Navigation** | Screen routing |
| **Expo FileSystem** | File handling |

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** and npm
- **Expo CLI** (installed globally)
- An Android device or emulator for testing

### 1️⃣ Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend running at `http://localhost:8000`

### 2️⃣ Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start Expo development server
expo start
```

📱 Scan the QR code with **Expo Go** or press:
- `a` to open on Android emulator
- `i` to open on iOS simulator
- `w` to open in web browser

### 3️⃣ Configuration

Update the API endpoint in `frontend/src/config.ts`:

```typescript
export const API_URL = 'http://YOUR_LOCAL_IP:8000';
// Example: 'http://192.168.1.100:8000'
```

⚠️ **Important**: Use your local network IP address, not `localhost`, for physical device testing.

---

## 📡 API Documentation

### Authentication Endpoints

#### Register New User
```http
POST /signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "message": "User created successfully"
}
```

#### User Login
```http
POST /login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Analysis Endpoints

#### Individual Tool Analysis
```http
POST /analyze/tool?tool_name=permissions
Authorization: Bearer <JWT_TOKEN>
Content-Type: multipart/form-data

file: <APK_FILE>
```

**Available Tools:**
- `permissions` - Permission analysis
- `crypto` - Cryptography check
- `secrets` - Hardcoded secret detection

**Response:**
```json
{
  "tool": "permissions",
  "result": { /* tool-specific data */ },
  "summary": "Analysis completed successfully"
}
```

#### Full OWASP MASVS Scan
```http
POST /analyze/whole
Authorization: Bearer <JWT_TOKEN>
Content-Type: multipart/form-data

file: <APK_FILE>
```

**Response:**
```json
{
  "app_info": { /* package, version, etc. */ },
  "permissions": { /* permission analysis */ },
  "crypto_findings": { /* crypto issues */ },
  "hardcoded_secrets": [ /* detected secrets */ ],
  "masvs_compliance": { /* OWASP checklist */ }
}
```

---

## 🔒 Security Considerations

- APK files are **temporarily stored** during analysis and **automatically deleted** afterward
- All analysis endpoints require **JWT authentication**
- Passwords are **hashed** using bcrypt before storage
- Tokens expire after **24 hours** (configurable)

---

## ⏱️ Performance Notes

| Scan Type | Typical Duration |
|-----------|-----------------|
| Single Tool | 5–15 seconds |
| Full MASVS Scan | 30–120 seconds |

*Duration varies based on APK size and complexity*

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit** your changes
   ```bash
   git commit -m "feat: add amazing feature"
   ```
4. **Push** to your branch
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open** a Pull Request

### Commit Convention
We follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation updates
- `refactor:` Code refactoring
- `test:` Test additions/updates

---

## 🗺️ Roadmap

- [ ] iOS IPA analysis support
- [ ] Dynamic analysis capabilities
- [ ] Malware detection module
- [ ] PDF report generation
- [ ] Team collaboration features
- [ ] CI/CD pipeline integration
- [ ] Docker containerization

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [OWASP MASVS](https://github.com/OWASP/owasp-masvs) - Security standards
- [Androguard](https://github.com/androguard/androguard) - APK analysis toolkit
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Expo](https://expo.dev/) - React Native development platform



</div>
