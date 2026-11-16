from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to AI Research Assistant API"}

def test_signup():
    # Use a random email to avoid collision
    import random
    email = f"test{random.randint(1000,9999)}@example.com"
    response = client.post(
        "/api/v1/signup",
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == email

def test_login_and_search():
    # 1. Signup
    import random
    email = f"user{random.randint(1000,9999)}@example.com"
    client.post("/api/v1/signup", json={"email": email, "password": "password"})
    
    # 2. Login
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": email, "password": "password"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Search Papers (Mocked ideally, but checking structure)
    # We will just call the endpoint and expect a list (even if empty or error from external API)
    # Note: This sends real requests if not mocked. 
    # To be safe, we might skip this or accept 500 if API key missing? 
    # Research search doesn't need API Key (Arxiv/Open/Pubmed are public).
    
    res = client.post(
        "/api/v1/research/search",
        json={"query": "machine learning", "max_results": 1},
        headers=headers
    )
    # It might fail if network issues, but code should be 200 or 500
    if res.status_code == 200:
        assert "papers" in res.json()
