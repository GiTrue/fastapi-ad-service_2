import requests

BASE_URL = "http://localhost:8080"

# 1. Регистрация
resp = requests.post(f"{BASE_URL}/user", json={"username": "user1", "password": "password123", "role": "user"})
print(f"User created: {resp.json()}")

# 2. Логин
resp = requests.post(f"{BASE_URL}/login", json={"username": "user1", "password": "password123"})
token = resp.json()["token"]
print(f"Logged in, token: {token}")

# 3. Создание объявления
resp = requests.post(
    f"{BASE_URL}/advertisement", 
    json={"title": "Car for sale", "description": "Good condition", "price": 5000},
    headers={"x-token": token}
)
print(f"Ad created: {resp.json()}")