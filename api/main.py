from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
import os

from api.auth.router import router as auth_router

app = FastAPI(title="Quant Platform API")

# Helper for root redirect
@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Quant Platform API is running. Go to /docs for Swagger UI."}

# Mount Auth Router
app.include_router(auth_router)

# Session Middleware is required for Authlib (OAuth 1.0/2.0 State)
# In production, set a real secret key
app.add_middleware(SessionMiddleware, secret_key="some-random-string")

