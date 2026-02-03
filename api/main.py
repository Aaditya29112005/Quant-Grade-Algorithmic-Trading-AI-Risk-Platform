from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Optional
import os

from api.auth import (
    create_access_token, 
    get_password_hash, 
    verify_password, 
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_google_auth_url,
    get_github_auth_url
)
from api.db_users import fake_users_db, get_user, create_user, UserInDB, User

app = FastAPI(title="Quant Platform API")

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(fake_users_db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/signup")
async def signup(username: str, password: str, email: str):
    if get_user(fake_users_db, username):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(password)
    user_in_db = UserInDB(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    create_user(fake_users_db, user_in_db)
    return {"message": "User created successfully"}

import httpx
from fastapi.responses import RedirectResponse

# OAuth Configuration (Load from ENV in production)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "dummy_client_id")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "dummy_secret")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "dummy_client_id")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "dummy_secret")

# Redirect URIs (Must match Console)
REDIRECT_URI_GOOGLE = "http://localhost:8000/callback/google"
REDIRECT_URI_GITHUB = "http://localhost:8000/callback/github"

@app.get("/login/google")
async def login_google():
    return {"auth_url": get_google_auth_url(GOOGLE_CLIENT_ID, REDIRECT_URI_GOOGLE)}

@app.get("/login/github")
async def login_github():
    return {"auth_url": get_github_auth_url(GITHUB_CLIENT_ID, REDIRECT_URI_GITHUB)}

@app.get("/callback/google")
async def callback_google(code: str):
    async with httpx.AsyncClient() as client:
        # 1. Exchange Code for Token
        token_res = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": REDIRECT_URI_GOOGLE,
            },
        )
        token_data = token_res.json()
        if "access_token" not in token_data:
            raise HTTPException(status_code=400, detail="Failed to retrieve Google token")
        
        # 2. Get User Info
        user_res = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
        user_info = user_res.json()
        email = user_info.get("email")
        
        # 3. Create/Get Local User & Token
        if not get_user(fake_users_db, email):
            # Auto-signup
            user_in_db = UserInDB(
                username=email,
                email=email,
                hashed_password=get_password_hash("oauth_user") # Dummy password
            )
            create_user(fake_users_db, user_in_db)
            
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": email}, expires_delta=access_token_expires
        )
        
        # 4. Redirect to Dashboard with Token
        return RedirectResponse(url=f"http://localhost:8501/?token={access_token}")

@app.get("/callback/github")
async def callback_github(code: str):
    async with httpx.AsyncClient() as client:
        # 1. Exchange Code for Token
        token_res = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": REDIRECT_URI_GITHUB,
            },
        )
        token_data = token_res.json()
        if "access_token" not in token_data:
             raise HTTPException(status_code=400, detail="Failed to retrieve GitHub token")
        
        # 2. Get User Info
        user_res = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
        user_info = user_res.json()
        username = user_info.get("login")
        
        # 3. Create/Get Local User
        if not get_user(fake_users_db, username):
             user_in_db = UserInDB(
                username=username,
                email=f"{username}@github.com",
                hashed_password=get_password_hash("oauth_user")
            )
             create_user(fake_users_db, user_in_db)
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username}, expires_delta=access_token_expires
        )
        
        return RedirectResponse(url=f"http://localhost:8501/?token={access_token}")

@app.get("/")
async def root():
    return {"message": "Welcome to Quant Platform API"}
