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

# Set up logging
logging.basicConfig(level=logging.INFO)
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
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920,1080")
        
        # Add a user agent to avoid detection
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")
        
        # Initialize driver to None (will be set in scrape method)
        self.driver = None
    
    def _setup_driver(self):
        """
        Set up the Chrome WebDriver with configured options
        """
        try:
            # Use webdriver_manager to handle driver installation
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=self.options)
            logger.info("WebDriver initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error setting up WebDriver: {str(e)}")
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
        Extract business listings from the current page
        """
        try:
            # Get the page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find all business listings
            listings = soup.find_all('div', class_=lambda c: c and 'hfpxzc' in c)
            
            business_data = []
            
            # If we can't find listings with the expected class, try an alternate approach
            if not listings:
                logger.info("Using alternate method to find listings")
                # Alternative: find the feed container and get all direct children
                feed = soup.find('div', attrs={'role': 'feed'})
                if feed:
                    listings = feed.find_all('div', recursive=False)
            
            # Process each listing
            for listing in listings:
                # Try to click on each listing to view details
                try:
                    # Find the listing element in Selenium
                    listing_element = self.driver.find_element(By.XPATH, f"//a[contains(@href, '/maps/place/')]")
                    listing_element.click()
                    
                    # Wait for details panel to load
                    self._random_delay(2, 4)
                    
                    # Extract business information
                    business_info = self._extract_business_info()
                    if business_info:
                        business_data.append(business_info)
                
                except (NoSuchElementException, TimeoutException):
                    logger.warning("Could not click on a listing or extract its information")
                    continue
                except Exception as e:
                    logger.error(f"Error processing listing: {str(e)}")
                    continue
            
            logger.info(f"Extracted {len(business_data)} business listings")
            return business_data
        
        except Exception as e:
            logger.error(f"Error extracting business listings: {str(e)}")
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
        
        Args:
            query (str): The search query (e.g., "plumbers in Manchester")
            max_results (int): Maximum number of results to scrape
            
        Returns:
            list: List of dictionaries containing business information
        """
        try:
            # Set up the WebDriver
            if not self._setup_driver():
                return []
            
            logger.info(f"Starting scrape for query: {query}")
            
            # Search for the query
            if not self._search_query(query):
                return []
            
            # Scroll to load more results
            self._scroll_results(num_scrolls=3)
            
            # Extract business listings
            business_data = self._extract_business_listings()
            
            # Limit results if needed
            if len(business_data) > max_results:
                business_data = business_data[:max_results]
            
            logger.info(f"Scraping completed, found {len(business_data)} businesses")
            
            return business_data
            
        except Exception as e:
            logger.error(f"Error in scraping process: {str(e)}")
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