#!/usr/bin/env python3
"""
Script de prueba simplificado para los endpoints de autenticacion
CU1: Iniciar Sesion
CU2: Cerrar Sesion
"""

import requests
import json

# Configuracion
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/login/"
LOGOUT_URL = f"{BASE_URL}/api/logout/"
CHECK_SESSION_URL = f"{BASE_URL}/api/check-session/"

def test_login():
    """Probar CU1: Iniciar Sesion"""
    print("=" * 50)
    print("PRUEBA CU1: INICIAR SESION")
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
            print("SUCCESS: Login exitoso!")
            return True
        else:
            print("ERROR: Login fallo!")
            return False
            
    except requests.exceptions.ConnectionError:
        print("ERROR: No se puede conectar al servidor")
        print("Asegurate de que el servidor este ejecutandose en http://localhost:8000")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_logout():
    """Probar CU2: Cerrar Sesion"""
    print("\n" + "=" * 50)
    print("PRUEBA CU2: CERRAR SESION")
    print("=" * 50)
    
    try:
        response = requests.post(LOGOUT_URL)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("SUCCESS: Logout exitoso!")
            return True
        else:
            print("ERROR: Logout fallo!")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Funcion principal de pruebas"""
    print("INICIANDO PRUEBAS DE AUTENTICACION")
    print("Servidor: http://localhost:8000")
    print("\nNota: Asegurate de que el servidor Django este ejecutandose")
    
    # Ejecutar pruebas
    tests = [
        ("Login valido", test_login),
        ("Logout", test_logout),
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
    print("\n" + "=" * 50)
    print("RESUMEN DE PRUEBAS")
    print("=" * 50)
    
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
    else:
        print("Algunas pruebas fallaron. Revisa los errores arriba.")

if __name__ == "__main__":
    main()
