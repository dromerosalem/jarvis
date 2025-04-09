# Jarvis Lead Finder Backend

This backend service powers the Jarvis Lead Finder module, which helps digital agencies discover local businesses with weak or non-existent online presence.

## What It Does

- Accepts search queries like "plumbers in Manchester"
- Scrapes Google Maps business listings using Selenium and BeautifulSoup
- Identifies businesses without websites
- Stores the results in a SQLite database
- Provides REST API endpoints to initiate scraping and retrieve leads

## Technology Stack

- **Framework**: FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **Web Scraping**: Selenium with Chrome WebDriver
- **HTML Parsing**: BeautifulSoup4
- **Web Driver Management**: webdriver-manager

## Installation

1. Make sure you have Python 3.8+ installed
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Setup

The application will automatically:
- Set up the database tables on first run
- Install and configure ChromeDriver through webdriver-manager

## Running the Service

Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Endpoints

- **POST /scrape-leads**: Start a scraping job
  - Request body: `{"query": "plumbers in Manchester"}`
  - Response: `{"success": true, "leads_added": 25, "high_priority": 10}`

- **GET /leads**: Get all leads
  - Optional query param: `high_priority_only=true` to filter for businesses without websites
  - Returns a list of leads with all details

## Customization

- Edit `app/scraper/scraper.py` to modify scraping behavior
- Edit `app/database/database.py` to change database schema or connection

## Limitations

- For demonstration purposes only
- Operates within Google's terms of service
- Includes delays to avoid rate limits
- Should not be used for high-volume scraping 