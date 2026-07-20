#!/usr/bin/env python3
"""
Finanzfluss Copilot - Transaktionen auslesen - Firefox Version (mit Browserfenster)
"""

import keyring
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import time
import json


# Login-Daten aus Keyring holen
DIENST_NAME = "finanzfluss"
EMAIL = "XXX@mail.de"  # Hier deine E-Mail eintragen (gleich wie in save_password.py)
PASSWORD = keyring.get_password(DIENST_NAME, EMAIL)

if not PASSWORD:
    raise ValueError("Passwort nicht gefunden! Bitte zuerst mit save_password.py speichern.")

# Konten-URLs (kann später erweitert werden)
ACCOUNTS = {
    "ING": "https://www.finanzfluss.de/user/accounts/XXXX",
    "Trade Republic": "https://www.finanzfluss.de/user/accounts/XXXX"
}

options = Options()
options.headless = False

driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, 15)


def close_banner():
    """Schließt das Trial-Banner nach dem Login, falls vorhanden."""
    try:
        close_icon = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "svg path[d^='M5.11648 5.11612']")
            )
        )
        close_button = close_icon.find_element(By.XPATH, "./ancestor::button[1]")
        driver.execute_script("arguments[0].click();", close_button)
        print("Trial-Banner geschlossen.")
        time.sleep(1)
    except Exception:
        print("Kein Trial-Banner gefunden (oder bereits geschlossen).")


def login():
    """Führt den Login durch"""
    print("Öffne Login-Seite...")
    driver.get("https://www.finanzfluss.de/user/login")
    time.sleep(3)

    print("Fülle Login-Formular...")
    email_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
    email_field.clear()
    email_field.send_keys(EMAIL)

    password_field = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
    password_field.clear()
    password_field.send_keys(PASSWORD)

    print("Klicke Login-Button...")
    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()

    print("Warte auf Login...")
    time.sleep(5)

    current_url = driver.current_url
    if "finanzfluss.de/user" in current_url:
        print("Login erfolgreich!")
        close_banner()
        return True
    else:
        print("Login fehlgeschlagen!")
        return False


def set_page_size_to_100():
    """Stellt die Anzahl der angezeigten Einträge pro Seite auf 100."""
    try:
        button_100 = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-testid='paginator.bar.perPage.100']")
            )
        )
        if button_100.get_attribute("data-active") != "true":
            driver.execute_script("arguments[0].click();", button_100)
            print("Seitengröße auf 100 Einträge gesetzt.")
            time.sleep(2)
        else:
            print("Seitengröße war bereits auf 100 Einträge gesetzt.")
    except Exception:
        print("Kein '100 Elemente pro Seite'-Button gefunden (evtl. weniger als 27 Einträge).")


def get_cell_text(cell):
    """Extrahiert Text robust, unabhängig vom inneren Tag."""
    try:
        return cell.find_element(By.TAG_NAME, "p").text.strip()
    except Exception:
        pass
    try:
        return cell.find_element(By.CSS_SELECTOR, "span, div").text.strip()
    except Exception:
        pass
    return cell.text.strip()


def scrape_rows_on_current_page(account_name):
    """Extrahiert alle Transaktionszeilen der aktuell sichtbaren Seite."""
    transactions = []
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    print(f"Gefundene Transaktionen auf dieser Seite: {len(rows)}")

    for row in rows:
        try:
            cells = row.find_elements(By.TAG_NAME, "td")

            if len(cells) >= 3:
                date = get_cell_text(cells[0])
                booking_info = get_cell_text(cells[1])
                amount = get_cell_text(cells[2])

                additional_info = ""
                try:
                    info_tag = cells[0].find_element(By.CSS_SELECTOR, ".MuiBox-root .MuiTypography-body2")
                    additional_info = info_tag.text.strip()
                except Exception:
                    pass

                transaction = {
                    "datum": date,
                    "buchung": booking_info,
                    "betrag": amount,
                    "zusatzinfo": additional_info,
                    "konto": account_name
                }

                transactions.append(transaction)
                print(f"  - {date}: {booking_info} -> {amount}")

        except Exception as e:
            print(f"Fehler beim Extrahieren einer Zeile: {e}")
            continue

    return transactions


def go_to_next_page():
    """Klickt auf 'Nächste Seite', falls verfügbar. Gibt True zurück, wenn geklickt wurde."""
    try:
        next_button = driver.find_element(
            By.CSS_SELECTOR, "button[data-testid='paginationBar.button.next']"
        )
        if next_button.get_attribute("disabled") is not None or not next_button.is_enabled():
            return False

        driver.execute_script("arguments[0].click();", next_button)
        print("Nächste Seite geladen...")
        time.sleep(2)
        return True
    except Exception:
        return False


def scrape_transactions(account_name, account_url):
    """Scraped Transaktionen von einem bestimmten Konto (inkl. Pagination)"""
    print(f"\nScrape Transaktionen von {account_name}...")

    driver.get(account_url)
    time.sleep(5)

    print(f"Aktuelle URL: {driver.current_url}")

    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        print("Transaktionstabelle gefunden")
    except Exception:
        print("Keine Transaktionstabelle gefunden")
        return []

    set_page_size_to_100()

    transactions = []

    try:
        while True:
            transactions.extend(scrape_rows_on_current_page(account_name))

            if not go_to_next_page():
                break

    except Exception as e:
        print(f"Fehler beim Scrapen der Transaktionen: {e}")

    return transactions


def save_to_json(transactions, filename="transaktionen.json"):
    """Speichert Transaktionen in JSON-Datei"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(transactions, f, ensure_ascii=False, indent=2)
        print(f"Transaktionen gespeichert in {filename}")
    except Exception as e:
        print(f"Fehler beim Speichern: {e}")


def main():
    """Hauptfunktion"""
    try:
        if not login():
            return

        all_transactions = []

        for account_name, account_url in ACCOUNTS.items():
            transactions = scrape_transactions(account_name, account_url)
            all_transactions.extend(transactions)
            time.sleep(2)

        print("\n" + "="*60)
        print("GESAMTÜBERSICHT ALLER TRANSAKTIONEN")
        print("="*60)

        for transaction in all_transactions:
            print(f"{transaction['konto']} | {transaction['datum']} | {transaction['buchung']} | {transaction['betrag']}")

        save_to_json(all_transactions)

        print(f"\nGesamt: {len(all_transactions)} Transaktionen erfasst")

    except Exception as e:
        print(f"Fehler im Hauptprogramm: {e}")

    finally:
        input("\nDrücke Enter um Browser zu schließen...")
        driver.quit()


if __name__ == "__main__":
    main()
