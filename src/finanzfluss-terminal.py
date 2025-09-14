#!/usr/bin/env python3
"""
Finanzfluss Copilot - Transaktionen auslesen - Terminal Version
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
EMAIL = "tillemil07@gmail.com"
PASSWORD = keyring.get_password(DIENST_NAME, EMAIL)

if not PASSWORD:
    raise ValueError("❌ Passwort nicht gefunden! Bitte zuerst mit save_password.py speichern.")

ACCOUNTS = {
    "ING": "https://www.finanzfluss.de/user/accounts/4076571",
    "Trade Republic": "https://www.finanzfluss.de/user/accounts/4076579"
}

# Firefox im Headless-Modus konfigurieren (kein Fenster sichtbar)
options = Options()
options.headless = True
options.add_argument("--headless")  # doppelt für Sicherheit
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")  # für korrektes Rendering

driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, 20)

def login():
    print("Öffne Login-Seite...")
    driver.get("https://www.finanzfluss.de/user/login")
    time.sleep(2)

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
    if "user/accounts" in current_url or "user" in current_url:
        print("✅ Login erfolgreich!")
        return True
    else:
        print("❌ Login fehlgeschlagen!")
        return False

def scrape_transactions(account_name, account_url):
    print(f"\nScrape Transaktionen von {account_name}...")
    driver.get(account_url)
    time.sleep(5)
    
    try:
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        print("Transaktionstabelle gefunden")
    except:
        print("Keine Transaktionstabelle gefunden")
        return []
    
    transactions = []
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    print(f"Gefundene Transaktionen: {len(rows)}")

    for row in rows:
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 3:
                date = cells[0].find_element(By.TAG_NAME, "p").text.strip()
                booking_info = cells[1].find_element(By.TAG_NAME, "p").text.strip()
                amount = cells[2].find_element(By.TAG_NAME, "p").text.strip()
                
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
    return transactions

def save_to_json(transactions, filename="transaktionen.json"):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(transactions, f, ensure_ascii=False, indent=2)
        print(f"Transaktionen gespeichert in {filename}")
    except Exception as e:
        print(f"Fehler beim Speichern: {e}")

def main():
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
        driver.quit()

if __name__ == "__main__":
    main()
