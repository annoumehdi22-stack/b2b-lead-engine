from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel

# ==========================================
# IMPORTS DYAL LES SCRIPTS L-KHRIN
# ==========================================
from database import get_db, LeadModel
from advanced_scraper import deep_scrape_website
from search_discovery import discover_company_urls
from ai_email_generator import generate_email_content
from webhook_dispatcher import send_to_make

# ==========================================
# INITIALISATION DYAL L-APP
# ==========================================
app = FastAPI(title="Pro B2B Lead Engine")
templates = Jinja2Templates(directory="templates")

# ==========================================
# MODELS DYAL DATA (PYDANTIC)
# ==========================================
class ScrapeRequest(BaseModel):
    sector: str
    city: str
    limit: int = 5

class SendEmailRequest(BaseModel):
    lead_id: int

# ==========================================
# 1. ROUTE DYAL L-ACCUEIL (DASHBOARD)
# ==========================================
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    # Kanjbdo les leads mn SQLite mrttbin mn jdid l 9dim
    leads = db.query(LeadModel).order_by(LeadModel.updated_at.desc()).all()
    
    # T7dit jdid dyal FastAPI/Starlette
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"leads": leads}
    )

# ==========================================
# 2. ROUTE DYAL SCRAPING (DISCOVERY & DEEP SCRAPE)
# ==========================================
@app.post("/api/scrape")
def run_scrape_pipeline(data: ScrapeRequest, db: Session = Depends(get_db)):
    print(f"\n[🚀 START SCRAPE] Recherche: {data.sector} f {data.city} (Limit: {data.limit})")
    
    # 1. Discovery
    discovered_urls = discover_company_urls(data.sector, data.city, data.limit)
    print(f"[🔍 DISCOVERY] URLs l9ina ({len(discovered_urls)}): {discovered_urls}")

    processed_summary = []

    if not discovered_urls:
        print("[-] HTA URL MA L9INAH! T2ked mn search_discovery.py awla l-connexion.")
        return {"status": "success", "processed": []}

    for url in discovered_urls:
        print(f"\n[🕵️ DEEP SCRAPE] Kat-scrapi: {url}")
        existing_lead = db.query(LeadModel).filter(LeadModel.website == url).first()
        
        scraped_data = deep_scrape_website(url)
        if not scraped_data:
            print(f"[-] Ma-9drnach n-scrapio Had l-site: {url}")
            continue

        print(f"[+] Scraping réussi: {scraped_data.get('title')} | Email: {scraped_data.get('emails')}")

        if existing_lead:
            if (existing_lead.emails != scraped_data['emails']) or (existing_lead.description != scraped_data['description']):
                existing_lead.emails = scraped_data['emails']
                existing_lead.description = scraped_data['description']
                existing_lead.company_name = scraped_data['title']
                existing_lead.status = "UPDATED"
                db.commit()
                processed_summary.append({"url": url, "status": "UPDATED"})
            else:
                existing_lead.status = "NO_CHANGE"
                db.commit()
                processed_summary.append({"url": url, "status": "NO_CHANGE"})
        else:
            new_lead = LeadModel(
                website=url,
                company_name=scraped_data['title'],
                description=scraped_data['description'],
                emails=scraped_data['emails'],
                city=data.city,
                sector=data.sector,
                status="NEW"
            )
            db.add(new_lead)
            db.commit()
            processed_summary.append({"url": url, "status": "NEW"})

    print(f"[✅ FIN] Total de leads traités: {len(processed_summary)}\n")
    return {"status": "success", "processed": processed_summary}

# ==========================================
# 3. ROUTE DYAL L-IA W L-IRSAL (MAKE.COM)
# ==========================================
@app.post("/api/send_email")
def send_email_to_lead(data: SendEmailRequest, db: Session = Depends(get_db)):
    # 1. Njebdo l-lead mn l-Database
    lead = db.query(LeadModel).filter(LeadModel.id == data.lead_id).first()
    
    if not lead or not lead.emails or lead.emails == "Not Found":
        return {"status": "error", "message": "Email invalide ou introuvable."}

    # Kan-nakhdo ghir l-email l-lewel ila kanu bzaf (m-fr9in b comma)
    target_email = lead.emails.split(',')[0].strip()

    # 2. Génération dyal l-email b Groq (Llama 3)
    subject, html_content = generate_email_content(lead.company_name, lead.description, lead.sector)
    
    if not subject or not html_content:
        return {"status": "error", "message": "Erreur lors de la génération par l'IA."}

    # 3. Irsal l Webhook dyal Make.com
    success = send_to_make(target_email, subject, html_content)
    
    if success:
        # Tbedil l-status l SENT bach tban f l-dashboard
        lead.status = "SENT" 
        db.commit()
        return {"status": "success", "message": f"Email envoyé avec succès à {target_email} !"}
    else:
        return {"status": "error", "message": "Erreur lors de l'envoi au Webhook Make.com."}