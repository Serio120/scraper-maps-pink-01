from playwright.sync_api import sync_playwright
import time

def run(playwright):
    print("Lanzando Firefox...")
    browser = playwright.firefox.launch(headless=True)
    page = browser.new_page()

    print("Navegando a una página de prueba simple...")
    page.goto("https://www.google.com")

    # CORRECCIÓN: Cambiando el título del selector a inglés ("Search"),
    # que es el idioma más probable del entorno de ejecución.
    search_selector = 'textarea[title="Search"]'
    
    print(f"Página cargada. Esperando al selector: {search_selector}")
    page.wait_for_selector(search_selector, timeout=10000)
    print("¡Éxito! El elemento clave de la página se ha encontrado.")

    search_query = 'Playwright en Nix'
    print(f"Buscando: '{search_query}'...")
    page.fill(search_selector, search_query)
    
    time.sleep(2)

    print("Cerrando el navegador.")
    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
