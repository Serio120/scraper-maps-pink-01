
import sys
import time
import pandas as pd
import urllib.parse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def scrape_data(query: str, min_results: int):
    """
    Navega directamente a Google Maps con una consulta de búsqueda mejorada, extrae
    detalles usando selectores robustos y los guarda en un archivo CSV.

    Args:
        query (str): El término de búsqueda.
        min_results (int): El número mínimo de resultados a intentar extraer.
    """
    print("Iniciando el proceso de scraping (v4, enfoque directo y robusto)...")

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        # Usar un user agent común para evitar ser bloqueado
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0")
        page = context.new_page()

        try:
            # --- 1. Navegar directamente a Google Maps ---
            encoded_query = urllib.parse.quote_plus(query)
            maps_url = f"https://www.google.com/maps/search/{encoded_query}"
            
            print(f"Navegando directamente a: {maps_url}")
            page.goto(maps_url, timeout=30000)

            # --- Aceptar Cookies (si aparece) ---
            try:
                # Selector genérico para el botón de consentimiento
                consent_button = page.locator("//form[.//button[contains(., 'Accept all') or contains(., 'Aceptar todo')]]//button").last
                consent_button.click(timeout=5000)
                print("Banner de cookies aceptado.")
                page.wait_for_load_state("networkidle", timeout=5000)
            except PlaywrightTimeoutError:
                print("No se encontró el banner de cookies o ya fue aceptado.")

            # --- 2. Hacer Scroll para Cargar Resultados ---
            feed_selector = 'div[role="feed"]'
            print(f"Esperando el panel de resultados ('{feed_selector}')...")
            page.wait_for_selector(feed_selector, state='visible', timeout=20000)
            print("Panel encontrado. Haciendo scroll para cargar resultados...")

            result_selector = f'{feed_selector} div[role="article"]'
            loaded_results = page.locator(result_selector)
            
            previous_count = 0
            while loaded_results.count() < min_results:
                current_count = loaded_results.count()
                print(f"Resultados cargados: {current_count}/{min_results}")
                
                # Hace scroll en el panel de resultados
                page.locator(feed_selector).evaluate("node => node.scrollTo(0, node.scrollHeight)")
                # Espera un tiempo fijo para que los nuevos resultados se carguen y rendericen
                time.sleep(3)

                if loaded_results.count() == current_count:
                    print("No se han encontrado más resultados al hacer scroll. Deteniendo.")
                    break
            
            all_results = loaded_results.all()[:min_results]
            print(f"Se procesarán {len(all_results)} resultados. Extrayendo datos...")

            # --- 3. Extraer Datos con Selectores Robustos ---
            extracted_data = []
            for i, result_locator in enumerate(all_results):
                print(f"--- Procesando resultado {i+1}/{len(all_results)} ---")
                try:
                    result_locator.click()
                    # Espera a que el panel principal se actualice después del clic
                    time.sleep(2)
                except Exception as e:
                    print(f"Error al hacer clic en el resultado. Saltando. Error: {e}")
                    continue
                
                # Panel principal que contiene los detalles del lugar
                details_panel_selector = 'div[role="main"]'
                main_panel = page.locator(details_panel_selector).first

                # Función para extraer texto de forma segura
                def get_text_from_panel(selector, default="N/A"):
                    try: return main_panel.locator(selector).first.inner_text(timeout=1500)
                    except: return default

                # El nombre es casi siempre el H1
                name = get_text_from_panel('h1')
                
                # Usamos selectores de atributos que son más estables
                address = get_text_from_panel('button[data-item-id="address"]')
                website = get_text_from_panel('a[data-item-id="authority"]')
                phone = get_text_from_panel('button[data-item-id*="phone"]')
                rating_text = get_text_from_panel('div.F7nice')

                print(f"  Nombre: {name}")

                extracted_data.append({
                    "Nombre": name,
                    "Valoracion_y_Resenas": rating_text.replace("\n", " "),
                    "Direccion": address,
                    "Web": website,
                    "Telefono": phone,
                })

            # --- 4. Guardar en CSV ---
            if not extracted_data:
                print("No se pudo extraer ningún dato.")
                return

            output_file = "colegios_veterinarios.csv"
            print(f"Extracción completada. Guardando datos en '{output_file}'...")
            df = pd.DataFrame(extracted_data)
            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"¡Éxito! Los datos se han guardado en {output_file}.")

        except Exception as e:
            print(f"Ha ocurrido un error inesperado: {e}")
            page.screenshot(path="error_screenshot.png")
            print("Se ha guardado una captura de pantalla del error en 'error_screenshot.png'.")
        finally:
            print("Cerrando el navegador.")
            if "browser" in locals() and browser.is_connected():
                browser.close()

if __name__ == "__main__":
    # Consulta de búsqueda mejorada por defecto
    query_to_search = sys.argv[1] if len(sys.argv) > 1 else "Veterinario en Cataluña"
    try:
        results_to_fetch = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    except (ValueError, IndexError):
        results_to_fetch = 20

    scrape_data(query=query_to_search, min_results=results_to_fetch)
