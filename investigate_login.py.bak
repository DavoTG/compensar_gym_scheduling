"""
Script para extraer y analizar el JavaScript de login
"""
import requests
from bs4 import BeautifulSoup
import re

login_url = "https://seguridad.compensar.com/views/index.html?serviceProviderName=HER-SP&protocol=SAML"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print("Obteniendo página...")
response = session.get(login_url)
soup = BeautifulSoup(response.text, 'html.parser')

print("\n" + "="*80)
print("ANALIZANDO JAVASCRIPT")
print("="*80)

# Buscar todos los scripts
scripts = soup.find_all('script')

for i, script in enumerate(scripts):
    if script.string:
        # Buscar funciones de validación
        if 'valido' in script.string or 'login' in script.string.lower() or 'submit' in script.string.lower():
            print(f"\n--- SCRIPT {i+1} (Relevante para login) ---")
            print(script.string)
            print("\n")

# Buscar el action real del formulario
print("\n" + "="*80)
print("BUSCANDO ENDPOINT DE AUTENTICACIÓN")
print("="*80)

# Buscar en el HTML cualquier URL que contenga 'auth', 'login', 'signin'
urls_found = re.findall(r'https?://[^\s<>"]+(?:auth|login|signin|validate)[^\s<>"]*', response.text, re.IGNORECASE)
if urls_found:
    print("\nURLs encontradas con palabras clave de autenticación:")
    for url in set(urls_found):
        print(f"  - {url}")

# Buscar en scripts inline
ajax_calls = re.findall(r'\$\.(?:ajax|post|get)\s*\(\s*["\']([^"\']+)["\']', response.text)
if ajax_calls:
    print("\nLlamadas AJAX encontradas:")
    for call in set(ajax_calls):
        print(f"  - {call}")

# Buscar fetch calls
fetch_calls = re.findall(r'fetch\s*\(\s*["\']([^"\']+)["\']', response.text)
if fetch_calls:
    print("\nLlamadas fetch encontradas:")
    for call in set(fetch_calls):
        print(f"  - {call}")

print("\n" + "="*80)
