from authlib.integrations.starlette_client import OAuth
import os
from dotenv import load_dotenv

load_dotenv()

from starlette.middleware.sessions import SessionMiddleware

oauth = OAuth()

# Load env vars or use dummies
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "dummy")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "dummy")

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "dummy")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "dummy")

oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

oauth.register(
    name='github',
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    access_token_url='https://github.com/login/oauth/access_token',
    access_token_params=None,
    authorize_url='https://github.com/login/oauth/authorize',
    authorize_params=None,
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)
