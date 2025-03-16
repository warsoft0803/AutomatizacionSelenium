# README - Pruebas Automatizadas con Selenium, Pytest y API Testing

## Descripción

Este proyecto implementa pruebas automatizadas para una API utilizando Selenium, Pytest y request la cual permite realizar pruebas concurrentes, validar respuestas de la API y generar reportes en formato JSON y CSV.

## Librerías Utilizadas

Las siguientes librerías de Python son utilizadas en el proyecto:

- **json**: Para cargar configuraciones y cuerpos de peticiones desde archivos JSON.
- **csv**: Para generar reportes en formato CSV.
- **time**: Para manejar tiempos de espera en las pruebas.
- **pytest**: Para ejecutar las pruebas automatizadas.
- **datetime**: Para registrar las marcas de tiempo en los reportes.
- **concurrent.futures.ThreadPoolExecutor**: Para ejecutar múltiples peticiones en paralelo y mejorar la eficiencia de las pruebas.
- **selenium.webdriver**: Para simular el acceso a la API y capturar respuestas.
- **selenium.webdriver.chrome.service.Service**: Para administrar el servicio del navegador Chrome en Selenium.
- **selenium.webdriver.chrome.options.Options**: Para configurar Selenium en modo sin interfaz gráfica (headless).
- **webdriver_manager.chrome.ChromeDriverManager**: Para gestionar automáticamente la instalación de ChromeDriver.

## Instalación de Librerías

Para ejecutar este proyecto, debes instalar las librerías necesarias. Puedes hacerlo ejecutando el siguiente comando:

```bash
pip install selenium pytest webdriver-manager
```

## Configuración Requerida

Antes de ejecutar las pruebas, asegúrate de tener los siguientes archivos configurados:

- **config.json**: Contiene la URL base de la API.
- **request_body.json**: Contiene los cuerpos de las peticiones POST y PUT.

Ejemplo de `config.json`:

```json
{
  "api_url": "https://fakestoreapi.com/products"
}
```

Ejemplo de `request_body.json`:

```json
{
  "POST": {
    "title": "Producto de prueba",
    "price": 29.99
  },
  "PUT": {
    "title": "Producto actualizado",
    "price": 39.99
  }
}
```

## Ejecución del Script

Para ejecutar las pruebas, usa el siguiente comando:

```bash
pytest test_script.py
```

Al finalizar, se generarán los reportes en los archivos `reporte_api.json` y `reporte_api.csv` con los resultados de las pruebas.

## Comando ejecutar
Se debe ejecutar el siguiente script para generar el consumo de la apis.

python api.request.py
pytest -s api_test.py

