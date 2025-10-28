#!/usr/bin/env python3
"""
Script de prueba para los endpoints de autenticación
CU1: Iniciar Sesión
CU2: Cerrar Sesión
"""

import requests
import json

# Configuración
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login/"
LOGOUT_URL = f"{BASE_URL}/api/auth/logout/"
CHECK_SESSION_URL = f"{BASE_URL}/api/auth/check-session/"

def test_login():
    """Probar CU1: Iniciar Sesión"""
    print("=" * 50)
    print("PRUEBA CU1: INICIAR SESIÓN")
    print("=" * 50)
    
    # Datos de prueba
    login_data = {
        "email": "admin@tienda.com",
        "contrasena": "admin123"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ Login exitoso!")
            return True
        else:
            print("❌ Login falló!")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_check_session():
    """Probar verificación de sesión"""
    print("\n" + "=" * 50)
    print("PRUEBA: VERIFICAR SESIÓN")
    print("=" * 50)
    
    try:
        response = requests.get(CHECK_SESSION_URL)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ Verificación de sesión exitosa!")
            return True
        else:
            print("❌ Verificación de sesión falló!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_logout():
    """Probar CU2: Cerrar Sesión"""
    print("\n" + "=" * 50)
    print("PRUEBA CU2: CERRAR SESIÓN")
    print("=" * 50)
    
    try:
        response = requests.post(LOGOUT_URL)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ Logout exitoso!")
            return True
        else:
            print("❌ Logout falló!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_invalid_login():
    """Probar login con credenciales inválidas"""
    print("\n" + "=" * 50)
    print("PRUEBA: LOGIN CON CREDENCIALES INVÁLIDAS")
    print("=" * 50)
    
    invalid_data = {
        "email": "usuario@inexistente.com",
        "contrasena": "password123"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=invalid_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 401:
            print("✅ Validación de credenciales inválidas funcionando!")
            return True
        else:
            print("❌ Validación de credenciales inválidas falló!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal de pruebas"""
    print("INICIANDO PRUEBAS DE AUTENTICACION")
    print("Servidor: http://localhost:8000")
    print("\nNota: Asegurate de que el servidor Django este ejecutandose")
    
    # Ejecutar pruebas
    tests = [
        ("Login válido", test_login),
        ("Verificar sesión", test_check_session),
        ("Logout", test_logout),
        ("Login inválido", test_invalid_login),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen de resultados
    print("\n" + "=" * 50)
    print("RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("Todas las pruebas pasaron exitosamente!")
    else:
        print("Algunas pruebas fallaron. Revisa los errores arriba.")

if __name__ == "__main__":
    main()
