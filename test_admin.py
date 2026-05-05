import requests

BASE_URL = "http://127.0.0.1:8000"

def test_admin_access():
    # 1. Login
    login_data = {
        "email": "super_admin@safeguard.com",
        "password": "password123"
    }
    print(f"Logging in with {login_data['email']}...")
    res = requests.post(f"{BASE_URL}/login", json=login_data)
    if res.status_code != 200:
        print(f"Login failed: {res.text}")
        return
    
    token = res.json()["access_token"]
    print(f"Login successful. Token: {token[:20]}...")
    
    # Decode token for debugging
    from jose import jwt
    SECRET_KEY = "safeguard_advisor_secret_key_123"
    ALGORITHM = "HS256"
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print(f"Token Payload: {payload}")

    # 2. Access Admin Users
    headers = {"Authorization": f"Bearer {token}"}
    print("Fetching admin users...")
    res = requests.get(f"{BASE_URL}/admin/users", headers=headers)
    print(f"Status Code: {res.status_code}")
    print(f"Response: {res.text}")

if __name__ == "__main__":
    test_admin_access()
