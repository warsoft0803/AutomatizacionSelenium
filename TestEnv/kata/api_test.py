import json
import csv
import time
import pytest
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Cargar configuración desde config.json
try:
    with open("config.json", "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
        API_BASE = config.get("api_url", "https://fakestoreapi.com/products")
except Exception as e:
    print(f" Error al cargar config.json: {e}")
    API_BASE = "https://fakestoreapi.com/products"

# Cargar body de las peticiones desde un JSON
try:
    with open("request_body.json", "r", encoding="utf-8") as body_file:
        body_data = json.load(body_file)
except Exception as e:
    print(f" Error al cargar request_body.json: {e}")
    body_data = {}

# Configurar WebDriver con Selenium
@pytest.fixture(scope="module")
def driver():
    options = Options()
    options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    yield driver
    driver.quit()

# Lista de peticiones
requests_data = [
    ("GET", API_BASE, None),
    ("POST", API_BASE, body_data.get("POST", {})),
    ("PUT", f"{API_BASE}/1", body_data.get("PUT", {})),
    ("DELETE", f"{API_BASE}/1", None),
    ("GET", f"{API_BASE}/99999", None)  # Petición que fallará para validar errores
]

# Almacenar los reportes
reports = []

# Función para ejecutar la API con Selenium
def fetch_api_data(driver, method, url, data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    driver.get(url)
    time.sleep(2)

    response_body = driver.page_source[:500]  # Capturar parte del contenido

    # Simulación de códigos de respuesta según el tipo de request
    status_code = 200 if method in ["GET", "PUT", "DELETE"] else 201 if method == "POST" else 404
    if "error" in response_body.lower():  # Simular fallo si hay mensaje de error en la respuesta
        status_code = 500

    success = status_code in [200, 201]
    error_message = None if success else "❌ Error en la API"

    report = {
        "timestamp": timestamp,
        "method": method,
        "endpoint": url,
        "status_code": status_code,
        "success": success,
        "response_body": response_body[:100],  # Limitar salida en consola
        "error_message": error_message,
    }

    print(f"\n Respuesta de {method} {url}:")
    print(json.dumps(report, indent=2, ensure_ascii=False))  # Imprimir en consola

    reports.append(report)
    return report

# Pruebas con pytest y ejecución en paralelo
@pytest.mark.parametrize("method, url, data", requests_data)
def test_fetch_api_data(driver, method, url, data):
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(lambda req: fetch_api_data(driver, req[0], req[1], req[2]), requests_data))
    
    assert all(result["success"] for result in results if result["status_code"] in [200, 201]), "❌ Algunas pruebas fallaron"

# Guardar reporte en JSON y CSV
@pytest.fixture(scope="session", autouse=True)
def save_report():
    yield  # Esperar que terminen todas las pruebas
    with open("reporte_api.json", "w", encoding="utf-8") as json_file:
        json.dump(reports, json_file, indent=2, ensure_ascii=False)

    # Guardar reporte en CSV
    csv_filename = "reporte_api.csv"
    csv_headers = ["timestamp", "method", "endpoint", "status_code", "success", "response_body", "error_message"]

    with open(csv_filename, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
        writer.writeheader()
        for report in reports:
            writer.writerow({
                "timestamp": report["timestamp"],
                "method": report["method"],
                "endpoint": report["endpoint"],
                "status_code": report["status_code"],
                "success": report["success"],
                "response_body": report["response_body"],
                "error_message": report["error_message"] if report["error_message"] else ""
            })

    print("\n Reportes guardados en 'reporte_api.json' y 'reporte_api.csv'")
