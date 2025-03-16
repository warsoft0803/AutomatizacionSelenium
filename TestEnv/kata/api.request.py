import re
import json
import csv
import os
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
# Cargar configuración desde config.json
try:
    with open("config.json", "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
        API_BASE = config.get("api_url", "https://fakestoreapi.com/products")
except Exception as e:
    print(f"Error al cargar config.json: {e}")
    API_BASE = "https://fakestoreapi.com/products"  # Fallback
# Función para limpiar etiquetas HTML
def clean_html(raw_html):
    return re.sub(r'<.*?>', '', raw_html).strip()
# Función para hacer la solicitud y procesar la respuesta
def fetch_api_data(method, url, data=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        response = None
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            return {"error": f"Método {method} no soportado"}
        # Validar el código de respuesta
        status_code = response.status_code
        success = status_code in [200, 201]
        error_message = None if success else clean_html(response.text)
        
        try:
            response_body = response.json() if success else None
        except json.JSONDecodeError:
            response_body = response.text  # Guardar texto en caso de error
        report = {
            "timestamp": timestamp,
            "method": method,
            "endpoint": url,
            "status_code": status_code,
            "success": success,
            "response_body": response_body,
            "error_message": error_message,
        }
        print(f"Respuesta de {method} {url}: {json.dumps(report, indent=2, ensure_ascii=False)}")
        return report
    except Exception as e:
        return {
            "timestamp": timestamp,
            "method": method,
            "endpoint": url,
            "status_code": None,
            "success": False,
            "error_message": str(e),
        }
# Verificar si request_body.json existe, si no, crearlo con datos de ejemplo
request_body_path = "request_body.json"
if not os.path.exists(request_body_path):
    default_body = {
        "POST": {
            "title": "Producto de prueba",
            "price": 19.99,
            "category": "electronics"
        },
        "PUT": {
            "title": "Producto actualizado",
            "price": 25.99,
            "category": "home"
        }
    }
    with open(request_body_path, "w", encoding="utf-8") as body_file:
        json.dump(default_body, body_file, indent=2, ensure_ascii=False)
    print(f"Archivo {request_body_path} creado con datos de ejemplo.")
# Cargar body de las peticiones desde request_body.json
try:
    with open(request_body_path, "r", encoding="utf-8") as body_file:
        body_data = json.load(body_file)
except Exception as e:
    print(f"Error al cargar {request_body_path}: {e}")
    body_data = {}
# Definir las peticiones
requests_data = [
    ("GET", API_BASE, None),  # Obtener todos los productos
    ("POST", API_BASE, body_data.get("POST", {})),  # Crear producto
    ("PUT", f"{API_BASE}/1", body_data.get("PUT", {})),  # Actualizar producto
    ("DELETE", f"{API_BASE}/1", None)  # Eliminar producto
]
# Ejecutar en paralelo (máximo 3 hilos a la vez)
reports = []
with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(lambda req: fetch_api_data(*req), requests_data)
    reports.extend(results)
# Guardar reporte en JSON
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
            "response_body": json.dumps(report["response_body"], ensure_ascii=False) if isinstance(report["response_body"], (dict, list)) else report["response_body"],
            "error_message": report["error_message"] if report["error_message"] else ""
        })
print(f"Reporte guardado en {csv_filename} y reporte_api.json")
