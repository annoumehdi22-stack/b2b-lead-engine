import re
import requests
import dns.resolver
import smtplib
from bs4 import BeautifulSoup
import pandas as pd

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def verify_email_free(email):
    """فحص مجاني للأيميل عبر فحص سيرڤور الـ MX ديال الدومين"""
    try:
        domain = email.split('@')[1]
        
        # 1. فحص واش الدومين عندو سيرڤور أيميل (MX Record)
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(records[0].exchange)
        
        if mx_record:
            print(f"   ✅ [Valid MX] الدومين {domain} عندو سيرڤور أيميل شغال ({mx_record})")
            return True
    except Exception:
        print(f"   ❌ [Invalid Domain] الدومين {email.split('@')[-1]} ما عندوش سيرڤور أيميل")
        return False
        
    return False

def extract_emails(text):
    """استخراج الأيميلات وتصفيتها مجاناً"""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = list(set(re.findall(email_pattern, text)))
    
    # تصفية امتدادات الصور
    clean_emails = [e for e in emails if not e.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.svg', '.gif'))]
    
    # فحص مجاني لكل أيميل
    verified_emails = []
    for email in clean_emails:
        if verify_email_free(email):
            verified_emails.append(email)
            
    return verified_emails

def scrape_domain(url):
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        
    try:
        response = requests.get(url, headers=HEADERS, timeout=12)
        if response.status_code != 200:
            print(f"[-] Access error for {url} (Status: {response.status_code})")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        emails = extract_emails(response.text)
        
        title = soup.title.string.strip() if soup.title and soup.title.string else "N/A"
        meta_desc = "N/A"
        desc_tag = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        if desc_tag and desc_tag.get('content'):
            meta_desc = desc_tag['content'].strip()
            
        return {
            "website": url,
            "title": title,
            "description": meta_desc,
            "emails": ", ".join(emails) if emails else "Not Found"
        }

    except Exception as e:
        print(f"[!] Error inspecting {url}: {e}")
        return None

def process_leads_list(urls_list):
    results = []
    print(">>> Starting Scraping & FREE Email Verification...\n")
    
    for idx, url in enumerate(urls_list, 1):
        print(f"[{idx}/{len(urls_list)}] Scraping: {url}")
        data = scrape_domain(url)
        if data:
            results.append(data)
            
    if results:
        df = pd.DataFrame(results)
        df.to_csv("scraped_leads.csv", index=False, encoding='utf-8-sig')
        print(f"\n[+] Success! Saved {len(results)} verified leads in 'scraped_leads.csv'.")

if __name__ == "__main__":
    test_urls = [
        "https://www.mediamarketing.ma",
        "https://www.inwi.ma"
    ]
    process_leads_list(test_urls)