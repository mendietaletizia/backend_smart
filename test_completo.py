#!/usr/bin/env python3
"""
Script de prueba mejorado para los endpoints de autenticacion
CU1: Iniciar Sesion
CU2: Cerrar Sesion
Mantiene las sesiones entre llamadas HTTP
"""

import requests
import json

# Configuracion
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/login/"
LOGOUT_URL = f"{BASE_URL}/api/logout/"
CHECK_SESSION_URL = f"{BASE_URL}/api/check-session/"

def test_login_and_logout():
    """Probar CU1 y CU2: Login y Logout con sesion persistente"""
    print("=" * 60)
    print("PRUEBA COMPLETA: LOGIN Y LOGOUT CON SESION PERSISTENTE")
    print("=" * 60)
    
    # Crear una sesion que mantenga las cookies
    session = requests.Session()
    
    # Datos de prueba
    login_data = {
        "email": "admin@tienda.com",
        "contrasena": "admin123"
    }
    
    # PASO 1: Iniciar sesion
    print("\n1. INICIANDO SESION...")
    try:
        response = session.post(LOGIN_URL, json=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("SUCCESS: Login exitoso!")
            login_success = True
        else:
            print("ERROR: Login fallo!")
            login_success = False
            return False
            
    except Exception as e:
        print(f"ERROR en login: {e}")
        return False
    
    # PASO 2: Verificar sesion activa
    print("\n2. VERIFICANDO SESION ACTIVA...")
    try:
        response = session.get(CHECK_SESSION_URL)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200 and response.json().get('authenticated'):
            print("SUCCESS: Sesion verificada correctamente!")
        else:
            print("ERROR: Sesion no verificada!")
            
    except Exception as e:
        print(f"ERROR verificando sesion: {e}")
    
    # PASO 3: Cerrar sesion
    print("\n3. CERRANDO SESION...")
    try:
        response = session.post(LOGOUT_URL)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("SUCCESS: Logout exitoso!")
            logout_success = True
        else:
            print("ERROR: Logout fallo!")
            logout_success = False
            
    except Exception as e:
        print(f"ERROR en logout: {e}")
        logout_success = False
    
    # PASO 4: Verificar que la sesion se cerro
    print("\n4. VERIFICANDO QUE LA SESION SE CERRO...")
    try:
        response = session.get(CHECK_SESSION_URL)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200 and not response.json().get('authenticated'):
            print("SUCCESS: Sesion cerrada correctamente!")
            session_closed = True
        else:
            print("ERROR: Sesion aun activa!")
            session_closed = False
            
    except Exception as e:
        print(f"ERROR verificando cierre de sesion: {e}")
        session_closed = False
    
    return login_success and logout_success and session_closed

def test_invalid_login():
    """Probar login con credenciales inválidas"""
    print("\n" + "=" * 60)
    print("PRUEBA: LOGIN CON CREDENCIALES INVALIDAS")
    print("=" * 60)
    
    invalid_data = {
        "email": "usuario@inexistente.com",
        "contrasena": "password123"
    }
    
    try:
        response = requests.post(LOGIN_URL, json=invalid_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 401:
            print("SUCCESS: Validacion de credenciales invalidas funcionando!")
            return True
        else:
            print("ERROR: Validacion de credenciales invalidas fallo!")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_logout_without_session():
    """Probar logout sin sesion activa"""
    print("\n" + "=" * 60)
    print("PRUEBA: LOGOUT SIN SESION ACTIVA")
    print("=" * 60)
    
    try:
        response = requests.post(LOGOUT_URL)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 400:
            print("SUCCESS: Validacion de logout sin sesion funcionando!")
            return True
        else:
            print("ERROR: Validacion de logout sin sesion fallo!")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Funcion principal de pruebas"""
    print("INICIANDO PRUEBAS COMPLETAS DE AUTENTICACION")
    print("Servidor: http://localhost:8000")
    print("\nNota: Asegurate de que el servidor Django este ejecutandose")
    
    # Ejecutar pruebas
    tests = [
        ("Login y Logout completo", test_login_and_logout),
        ("Login invalido", test_invalid_login),
        ("Logout sin sesion", test_logout_without_session),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"ERROR en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen de resultados
    print("\n" + "=" * 60)
    print("RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("Todas las pruebas pasaron exitosamente!")
        print("Los casos de uso CU1 (Iniciar Sesion) y CU2 (Cerrar Sesion) estan funcionando correctamente!")
    else:
        print("Algunas pruebas fallaron. Revisa los errores arriba.")

if __name__ == "__main__":
    main()
