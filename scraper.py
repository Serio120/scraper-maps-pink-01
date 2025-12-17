
import sys
import time
import pandas as pd
import urllib.parse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def final_scraper(query: str, min_results: int):
    """
    Scraper definitivo de Google Maps. Utiliza selectores precisos identificados
    a través del análisis de HTML para extraer datos directamente de la lista de resultados.

    Args:
        query (str): El término de búsqueda.
        min_results (int): El número mínimo de resultados a extraer.
    """
    print("Iniciando el scraper final (v6, basado en diagnóstico HTML)...")

    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36")
        page = context.new_page()

        try:
            # --- 1. Navegar y aceptar cookies ---
            encoded_query = urllib.parse.quote_plus(query)
            maps_url = f"https://www.google.com/maps/search/{encoded_query}"
            print(f"Navegando a: {maps_url}")
            page.goto(maps_url, timeout=30000)

            try:
                consent_button = page.locator("//button[contains(., 'Accept all') or contains(., 'Aceptar todo')]").first
                consent_button.click(timeout=5000)
                print("Banner de cookies aceptado.")
                page.wait_for_load_state("networkidle", timeout=5000)
            except PlaywrightTimeoutError:
                print("No se encontró el banner de cookies.")

            # --- 2. Hacer scroll para cargar la lista de resultados ---
            feed_selector = 'div[role="feed"]'
            page.wait_for_selector(feed_selector, state='visible', timeout=20000)
            print("Panel de resultados encontrado. Cargando la lista completa...")

            result_selector = f'{feed_selector} div[role="article"]'
            while page.locator(result_selector).count() < min_results:
                current_count = page.locator(result_selector).count()
                print(f"Resultados cargados: {current_count}/{min_results}")
                page.locator(feed_selector).evaluate("node => node.scrollTo(0, node.scrollHeight)")
                time.sleep(3)
                if page.locator(result_selector).count() == current_count:
                    print("No se cargaron más resultados. Deteniendo scroll.")
                    break

            # --- 3. Extraer datos con los selectores correctos ---
            all_results = page.locator(result_selector).all()[:min_results]
            print(f"Extrayendo datos de {len(all_results)} resultados...")
            extracted_data = []

            for i, result_locator in enumerate(all_results):
                
                name, rating, address, phone = "N/A", "N/A", "N/A", "N/A"

                try:
                    # Selector para el nombre, basado en el aria-label del enlace principal
                    name = result_locator.locator("a.hfpxzc").get_attribute('aria-label')
                except: pass

                try:
                    # Selector para la valoración, basado en el role y aria-label
                    rating = result_locator.locator('span[role="img"]').get_attribute('aria-label')
                except: pass

                try:
                    # Extraer toda la información de dirección/categoría/teléfono
                    # Hay varios divs con la misma clase, los recorremos todos
                    info_divs = result_locator.locator(".W4Efsd").all()
                    full_text_info = " ".join([div.inner_text() for div in info_divs])
                    
                    # Heurística para separar dirección y teléfono
                    parts = full_text_info.split('·')
                    address = parts[1].strip() if len(parts) > 1 else "N/A"
                    phone = next((part.strip() for part in parts if '+' in part), "N/A")

                except: pass

                print(f"  - Extraído: {name}")

                extracted_data.append({
                    "Nombre": name,
                    "Valoracion_y_Resenas": rating,
                    "Direccion": address,
                    "Telefono": phone,
                })

            # --- 4. Guardar en CSV ---
            if not extracted_data:
                print("No se pudo extraer ningún dato.")
                return

            output_file = "colegios_veterinarios.csv"
            print(f"\nGuardando datos en '{output_file}'...")
            df = pd.DataFrame(extracted_data)
            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"¡ÉXITO TOTAL! Los datos se han guardado correctamente.")
            print("Puedes ver el archivo 'colegios_veterinarios.csv' en el explorador de archivos.")

        except Exception as e:
            print(f"Ha ocurrido un error inesperado: {e}")
            page.screenshot(path="error_screenshot.png")
            print(f"Se ha guardado una captura de pantalla del error en 'error_screenshot.png'.")
        finally:
            if "browser" in locals() and browser.is_connected():
                print("Cerrando el navegador.")
                browser.close()

if __name__ == "__main__":
    query_to_search = "Veterinario en Cataluña"
    results_to_fetch = 20
    final_scraper(query=query_to_search, min_results=results_to_fetch)
