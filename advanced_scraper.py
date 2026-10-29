import requests
from bs4 import BeautifulSoup
import re
import urllib3

# Hada bach y7iyed l-warnings l-7mrin f terminal ila kan chi site ma-m-sécurisich (SSL)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def clean_emails_list(emails_found):
    """Kat-filtri les emails l-khawyin (Dummy) w tsawer"""
    dummy_domains = ['example.com', 'domain.com', 'email.com', 'test.com', 'wixpress.com', 'sentry.io']
    dummy_names = ['john.doe', 'jane.doe', 'contact@votredomaine', 'email@email', 'nom@']
    clean_list = []
    
    for email in emails_found:
        email_clean = email.lower().strip()
        
        # 1. T2ked blli l-domaine machi khawi awla d'exemple
        if not any(dummy in email_clean for dummy in dummy_domains):
            # 2. T2ked blli smiya machi d l-kdoub
            if not any(dummy in email_clean for dummy in dummy_names):
                # 3. T2ked blli machi tsawer (.png, .jpg...)
                if not email_clean.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
                    clean_list.append(email_clean)
            
    # rje3 liste n9iya bla doublons (set katsupprimi l-m3awdin)
    return list(set(clean_list))

def deep_scrape_website(url):
    print(f"\n[🕵️ DEEP SCRAPE] Kat-scrapi: {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    try:
        # verify=False muhimma bach y-dkhol hta l-sites li fihom SSL 9dim awla taye7
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        
        if response.status_code != 200:
            print(f"[-] Ma-9drnach n-scrapio Had l-site (Code: {response.status_code})")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Jbid l-Title (Smiyat l-charika)
        title_tag = soup.find('title')
        title = title_tag.text.strip() if title_tag else url.split('//')[-1].split('/')[0]
        
        # 2. Jbid l-Description
        desc = ""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc = meta_desc['content'].strip()
        else:
            # Ila ma-l9ach meta description, kay-jbed awel paragraph fih m3lomat
            for p in soup.find_all('p'):
                text = p.text.strip()
                if len(text) > 50:
                    desc = text[:150] + "..."
                    break
        
        if not desc:
            desc = "Description introuvable."
            
        # 3. Jbid les Emails (B Regex)
        page_text = soup.get_text(separator=' ')
        
        # N-zido hta les liens dyal "mailto:" bach n-t2kdou
        for a in soup.find_all('a', href=True):
            if 'mailto:' in a['href']:
                page_text += " " + a['href'].replace('mailto:', '').split('?')[0]
                
        # Regex m-jahda kat-jbed gha l-format dyal emails
        raw_emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", page_text)
        
        # N-dewzohom f l-filtre li 9adina l-fou9
        valid_emails = clean_emails_list(raw_emails)
        
        emails_str = ", ".join(valid_emails) if valid_emails else "Not Found"
        
        print(f"[+] Scraping réussi: {title[:40]}... | Email: {emails_str}")
        
        return {
            "title": title,
            "description": desc,
            "emails": emails_str
        }

    except requests.exceptions.RequestException as e:
        print(f"[!] Deep Scrape Error l-site {url}: {e}")
        return None
    except Exception as e:
        print(f"[-] Erreur inattendue l-site {url}: {e}")
        return None