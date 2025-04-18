from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import random
import logging
import re
import platform
import os
import stat
import shutil

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # Change to DEBUG level
logger = logging.getLogger(__name__)

class GoogleMapsScraper:
    """
    Scraper for Google Maps business listings
    
    This class handles:
    - Setting up a headless Chrome browser
    - Searching for businesses based on query
    - Scrolling through results
    - Extracting business details
    - Identifying businesses without websites
    """
    
    def __init__(self):
        """
        Initialize the scraper with Chrome WebDriver
        """
        # Set up Chrome options for headless mode
        self.options = Options()
        # self.options.add_argument("--headless")  # Comment out headless mode for debugging
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920,1080")
        
        # Add a user agent to avoid detection
        self.options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
        
        # Initialize driver to None (will be set in scrape method)
        self.driver = None
    
    def _setup_driver(self):
        """
        Set up the Chrome WebDriver with configured options
        """
        try:
            # Set up ChromeDriver path
            driver_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chromedriver")
            driver_path = os.path.join(driver_dir, "chromedriver")
            
            if not os.path.exists(driver_path):
                logger.error(f"ChromeDriver not found at {driver_path}. Please run /debug/chrome-version endpoint first to set it up.")
                return False
            
            # Make sure the driver is executable
            os.chmod(driver_path, stat.S_IRWXU)
            
            # Initialize ChromeDriver with explicit path
            service = Service(executable_path=driver_path)
            self.driver = webdriver.Chrome(service=service, options=self.options)
            
            logger.info("WebDriver initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error setting up WebDriver: {str(e)}", exc_info=True)
            return False
    
    def _random_delay(self, min_seconds=3, max_seconds=7):
        """
        Add a random delay to avoid bot detection
        """
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def _search_query(self, query):
        """
        Open Google Maps and search for the query
        """
        try:
            # Navigate to Google Maps
            self.driver.get("https://www.google.com/maps")
            logger.info("Navigated to Google Maps")
            
            # Wait for the search box to be available
            self._random_delay(2, 4)
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "searchboxinput"))
            )
            
            # Clear any existing text and enter the search query
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.ENTER)
            
            # Wait for results to load
            self._random_delay()
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
            )
            
            logger.info(f"Successfully searched for: {query}")
            return True
        
        except TimeoutException:
            logger.error("Timeout waiting for search results")
            return False
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            return False
    
    def _scroll_results(self, num_scrolls=5):
        """
        Scroll through the results list to load more businesses
        """
        try:
            # Find the results container
            results_div = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
            )
            
            # Scroll multiple times with random delays
            for i in range(num_scrolls):
                logger.info(f"Scrolling results (scroll {i+1}/{num_scrolls})")
                
                # Execute JavaScript to scroll down
                self.driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight", 
                    results_div
                )
                
                # Add a random delay between scrolls
                self._random_delay(2, 5)
            
            return True
        
        except Exception as e:
            logger.error(f"Error scrolling results: {str(e)}")
            return False
    
    def _extract_business_listings(self):
        """
        Extract business listings from the loaded Google Maps page
        """
        try:
            logger.debug("Starting business listings extraction...")
            
            # Wait for listings to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='article']"))
            )
            
            # Get the page source and create BeautifulSoup object
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find all business listings
            listings = soup.find_all("div", {"role": "article"})
            logger.debug(f"Found {len(listings)} raw business listings in HTML")
            
            business_data = []
            for listing in listings:
                try:
                    # Extract business name
                    name_element = listing.find("h3", recursive=True)
                    if not name_element:
                        logger.debug("Skipping listing - no business name found")
                        continue
                    name = name_element.get_text(strip=True)
                    
                    # Extract address
                    address_element = listing.find("div", {"role": "link"})
                    address = address_element.get_text(strip=True) if address_element else "N/A"
                    
                    # Extract rating and reviews
                    rating_element = listing.find("span", {"role": "img"})
                    rating = rating_element.get("aria-label", "N/A") if rating_element else "N/A"
                    
                    reviews_element = listing.find("div", string=lambda text: text and "reviews" in text.lower())
                    reviews = reviews_element.get_text(strip=True) if reviews_element else "N/A"
                    
                    business_info = {
                        "name": name,
                        "address": address,
                        "rating": rating,
                        "reviews": reviews
                    }
                    
                    logger.debug(f"Extracted business info: {business_info}")
                    business_data.append(business_info)
                    
                except Exception as e:
                    logger.error(f"Error extracting data from listing: {str(e)}")
                    continue
            
            logger.info(f"Successfully extracted {len(business_data)} business listings")
            return business_data
            
        except Exception as e:
            logger.error(f"Error in _extract_business_listings: {str(e)}", exc_info=True)
            return []
    
    def _extract_business_info(self):
        """
        Extract business information from the details panel
        """
        try:
            # Wait for the details panel to fully load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.fontHeadlineSmall"))
            )
            
            # Get the current page source for the details panel
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract business name
            name_element = soup.find('h1', class_=lambda c: c and 'fontHeadlineLarge' in c)
            name = name_element.text.strip() if name_element else "N/A"
            
            # Extract category
            category_element = soup.find('button', class_=lambda c: c and 'hH0iDf' in c)
            category = category_element.text.strip() if category_element else None
            
            # Extract rating and reviews
            rating_element = soup.find('div', class_=lambda c: c and 'fontBodyMedium' in c and 'f5' in c)
            rating = None
            reviews = None
            if rating_element:
                rating_text = rating_element.text.strip()
                rating_match = re.search(r'([\d.]+)', rating_text)
                reviews_match = re.search(r'(\d+) reviews', rating_text)
                
                if rating_match:
                    rating = rating_match.group(1)
                if reviews_match:
                    reviews = reviews_match.group(1)
            
            # Extract address
            address = None
            address_elements = soup.find_all('button', attrs={'data-item-id': 'address'})
            if address_elements:
                address = address_elements[0].text.strip()
            
            # Extract phone number
            phone = None
            phone_elements = soup.find_all('button', attrs={'data-item-id': 'phone'})
            if phone_elements:
                phone = phone_elements[0].text.strip()
            
            # Extract website URL
            website = None
            website_elements = soup.find_all('a', attrs={'data-item-id': 'authority'})
            if website_elements:
                website = website_elements[0].get('href')
            
            # Determine if business has a website
            has_website = website is not None and website.strip() != ""
            
            # Create business data dictionary
            business_data = {
                'name': name,
                'category': category,
                'rating': rating,
                'reviews': reviews,
                'address': address,
                'phone': phone,
                'website': website,
                'has_website': has_website
            }
            
            logger.info(f"Extracted business info for: {name}")
            return business_data
        
        except TimeoutException:
            logger.warning("Timeout waiting for business details")
            return None
        except Exception as e:
            logger.error(f"Error extracting business info: {str(e)}")
            return None
    
    def scrape(self, query, max_results=20):
        """
        Main method to scrape Google Maps for business listings
        """
        try:
            logger.debug("Starting scraping process...")
            
            # Set up the WebDriver
            if not self._setup_driver():
                logger.error("Failed to set up WebDriver")
                return []
            
            logger.info(f"Starting scrape for query: {query}")
            
            # Search for the query
            if not self._search_query(query):
                logger.error("Failed to execute search query")
                return []
            
            logger.debug("Search query executed successfully")
            
            # Scroll to load more results
            if not self._scroll_results(num_scrolls=3):
                logger.error("Failed to scroll results")
                return []
            
            logger.debug("Scrolling completed successfully")
            
            # Extract business listings
            business_data = self._extract_business_listings()
            
            logger.debug(f"Raw business data extracted: {len(business_data)} listings")
            
            # Limit results if needed
            if len(business_data) > max_results:
                business_data = business_data[:max_results]
                logger.debug(f"Limited results to {max_results} listings")
            
            logger.info(f"Scraping completed, found {len(business_data)} businesses")
            
            return business_data
            
        except Exception as e:
            logger.error(f"Error in scraping process: {str(e)}", exc_info=True)
            return []
            
        finally:
            # Always close the WebDriver
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver closed")


# For testing purposes
if __name__ == "__main__":
    scraper = GoogleMapsScraper()
    results = scraper.scrape("plumbers in Manchester", max_results=5)
    print(f"Found {len(results)} results")
    for result in results:
        print(f"Name: {result['name']}")
        print(f"Has Website: {result['has_website']}")
        print("---") 