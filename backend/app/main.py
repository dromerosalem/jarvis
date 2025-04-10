from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
from datetime import datetime
import traceback
import sys
from selenium import webdriver
import platform
import subprocess
import json
import os
import shutil
import requests
import zipfile
import stat

# Import local modules
from app.scraper.scraper import GoogleMapsScraper
from app.database.database import get_db, Lead, create_tables

# Set up logging with more detailed configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('debug.log')
    ]
)
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

@app.get("/debug/test-scraper")
async def test_scraper():
    """
    Debug endpoint to test the scraper functionality
    """
    try:
        logger.debug("Starting scraper test...")
        scraper = GoogleMapsScraper()
        
        # Test WebDriver setup
        logger.debug("Testing WebDriver setup...")
        setup_success = scraper._setup_driver()
        if not setup_success:
            return {"status": "error", "message": "WebDriver setup failed"}
        
        # Test search
        logger.debug("Testing search functionality...")
        test_query = "test business"
        search_success = scraper._search_query(test_query)
        
        # Get page source for debugging
        page_source = scraper.driver.page_source if scraper.driver else "No driver available"
        
        # Capture any errors
        return {
            "status": "success" if setup_success and search_success else "error",
            "setup_success": setup_success,
            "search_success": search_success,
            "driver_initialized": scraper.driver is not None,
            "page_source_length": len(page_source) if isinstance(page_source, str) else 0
        }
    except Exception as e:
        logger.error(f"Error in test-scraper: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }
    finally:
        if scraper and scraper.driver:
            scraper.driver.quit()

@app.get("/debug/chrome-version")
async def check_chrome_version():
    """
    Debug endpoint to check Chrome and ChromeDriver versions
    """
    try:
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        
        # Get Chrome version first
        try:
            chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
            chrome_version = subprocess.check_output([chrome_path, "--version"]).decode().strip()
            logger.info(f"Chrome version: {chrome_version}")
            # Extract version number (e.g., "134.0.6998.166" from "Google Chrome 134.0.6998.166")
            version = chrome_version.split()[-1]
            major_version = version.split('.')[0]
            logger.info(f"Major version: {major_version}")
        except Exception as e:
            logger.error(f"Error getting Chrome version: {e}")
            version = "134.0.6998.166"  # Use latest version
            major_version = "134"
        
        # Set up Chrome options
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Set up ChromeDriver path
        driver_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chromedriver")
        driver_path = os.path.join(driver_dir, "chromedriver")
        
        # Create directory if it doesn't exist
        os.makedirs(driver_dir, exist_ok=True)
        
        # Download ChromeDriver if it doesn't exist
        if not os.path.exists(driver_path):
            # Use Chrome for Testing download URL for newer versions
            base_url = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing"
            download_url = f"{base_url}/{version}/mac-x64/chromedriver-mac-x64.zip"
            
            logger.info(f"Downloading ChromeDriver from: {download_url}")
            
            try:
                # Download the zip file
                response = requests.get(download_url)
                if response.status_code != 200:
                    # Try with stable version URL
                    stable_url = f"{base_url}/stable/mac-x64/chromedriver-mac-x64.zip"
                    logger.info(f"Trying stable version from: {stable_url}")
                    response = requests.get(stable_url)
                    
                if response.status_code != 200:
                    raise Exception(f"Failed to download ChromeDriver. Status code: {response.status_code}")
                
                # Save the zip file
                zip_path = os.path.join(driver_dir, "chromedriver.zip")
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                
                # Extract the zip file
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # Extract to a temporary directory first
                    temp_dir = os.path.join(driver_dir, "temp")
                    os.makedirs(temp_dir, exist_ok=True)
                    zip_ref.extractall(temp_dir)
                    
                    # Move the chromedriver to the correct location
                    extracted_driver = os.path.join(temp_dir, "chromedriver-mac-x64", "chromedriver")
                    if os.path.exists(extracted_driver):
                        shutil.copy2(extracted_driver, driver_path)
                    else:
                        raise Exception(f"ChromeDriver not found in extracted files at {extracted_driver}")
                
                # Make the chromedriver executable
                os.chmod(driver_path, stat.S_IRWXU)
                
                # Clean up
                os.remove(zip_path)
                shutil.rmtree(temp_dir, ignore_errors=True)
                
            except Exception as e:
                logger.error(f"Error downloading/extracting ChromeDriver: {e}")
                raise
        
        logger.info(f"Using ChromeDriver at: {driver_path}")
        
        # Initialize ChromeDriver
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        # Get versions
        capabilities = driver.capabilities
        driver.quit()
        
        return {
            "status": "success",
            "chrome_version": chrome_version,
            "driver_path": driver_path,
            "capabilities": json.dumps(capabilities, indent=2),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "system": platform.system()
        }
    except Exception as e:
        logger.error(f"Error checking Chrome version: {str(e)}")
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "system": platform.system()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 