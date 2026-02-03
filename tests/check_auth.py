import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from api.main import app

def main():
    print("=== Phase 10 Verification: Authentication System ===")
    
    client = TestClient(app)
    
    # 1. Signup
    print("\n[1] Testing Signup...")
    signup_data = {
        "username": "test_quant",
        "password": "secure_password_123",
        "email": "quant@fund.com"
    }
    response = client.post("/signup", params=signup_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("PASS: Signup successful.")
    else:
        print("FAIL: Signup failed.")
        
    # 2. Login (Get Token)
    print("\n[2] Testing Login...")
    login_data = {
        "username": "test_quant",
        "password": "secure_password_123"
    }
    response = client.post("/token", data=login_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        token = response.json().get("access_token")
        print(f"PASS: Login successful. Token received: {token[:15]}...")
        
        # 3. Test Invalid Login
        print("\n[3] Testing Invalid Login...")
        bad_response = client.post("/token", data={"username": "test_quant", "password": "wrong_password"})
        if bad_response.status_code == 401:
            print("PASS: Invalid credentials correctly rejected.")
        else:
            print(f"FAIL: Expected 401, got {bad_response.status_code}")
            
    else:
        print("FAIL: Login failed.")
        print(response.json())

    # 4. Check OAuth Redirects
    print("\n[4] Checking OAuth Endpoints...")
    res_google = client.get("/login/google")
    print(f"Google Auth URL: {res_google.json().get('auth_url')[:40]}...")
    
    res_github = client.get("/login/github")
    print(f"GitHub Auth URL: {res_github.json().get('auth_url')[:40]}...")

if __name__ == "__main__":
    main()
