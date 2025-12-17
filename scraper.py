from playwright.sync_api import sync_playwright
import time
import sys

def run(playwright, query):
    print("Lanzando Firefox...")
    browser = playwright.firefox.launch(headless=True)
    page = browser.new_page()

    print("Navegando a www.google.com...")
    page.goto("https://www.google.com")

    search_selector = 'textarea[title="Search"]'
    
    print(f"Página cargada. Esperando al selector...")
    page.wait_for_selector(search_selector, timeout=10000)
    print("¡Selector encontrado!")

    search_query = query
    print(f"Buscando: '{search_query}'...")
    page.fill(search_selector, search_query)
    page.press(search_selector, 'Enter')

    print("Búsqueda enviada. Esperando a que carguen los resultados...")
    page.wait_for_load_state("networkidle")

    screenshot_path = "search_results.png"
    page.screenshot(path=screenshot_path)
    print(f"Captura de pantalla de los resultados guardada en: {screenshot_path}")

    print("Cerrando el navegador.")
    browser.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query_to_search = sys.argv[1]
    else:
        query_to_search = "Playwright en Nix"
        print(f"No se proporcionó una búsqueda. Usando valor por defecto: '{query_to_search}'")

    with sync_playwright() as playwright:
        run(playwright, query_to_search)
