# Finanzfluss Exporter 🚀

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Selenium](https://img.shields.io/badge/selenium-supported-green)
![License: MIT](https://img.shields.io/badge/license-MIT-yellow)

**Finanzfluss Exporter** ist ein Python-Skript, das automatisch Transaktionen aus einer Web-Finanzanwendung ausliest und in einer JSON-Datei speichert. Ideal für Entwickler, die ihre Finanzdaten automatisiert analysieren oder weiterverarbeiten möchten.

---

## Features ✨

- Automatisches Einloggen in die Finanz-Webanwendung mit Selenium.
- Scraping von Transaktionen verschiedener Konten.
- Extrahiert: Datum, Buchungsinformationen, Betrag, Zusatzinformationen und Konto.
- Ausgabe als JSON-Datei (`transaktionen.json`) für Weiterverarbeitung.
- Übersichtliche Konsolen-Ausgabe aller Transaktionen.
- Einfach erweiterbar für weitere Konten oder Analysefunktionen.

---

## Badges / GitHub-Integrationen 🛠

- **Python-Version**: 3.8+
- **Selenium-Unterstützung**: ✔
- **Lizenz**: MIT
- **CI/CD**: GitHub Actions möglich (z.B. automatisches Testen von Skripten oder Linting)

Beispiel GitHub Actions Workflow `.github/workflows/python-app.yml`:

```yaml
name: Python application

on: [push, pull_request]

jobs:
  build:

    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: pip install selenium
    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 .
````

---

## Voraussetzungen 📦

* Python 3.8+
* [Selenium](https://pypi.org/project/selenium/)
* Firefox-Browser
* [Geckodriver](https://github.com/mozilla/geckodriver/releases) im PATH

Installation von Selenium:

```bash
pip install selenium
```

---

## Einrichtung ⚙️

1. **Login-Daten eintragen**
   Öffne `finanzfluss_copilot.py` und trage deine Daten ein:

```python
EMAIL = "deine_email@beispiel.de"
PASSWORD = "dein_passwort"
```

> ⚠️ Sicherheit: Passwort im Klartext, Datei sicher aufbewahren!

2. **Konten konfigurieren**
   Füge weitere Konten in der Variable `ACCOUNTS` hinzu:

```python
ACCOUNTS = {
    "ING": "https://www.deine-finanz-app.de/user/accounts/4076571",
    "Trade Republic": "https://www.deine-finanz-app.de/user/accounts/4076579"
}
```

3. **Geckodriver installieren**
   Stelle sicher, dass Geckodriver im System-PATH liegt.

---

## Nutzung 🚀

```bash
python finanzfluss_copilot.py
```

* Firefox öffnet sich und loggt dich automatisch ein.
* Transaktionen werden ausgelesen und in der Konsole angezeigt.
* Ergebnisse werden in `transaktionen.json` gespeichert.
* Nach Abschluss Enter drücken, um den Browser zu schließen.

---

## JSON-Beispiel 📝

```json
[
  {
    "datum": "2025-09-14",
    "buchung": "Gehalt",
    "betrag": "2500,00 €",
    "zusatzinfo": "",
    "konto": "ING"
  },
  {
    "datum": "2025-09-10",
    "buchung": "Online Shopping",
    "betrag": "-45,99 €",
    "zusatzinfo": "Kreditkartenabbuchung",
    "konto": "Trade Republic"
  }
]
```

---

## Sicherheit & Hinweise ⚠️

* Änderungen auf der Finanz-Webseite können das Skript unterbrechen.
* Zugangsdaten niemals öffentlich teilen.
* Nutzung solcher Skripte erfolgt auf eigene Verantwortung – offizielle Erlaubnis durch Anbieter nicht gegeben.

---

## Ausblick / Ideen 💡

* Automatische Speicherung in Datenbanken (SQLite, PostgreSQL, etc.).
* Erstellung von Monatsberichten oder Diagrammen.
* Export in CSV oder Excel.
* Erweiterung auf weitere Finanz-Tools oder APIs.

---

## Lizenz 📄

Dieses Projekt ist unter der **MIT-Lizenz** lizenziert. Siehe [LICENSE](LICENSE) für Details.

---

## Beispiel-Daten für Tests 📂

Für die Entwicklung können Beispieldaten direkt ins Repo gelegt werden:

`sample_transaktionen.json`:

```json
[
  {
    "datum": "2025-01-01",
    "buchung": "Test-Transaktion",
    "betrag": "100,00 €",
    "zusatzinfo": "",
    "konto": "ING"
  }
]
```

Damit lassen sich Funktionen entwickeln und testen, ohne sich immer einloggen zu müssen.

---

**Viel Spaß beim Auslesen deiner Transaktionen! 🚀**
