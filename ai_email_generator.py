import json
import requests
import os
from dotenv import load_dotenv
load_dotenv() # Kat-chargi les variables mn .env

# Put your Groq API Key here
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Informations d'identité (Signature)
MY_NAME = "Mehdi Annou"
MY_ROLE = "Consultant IA & Automatisation"
MY_COMPANY = "Mehdi AI Solutions"
MY_EMAIL = "annoumehdi@gmail.com"
MY_PHONE = "+212 6657111736"
CALENDLY_LINK = "https://calendly.com/mehdi-annou"

def generate_email_content(company_name, description, sector=""):
    if not description or description == "N/A":
        description = f"Entreprise opérant dans le secteur: {sector}"

    prompt = f"""
    Tu es un expert en prospection B2B et Automatisation AI au Maroc.
    Génère un e-mail de prospection très court et percutant pour l'entreprise suivante :
    - Nom : {company_name}
    - Description : {description}

    Règles de formatage HTML STRICTES :
    1. Utilise <br><br> pour les sauts de ligne (aérer le texte).
    2. Mets en gras (<b>...</b>) la valeur ajoutée principale (ex: <b>augmenter l'engagement de 30%</b> ou <b>gagner du temps</b>).
    3. Inclus le bouton/lien Calendly : <a href="{CALENDLY_LINK}">Planifier un appel de 10 min</a>.
    4. Termine par cette signature exacte :
       <br><br>
       <b>{MY_NAME}</b><br>
       {MY_ROLE} | {MY_COMPANY}<br>
       <a href="mailto:{MY_EMAIL}">{MY_EMAIL}</a> | {MY_PHONE}

    Retourne UNIQUEMENT un objet JSON valide avec 2 clés :
    - "subject": l'objet de l'email en français
    - "html_content": le corps complet de l'email en HTML
    """

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            res_data = response.json()
            content = json.loads(res_data['choices'][0]['message']['content'])
            return content.get("subject"), content.get("html_content")
        else:
            print(f"[-] Erreur Groq ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"[-] Exception IA: {e}")

    return None, None