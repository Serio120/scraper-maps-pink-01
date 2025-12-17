from playwright.sync_api import sync_playwright
import time

def run(playwright):
    # Error 1 corregido: El navegador debe ejecutarse en modo headless en un entorno de nube.
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.google.com/maps")

    print("Esperando a que la página de Google Maps cargue...")
    # Es una buena práctica esperar a que un elemento clave esté disponible.
    page.wait_for_selector('#searchboxinput', timeout=10000)

    # El código de búsqueda que tenías comentado, ahora activado.
    search_query = 'Restaurantes en San Francisco'
    print(f"Buscando: '{search_query}'...")
    page.fill('#searchboxinput', search_query)
    page.click('#searchbox-searchbutton')

    print("Esperando los resultados de la búsqueda...")
    # Esperamos a que el panel de resultados se cargue.
    page.wait_for_selector('div[role="feed"]', timeout=10000)

    print(f"Búsqueda completada. Título de la página: '{page.title()}'")

    # Error 2 corregido: Se elimina el input() para que el script no se quede colgado.
    # El navegador se cerrará automáticamente al final de la función.
    print("Cerrando el navegador.")
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
