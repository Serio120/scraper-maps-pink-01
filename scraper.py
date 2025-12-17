
import sys
import time
import pandas as pd
import urllib.parse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def scrape_data(query: str, min_results: int):
    """
    Navega directamente a Google Maps con una consulta, extrae los detalles
    de los resultados y los guarda en un archivo CSV.

    Args:
        query (str): El término de búsqueda.
        min_results (int): El número mínimo de resultados a intentar extraer.
    """
    print("Iniciando el proceso de scraping (método directo a Google Maps)...")

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_page()

        try:
            # --- 1. Construir URL y navegar directamente a Google Maps ---
            encoded_query = urllib.parse.quote_plus(query)
            maps_url = f"https://www.google.com/maps/search/{encoded_query}"
            
            print(f"Navegando directamente a: {maps_url}")
            page.goto(maps_url, timeout=30000) # Aumentar timeout para la carga inicial

            # Aceptar cookies si el botón aparece (puede aparecer también en Maps)
            try:
                # Usamos un selector más genérico para el consentimiento
                accept_button = page.locator("//button[contains(., 'Accept all') or contains(., 'Aceptar todo')]").first
                accept_button.click(timeout=5000)
                print("Banner de cookies aceptado.")
                # Espera a que la página se estabilice después del clic
                page.wait_for_load_state("networkidle")
            except PlaywrightTimeoutError:
                print("No se encontró el banner de cookies. Continuando.")

            # --- 2. Hacer scroll para cargar múltiples resultados ---
            results_panel_selector = 'div[role="feed"]'
            print(f"Esperando el panel de resultados ('{results_panel_selector}')...")
            page.wait_for_selector(results_panel_selector, state='visible', timeout=15000)
            print("Panel encontrado. Haciendo scroll para cargar resultados...")

            results_selector = f'{results_panel_selector} > div > div[role="article"]'
            
            last_count = 0
            while page.locator(results_selector).count() < min_results:
                current_count = page.locator(results_selector).count()
                print(f"Resultados cargados actualmente: {current_count}")
                # El scroll se hace sobre el panel de resultados, no sobre la página entera
                page.locator(results_panel_selector).evaluate("node => node.scrollTop = node.scrollHeight")
                try:
                    page.wait_for_load_state("networkidle", timeout=5000)
                    time.sleep(2) # Pausa para permitir la renderización
                except PlaywrightTimeoutError:
                    print("Timeout de networkidle durante el scroll, posible final de la lista.")

                new_count = page.locator(results_selector).count()
                if new_count == last_count:
                    print("No se han encontrado más resultados al hacer scroll. Deteniendo.")
                    break
                last_count = new_count

            all_results = page.locator(results_selector).all()
            print(f"Se encontraron {len(all_results)} resultados. Procediendo a la extracción.")

            # --- 3. Extraer los datos de cada resultado ---
            extracted_data = []
            for i, result_locator in enumerate(all_results[:min_results]):
                print(f"--- Procesando resultado {i+1}/{len(all_results[:min_results])} ---")
                try:
                    result_locator.click()
                    page.wait_for_load_state("networkidle", timeout=5000)
                except PlaywrightTimeoutError as e:
                    print(f"Timeout al hacer clic o esperar red. Saltando resultado. Error: {e}")
                    continue
                
                # Extraer datos del panel principal que se actualiza
                name_selector = 'h1.DUwDvf.fontHeadlineLarge'
                address_selector = 'button[data-item-id="address"]',
                website_selector = 'a[data-item-id="authority"]',
                phone_selector = 'button[data-item-id*="phone"]',
                rating_selector = 'div.F7nice'

                def get_text(selector, default="N/A"):
                    try: return page.locator(selector).first.inner_text(timeout=1000)
                    except: return default

                name = get_text(name_selector)
                address = get_text(address_selector)
                website = get_text(website_selector)
                phone = get_text(phone_selector)
                rating_text = get_text(rating_selector)

                print(f"  Nombre: {name}")

                extracted_data.append({
                    "Nombre": name,
                    "Valoracion_y_Resenas": rating_text,
                    "Direccion": address,
                    "Web": website,
                    "Telefono": phone,
                })

            # --- 4. Guardar los datos en un archivo CSV ---
            if not extracted_data:
                print("No se pudo extraer ningún dato.")
                return

            output_file = "colegios_veterinarios.csv"
            print(f"Extracción completada. Guardando datos en '{output_file}'...")
            df = pd.DataFrame(extracted_data)
            df.to_csv(output_file, index=False)
            print(f"¡Éxito! Los datos se han guardado en {output_file}.")

        except PlaywrightTimeoutError as e:
            print(f"Error de Timeout: {e}")
            page.screenshot(path="error_screenshot.png")
            print("Se ha guardado una captura de pantalla del error en 'error_screenshot.png'.")
        except Exception as e:
            print(f"Ha ocurrido un error inesperado: {e}")
            page.screenshot(path="error_screenshot.png")
            print("Se ha guardado una captura de pantalla del error en 'error_screenshot.png'.")
        finally:
            print("Cerrando el navegador.")
            browser.close()

if __name__ == "__main__":
    query_to_search = sys.argv[1] if len(sys.argv) > 1 else "Colegios Veterinarios de Cataluña"
    try: results_to_fetch = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    except ValueError: results_to_fetch = 20

    scrape_data(query=query_to_search, min_results=results_to_fetch)
