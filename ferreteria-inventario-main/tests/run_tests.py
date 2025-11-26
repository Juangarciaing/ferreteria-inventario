"""
Script para ejecutar todos los tests
"""
import unittest
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_tests():
    """Ejecutar todos los tests"""
    # Descubrir y ejecutar tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Mostrar resumen
    print(f"\n{'='*50}")
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Errores: {len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")
    print(f"Exitosos: {result.testsRun - len(result.errors) - len(result.failures)}")
    
    if result.errors:
        print(f"\nErrores:")
        for test, error in result.errors:
            print(f"  {test}: {error}")
    
    if result.failures:
        print(f"\nFallos:")
        for test, failure in result.failures:
            print(f"  {test}: {failure}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
