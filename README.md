# Jarvis Lead Finder

A full-stack automation module for Jarvis that helps digital agencies find and convert local businesses with weak or non-existent online presence. The system scrapes Google Maps listings and identifies high-priority leads (businesses without websites).

## Project Structure

This project consists of two main parts:

- **Backend**: Python FastAPI application that handles web scraping and database storage
- **Frontend**: Next.js application that provides a user interface for finding and reviewing leads

## Features

- Search for businesses by query (e.g., "plumbers in Manchester")
- Automatically scrape Google Maps for business information
- Identify businesses without websites as high-priority leads
- Store all leads in a SQLite database
- Filter and browse leads through a clean web interface

## Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: SQLite with SQLAlchemy ORM
- **Web Scraping**: Selenium with Chrome WebDriver
- **HTML Parsing**: BeautifulSoup4
- **Web Driver Management**: webdriver-manager

### Frontend
- **Framework**: Next.js (React)
- **Styling**: Tailwind CSS
- **Data Fetching**: Axios and React Query
- **State Management**: React Hooks

## Getting Started

### Prerequisites

- Python 3.8+ for the backend
- Node.js 14+ for the frontend
- Chrome browser installed (for the web scraping component)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

3. Run the development server:
```bash
npm run dev
# or
yarn dev
```

The web application will be available at http://localhost:3000

## API Endpoints

- **POST /scrape-leads**: Start a scraping job
  - Request body: `{"query": "plumbers in Manchester"}`
  - Response: `{"success": true, "leads_added": 25, "high_priority": 10}`

- **GET /leads**: Get all leads
  - Optional query param: `high_priority_only=true` to filter for businesses without websites
  - Returns a list of leads with all details

## Deployment

### Backend Deployment

The backend can be deployed to services like:
- Railway
- Render
- Heroku

Make sure to set proper environment variables for production deployment.

### Frontend Deployment

The frontend is optimized for deployment on Vercel:
1. Push your code to a GitHub repository
2. Connect the repository to Vercel
3. Set the environment variables in the Vercel dashboard

For proper connection, set the `API_URL` environment variable to your deployed backend URL.

## Limitations and Responsible Use

- This tool is designed for demonstration purposes
- Use responsibly and in accordance with Google's terms of service
- The scraper includes delays to avoid rate limits
- Not intended for high-volume scraping
- No proxies or API keys are required, but consider adding them for production use

## License

This project is licensed under the MIT License - see the LICENSE file for details

## Acknowledgments

- Built for the Jarvis platform
- Designed to help digital agencies find clients who need websites
- Created as a modular component that can be extended with additional features 