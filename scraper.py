import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import logging
import random

# Set up logging
logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Target URL
TARGET_URL = "https://fpcitywide25-myexperience.personatech.com/selection/a50d6c24-545b-4327-a8b2-e9607e621db9"
LOGIN_URL = "https://fpcitywide25-myexperience.personatech.com/login"  # Adjust if the login URL differs

# Credentials
USERNAME = "lukezhu@umich.edu"
PASSWORD = "108897229"

# Function to scrape static content using requests
def scrape_static(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        scraped_data = []

        event_title = soup.find('h1') or soup.find('h2')
        event_title = event_title.get_text(strip=True) if event_title else "N/A"

        details = soup.find_all('div', class_='event-details')
        for detail in details:
            title = detail.find('h3')
            description = detail.find('p')
            scraped_data.append({
                'Event Title': event_title,
                'Detail Title': title.get_text(strip=True) if title else "N/A",
                'Description': description.get_text(strip=True) if description else "N/A"
            })

        if not scraped_data:
            paragraphs = soup.find_all('p')
            for i, p in enumerate(paragraphs):
                scraped_data.append({
                    'Event Title': event_title,
                    'Detail Title': f"Paragraph {i+1}",
                    'Description': p.get_text(strip=True)
                })

        logging.info(f"Successfully scraped static content from {url}")
        return scraped_data

    except requests.RequestException as e:
        logging.error(f"Error during static scraping: {e}")
        return []

# Function to scrape dynamic content using Selenium with login
def scrape_dynamic(url):
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        options.add_argument('--disable-blink-features=AutomationControlled')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Navigate to login page
        driver.get(LOGIN_URL)
        time.sleep(2)

        # Fill in login form
        driver.find_element("id", "username").send_keys(USERNAME)
        driver.find_element("id", "password").send_keys(PASSWORD)
        driver.find_element("css selector", ".btn--primary").click()
        time.sleep(3)

        # Navigate to the target URL
        driver.get(url)
        time.sleep(random.uniform(2, 5))

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        scraped_data = []

        event_title = soup.find('h1') or soup.find('h2')
        event_title = event_title.get_text(strip=True) if event_title else "N/A"

        details = soup.find_all('div', class_='event-details')
        for detail in details:
            title = detail.find('h3')
            description = detail.find('p')
            scraped_data.append({
                'Event Title': event_title,
                'Detail Title': title.get_text(strip=True) if title else "N/A",
                'Description': description.get_text(strip=True) if description else "N/A"
            })

        if not scraped_data:
            paragraphs = soup.find_all('p')
            for i, p in enumerate(paragraphs):
                scraped_data.append({
                    'Event Title': event_title,
                    'Detail Title': f"Paragraph {i+1}",
                    'Description': p.get_text(strip=True)
                })

        logging.info(f"Successfully scraped dynamic content from {url}")
        return scraped_data

    except Exception as e:
        logging.error(f"Error during dynamic scraping: {e}")
        return []

# Main function to run the scraper
def main():
    logging.info(f"Starting scrape for {TARGET_URL}")

    print("Attempting static scrape...")
    scraped_data = scrape_static(TARGET_URL)

    if not scraped_data:
        print("Static scrape failed or no data found. Attempting dynamic scrape...")
        scraped_data = scrape_dynamic(TARGET_URL)

    if scraped_data:
        print("Data scraped successfully!")
        print(scraped_data)

        df = pd.DataFrame(scraped_data)
        df.to_csv('scraped_data.csv', index=False)
        print("Data saved to scraped_data.csv")
        logging.info("Data saved to scraped_data.csv")
    else:
        print("No data retrieved. The site may require authentication or block scraping.")
        logging.warning("No data retrieved from the site.")

if __name__ == "__main__":
    main()
