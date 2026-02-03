from typing import Dict, Optional
from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

# Simulating a database with a dictionary
# In production, use SQLite or PostgreSQL
fake_users_db: Dict[str, dict] = {}

def get_user(db: Dict[str, dict], username: str) -> Optional[UserInDB]:
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None

def create_user(db: Dict[str, dict], user: UserInDB):
    db[user.username] = user.dict()
    return user
