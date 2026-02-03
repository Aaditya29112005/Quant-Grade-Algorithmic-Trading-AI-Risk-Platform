from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse
import os

# Required for Authlib to work over HTTP (localhost)
os.environ['AUTHLIB_INSECURE_TRANSPORT'] = '1'

app = FastAPI(title="Quant Platform API")

# Explicit Session Configuration for Local Development
app.add_middleware(
    SessionMiddleware, 
    secret_key="quant-platform-super-secret-key",
    same_site="lax",
    https_only=False
)

# Mount Auth Router
from api.auth.router import router as auth_router
app.include_router(auth_router)

# Helper for root redirect
@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Quant Platform API is running. Go to /docs for Swagger UI."}

