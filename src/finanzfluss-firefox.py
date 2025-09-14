#!/usr/bin/env python3
"""
Finanzfluss Copilot - Transaktionen auslesen - Firefox Version
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
EMAIL = "XXX@mail.de" # Hier deine E-Mail eintragen (gleich wie in save_password.py)
PASSWORD = keyring.get_password(DIENST_NAME, EMAIL)

# Überprüfen ob Passwort vorhanden ist
if not PASSWORD:
    raise ValueError("❌ Passwort nicht gefunden! Bitte zuerst mit save_password.py speichern.")

# Konten-URLs (kann später erweitert werden)
ACCOUNTS = {
    "ING": "https://www.finanzfluss.de/user/accounts/XXXX",
    "Trade Republic": "https://www.finanzfluss.de/user/accounts/XXXX"
}

# Firefox konfigurieren
options = Options()
options.headless = False

driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, 15)

def login():
    """Führt den Login durch"""
    print("Öffne Login-Seite...")
    driver.get("https://www.finanzfluss.de/user/login")
    time.sleep(3)

    print("Fülle Login-Formular...")
    # E-Mail Feld
    email_field = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='email']")))
    email_field.clear()
    email_field.send_keys(EMAIL)
    
    # Passwort Feld
    password_field = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
    password_field.clear()
    password_field.send_keys(PASSWORD)
    
    print("Klicke Login-Button...")
    # Login-Button
    login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    login_button.click()
    
    print("Warte auf Login...")
    time.sleep(5)
    
    # Überprüfe ob Login erfolgreich
    current_url = driver.current_url
    if "finanzfluss.de/user" in current_url:
        print("✅ Login erfolgreich!")
        return True
    else:
        print("❌ Login fehlgeschlagen!")
        return False

def scrape_transactions(account_name, account_url):
    """Scraped Transaktionen von einem bestimmten Konto"""
    print(f"\nScrape Transaktionen von {account_name}...")
    
    # Navigiere zur Kontoseite
    driver.get(account_url)
    time.sleep(5)
    
    print(f"Aktuelle URL: {driver.current_url}")
    
    # Warte auf die Transaktionstabelle
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        print("Transaktionstabelle gefunden")
    except:
        print("Keine Transaktionstabelle gefunden")
        return []
    
    # Extrahiere Transaktionen
    transactions = []
    
    try:
        # Finde alle Tabellenzeilen (überspringe den Header)
        rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        print(f"Gefundene Transaktionen: {len(rows)}")
        
        for row in rows:
            try:
                # Extrahiere die Zellen
                cells = row.find_elements(By.TAG_NAME, "td")
                
                if len(cells) >= 3:
                    # Datum
                    date = cells[0].find_element(By.TAG_NAME, "p").text.strip()
                    
                    # Buchungsinformationen
                    booking_info = cells[1].find_element(By.TAG_NAME, "p").text.strip()
                    
                    # Betrag
                    amount_element = cells[2].find_element(By.TAG_NAME, "p")
                    amount = amount_element.text.strip()
                    
                    # Zusätzliche Info falls vorhanden (Kontentransfer Tag)
                    additional_info = ""
                    try:
                        info_tag = cells[0].find_element(By.CSS_SELECTOR, ".MuiBox-root .MuiTypography-body2")
                        additional_info = info_tag.text.strip()
                    except:
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
        # Login
        if not login():
            return
        
        # Scrape Transaktionen von allen Konten
        all_transactions = []
        
        for account_name, account_url in ACCOUNTS.items():
            transactions = scrape_transactions(account_name, account_url)
            all_transactions.extend(transactions)
            time.sleep(2)  # Kurze Pause zwischen Konten
        
        # Ergebnisse anzeigen
        print("\n" + "="*60)
        print("GESAMTÜBERSICHT ALLER TRANSAKTIONEN")
        print("="*60)
        
        for transaction in all_transactions:
            print(f"{transaction['konto']} | {transaction['datum']} | {transaction['buchung']} | {transaction['betrag']}")
        
        # In JSON speichern
        save_to_json(all_transactions)
        
        print(f"\nGesamt: {len(all_transactions)} Transaktionen erfasst")
        
    except Exception as e:
        print(f"Fehler im Hauptprogramm: {e}")
    
    finally:
        input("\nDrücke Enter um Browser zu schließen...")
        driver.quit()

if __name__ == "__main__":
    main()