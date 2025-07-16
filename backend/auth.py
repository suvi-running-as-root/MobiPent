# pyright: reportMissingImports=false
# backend/auth.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta
import sqlite3

router = APIRouter()

SECRET_KEY = "SUPER_SECRET_KEY"
ALGORITHM = "HS256"

# === SQLite ===
def get_db():
    conn = sqlite3.connect("users.db")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT
        )"""
    )
    return conn

class User(BaseModel):
    email: str
    password: str

@router.post("/signup")
def signup(user: User):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (user.email,))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered")
    cur.execute("INSERT INTO users (email, password) VALUES (?, ?)", (user.email, user.password))
    conn.commit()
    conn.close()
    return {"message": "User created successfully"}

@router.post("/login")
def login(user: User):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ? AND password = ?", (user.email, user.password))
    if not cur.fetchone():
        raise HTTPException(status_code=401, detail="Invalid credentials")
    payload = {
        "sub": user.email,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token}
