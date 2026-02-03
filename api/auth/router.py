from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from datetime import timedelta

from api.auth.jwt import create_access_token, get_password_hash, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES
from api.users.crud import get_user, create_user
from api.users.models import UserInDB, Token
from api.auth.oauth import oauth

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
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

@router.post("/signup")
async def signup(username: str, password: str, email: str):
    if get_user(username) or get_user(email):
        raise HTTPException(status_code=400, detail="Username or Email already registered")
    
    hashed_password = get_password_hash(password)
    user_in_db = UserInDB(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    create_user(user_in_db)
    return {"message": "User created successfully"}

# --- OAuth2 Endpoints ---

@router.get("/login/google")
async def login_google(request: Request):
    redirect_uri = "http://127.0.0.1:8000/auth/callback/google"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/login/github")
async def login_github(request: Request):
    redirect_uri = "http://127.0.0.1:8000/auth/callback/github"
    return await oauth.github.authorize_redirect(request, redirect_uri)

@router.get("/callback/google")
async def callback_google(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
         raise HTTPException(status_code=400, detail=f"OAuth Error: {str(e)}")
         
    user_info = token.get('userinfo')
    if not user_info:
        # Fallback if userinfo is not in token response (depends on scope/provider)
        resp = await oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo', token=token)
        user_info = resp.json()

    email = user_info["email"]
    
    # Auto-Signup
    if not get_user(email):
         # Create user with dummy password
         hashed = get_password_hash("oauth_user")
         user_in_db = UserInDB(username=email, email=email, hashed_password=hashed)
         create_user(user_in_db)

    # Create JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": email}, expires_delta=access_token_expires
    )
    
    return RedirectResponse(url=f"http://127.0.0.1:8501/?token={access_token}")

@router.get("/callback/github")
async def callback_github(request: Request):
    try:
        token = await oauth.github.authorize_access_token(request)
    except Exception as e:
         raise HTTPException(status_code=400, detail=f"OAuth Error: {str(e)}")
         
    resp = await oauth.github.get('user', token=token)
    profile = resp.json()
    username = profile['login']
    email = profile.get('email') or f"{username}@github.com"

    if not get_user(username):
         hashed = get_password_hash("oauth_user")
         user_in_db = UserInDB(username=username, email=email, hashed_password=hashed)
         create_user(user_in_db)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return RedirectResponse(url=f"http://127.0.0.1:8501/?token={access_token}")

