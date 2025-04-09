from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
from datetime import datetime

# Import local modules
from app.scraper.scraper import GoogleMapsScraper
from app.database.database import get_db, Lead, create_tables

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Jarvis Lead Finder API", 
              description="API for finding local businesses with weak online presence")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def startup():
    logger.info("Creating database tables if they don't exist")
    create_tables()

# Define request and response models
class ScrapeRequest(BaseModel):
    query: str

class ScrapeResponse(BaseModel):
    success: bool
    leads_added: int
    high_priority: int

class LeadResponse(BaseModel):
    id: int
    name: str
    category: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    website: Optional[str]
    has_website: bool
    source: str
    query: str
    created_at: datetime

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to Jarvis Lead Finder API"}

@app.post("/scrape-leads", response_model=ScrapeResponse)
async def scrape_leads(request: ScrapeRequest, db=Depends(get_db)):
    """
    Scrape business leads from Google Maps based on the provided query
    """
    logger.info(f"Received scrape request for query: {request.query}")
    
    try:
        # Initialize the scraper and run it
        scraper = GoogleMapsScraper()
        leads = scraper.scrape(request.query)
        
        # Count total leads and high priority leads (no website)
        total_leads = len(leads)
        high_priority = sum(1 for lead in leads if not lead.get('has_website', False))
        
        # Store leads in the database
        with db:
            for lead_data in leads:
                lead = Lead(
                    name=lead_data.get('name', 'N/A'),
                    category=lead_data.get('category'),
                    address=lead_data.get('address'),
                    phone=lead_data.get('phone'),
                    website=lead_data.get('website'),
                    has_website=lead_data.get('has_website', False),
                    source="google_maps",
                    query=request.query,
                    created_at=datetime.now()
                )
                db.add(lead)
            db.commit()
        
        logger.info(f"Successfully added {total_leads} leads, {high_priority} high priority")
        
        return ScrapeResponse(
            success=True,
            leads_added=total_leads,
            high_priority=high_priority
        )
    
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

@app.get("/leads", response_model=List[LeadResponse])
async def get_leads(high_priority_only: bool = False, db=Depends(get_db)):
    """
    Get all leads from the database, with optional filtering for high priority leads
    """
    try:
        with db:
            if high_priority_only:
                leads = db.query(Lead).filter(Lead.has_website == False).all()
            else:
                leads = db.query(Lead).all()
        
        return leads
    
    except Exception as e:
        logger.error(f"Error fetching leads: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 