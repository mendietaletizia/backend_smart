#!/usr/bin/env python3
"""
Script para probar los endpoints con GET y POST
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoints():
    print("=" * 60)
    print("PROBANDO ENDPOINTS DE AUTENTICACION")
    print("=" * 60)
    
    # Probar GET en login
    print("\n1. PROBANDO GET /api/login/")
    try:
        response = requests.get(f"{BASE_URL}/api/login/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Probar GET en logout
    print("\n2. PROBANDO GET /api/logout/")
    try:
        response = requests.get(f"{BASE_URL}/api/logout/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Probar POST en login
    print("\n3. PROBANDO POST /api/login/")
    try:
        login_data = {
            "email": "admin@tienda.com",
            "contrasena": "admin123"
        }
        response = requests.post(f"{BASE_URL}/api/login/", json=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_endpoints()
