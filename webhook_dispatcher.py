import requests
import time
import os
from dotenv import load_dotenv
load_dotenv()

WEBHOOK_URL = os.getenv("MAKE_WEBHOOK_URL")

def send_to_make(email, subject, html_content):
    """كتاخد المعلومات نيشان من السيرڤور وكتصيفطها لـ Make.com"""
    if not email or email == "Not Found":
        print("[-] Email invalide, envoi annulé.")
        return False

    payload = {
        "to_email": email,
        "subject": subject,
        "html_content": html_content
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"[+] Envoye avec succès à Make.com: {email}")
            return True
        else:
            print(f"[-] Erreur {response.status_code} lors de l'envoi de {email}")
            return False
    except Exception as e:
        print(f"[!] Erreur webhook: {e}")
        return False