# save_password.py
import keyring

# Deine Daten
dienst_name = "finanzfluss"
email = "XXX@mail.de"
passwort = "XXX"  # Hier dein richtiges Passwort eintragen!

# Passwort im System-Keyring speichern
keyring.set_password(dienst_name, email, passwort)

print("✅ Passwort wurde sicher gespeichert!")
print(f"Service: {dienst_name}")
print(f"E-Mail: {email}")