import requests
import json
from urllib.parse import urlparse
import os
from dotenv import load_dotenv
load_dotenv()
# Put your Serper API Key here
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

def discover_company_urls(sector: str, city: str, limit: int = 5):
    query = f"{sector} {city} maroc"
    print(f"\n[🔎 DISCOVERY] Serper API Kan-9lbo 3la: {query}")

    url = "https://google.serper.dev/search"
    payload = json.dumps({
      "q": query,
      "num": 20,  # Kanjbdo 20 resultat باش نضمنو نلقاو الـ limit المطلوب بعد الفلترة
      "gl": "ma"
    })
    
    headers = {
      'X-API-KEY': SERPER_API_KEY,
      'Content-Type': 'application/json'
    }

    discovered_urls = []
    
    # Liste d les annuaires, réseaux sociaux w offres d'emploi li khasna nejnnbohom
    ignored_domains = [
        'facebook.com', 'instagram.com', 'linkedin.com', 'youtube.com', 
        'twitter.com', 'yellowpages.ma', 'telecontact.ma', 'maps.google.com',
        'sortlist.com', 'indeed.com', 'glassdoor.com', 'rekrute.com',
        'optioncarriere.com', 'kerix.net', 'kompass.com', 'tripadvisor.com',
        'solos.ma', 'emplacement.ma'
    ]

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=10)
        
        if response.status_code == 200:
            results = response.json().get("organic", [])
            
            for r in results:
                link = r.get("link", "")
                domain = urlparse(link).netloc.lower()

                # Filter dyal les sites
                if link and not any(ignored in domain for ignored in ignored_domains):
                    if link not in discovered_urls:
                        discovered_urls.append(link)
                        print(f"[+] L9ina URL (Société Valide): {link}")

                # Ma kiy- حبس حتى kiy-وصل l-limit المطلوبة بالضبط
                if len(discovered_urls) >= limit:
                    break
                    
            print(f"[✅ DISCOVERY] Total URLs trouvés: {len(discovered_urls)}")
            return discovered_urls
        else:
            print(f"[-] Erreur Serper API: {response.text}")
            return []
            
    except Exception as e:
        print(f"[-] Exception Serper: {e}")
        return []