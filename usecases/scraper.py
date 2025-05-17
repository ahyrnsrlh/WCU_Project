from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import csv
import os
import re
from entities.article import Article
from interfaces.writer import write_articles_to_csv

def scrape_articles_with_login(start_page, end_page, email, password):
    """
    Scrapes articles from Sinta Unila journal within the specified page range
    
    Args:
        start_page: The first page to scrape
        end_page: The last page to scrape (inclusive)
        email: Email for Sinta login
        password: Password for Sinta login
        
    Returns:
        str: Path to the CSV file containing scraped articles
    """
    # SETUP DRIVER
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(), options=options)
    
    try:
        # Login to Sinta
        if not login(driver, email, password):
            print("Login failed. Exiting.")
            return None
        
        # Track unique articles using a composite key of normalized title and year
        unique_article_keys = set()
        
        # List to store all articles
        all_articles = []
        
        # Define single output filename
        output_filename = f"sinta_articles_{start_page}_to_{end_page}.csv"
        
        # Load existing articles if file exists to avoid duplicates
        if os.path.exists(output_filename):
            print(f"Found existing file {output_filename}, loading to avoid duplicates...")
            existing_articles = load_existing_articles(output_filename)
            
            # Extract keys from existing articles
            for article in existing_articles:
                key = get_article_key(article)
                unique_article_keys.add(key)
                
            all_articles.extend(existing_articles)
            print(f"Loaded {len(existing_articles)} existing articles")
        
        # Loop through the specified page range
        for page_num in range(start_page, end_page + 1):
            print(f"Scraping page {page_num}...")
            
            # Try up to 3 times to scrape the page
            max_retries = 3
            for retry in range(max_retries):
                try:
                    # Check if we need to login again
                    if is_on_homepage(driver):
                        print("Session expired. Logging in again.")
                        if not login(driver, email, password):
                            print("Re-login failed. Exiting.")
                            return None
                    
                    articles = scrape_page(driver, page_num)
                    if articles:
                        # Add only non-duplicate articles
                        unique_articles = []
                        for article in articles:
                            key = get_article_key(article)
                            if key not in unique_article_keys:
                                unique_article_keys.add(key)
                                unique_articles.append(article)
                        
                        if unique_articles:
                            all_articles.extend(unique_articles)
                            print(f"Added {len(unique_articles)} new unique articles (filtered out {len(articles) - len(unique_articles)} duplicates)")
                        else:
                            print(f"No new unique articles found on page {page_num}")
                        
                        break  # Success, exit retry loop
                    else:
                        print(f"No articles found on page {page_num}, retry {retry + 1}/{max_retries}")
                        time.sleep(1)  # Reduced wait time before retry
                
                except Exception as e:
                    print(f"Error on page {page_num}, retry {retry + 1}/{max_retries}: {e}")
                    time.sleep(1)  # Reduced wait time on error
                    
                    # If last retry failed, continue to next page
                    if retry == max_retries - 1:
                        print(f"Failed to scrape page {page_num} after {max_retries} attempts")
            
            # Update the single CSV file with current progress - clear file and write all at once
            write_articles_to_csv(all_articles, output_filename)
            print(f"Progress updated: {len(all_articles)} articles saved to {output_filename}")
            
            # Wait between pages to avoid rate limiting
            time.sleep(0.5)  # Reduced wait time between pages
        
        # Final deduplication pass to ensure no duplicates
        final_articles = deduplicate_articles(all_articles)
        if len(final_articles) < len(all_articles):
            print(f"Final deduplication removed {len(all_articles) - len(final_articles)} duplicate entries")
            write_articles_to_csv(final_articles, output_filename)
        
        print(f"Successfully scraped {len(final_articles)} unique articles from pages {start_page} to {end_page}")
        print(f"All data saved to {output_filename}")
        
        return output_filename
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return None
    
    finally:
        driver.quit()

def normalize_title(title):
    """
    Normalize a title by removing special characters, extra spaces, and lowercase
    
    Args:
        title: The title to normalize
        
    Returns:
        Normalized title
    """
    # Remove special characters and convert to lowercase
    title = re.sub(r'[^\w\s]', '', title.lower())
    # Replace multiple spaces with single space
    title = re.sub(r'\s+', ' ', title)
    return title.strip()

def get_article_key(article):
    """
    Generate a unique key for an article based on normalized title and year
    
    Args:
        article: Article object
        
    Returns:
        A string key
    """
    # Use normalized title and year as a composite key
    norm_title = normalize_title(article.title)
    return f"{norm_title}_{article.year}"

def deduplicate_articles(articles):
    """
    Remove duplicate articles from a list
    
    Args:
        articles: List of Article objects
        
    Returns:
        List of unique Article objects
    """
    unique_keys = {}
    unique_articles = []
    
    for article in articles:
        key = get_article_key(article)
        if key not in unique_keys:
            unique_keys[key] = True
            unique_articles.append(article)
    
    return unique_articles

def load_existing_articles(csv_file):
    """
    Load existing articles from a CSV file
    
    Args:
        csv_file: Path to the CSV file
        
    Returns:
        List of Article objects
    """
    articles = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'Title' in row and 'Link' in row and 'Authors' in row and 'Year' in row and 'Cited' in row:
                    article = Article(
                        row['Title'],
                        row['Link'],
                        row['Authors'],
                        row['Year'],
                        row['Cited']
                    )
                    articles.append(article)
    except Exception as e:
        print(f"Error loading existing articles: {e}")
    
    return articles

def is_on_homepage(driver):
    """
    Check if the driver is currently on the Sinta homepage
    
    Args:
        driver: Selenium webdriver instance
        
    Returns:
        True if on homepage, False otherwise
    """
    current_url = driver.current_url
    return current_url == "https://sinta.kemdikbud.go.id/" or current_url == "https://sinta.kemdikbud.go.id"

def login(driver, email, password):
    """
    Login to Sinta website
    
    Args:
        driver: Selenium webdriver instance
        email: Email for login
        password: Password for login
        
    Returns:
        True if login successful, False otherwise
    """
    try:
        LOGIN_URL = "https://sinta.kemdikbud.go.id/logins"
        driver.get(LOGIN_URL)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        driver.find_element(By.NAME, "username").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        print("Login submitted.")

        # Wait for page to fully load and redirect to complete
        time.sleep(2)  # Reduced wait time after login
        
        # Verify successful login by checking we're not still on login page
        if "login" in driver.current_url:
            print("Login seems to have failed. Still on login page.")
            return False
            
        print("Login successful!")
        return True
        
    except Exception as e:
        print(f"Login error: {e}")
        return False

def scrape_page(driver, page_num):
    """
    Scrape articles from a specific page
    
    Args:
        driver: Selenium webdriver instance
        page_num: Page number to scrape
        
    Returns:
        List of Article objects
    """
    BASE_URL = "https://sinta.kemdikbud.go.id/affiliations/profile/398/?view=googlescholar&page={}"
    page_url = BASE_URL.format(page_num)
    driver.get(page_url)
    print(f"Navigated to: {driver.current_url}")
    
    # Check if we were redirected away from expected page
    if f"page={page_num}" not in driver.current_url:
        print(f"Warning: Redirected away from page {page_num}")
        return []

    # Wait for publication elements to appear
    try:
        WebDriverWait(driver, 8).until(  # Slightly reduced wait time
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.ar-list-item.mb-5"))
        )
    except:
        print("No articles found or page structure changed")
        return []

    soup = BeautifulSoup(driver.page_source, "html.parser")
    items = soup.select("div.ar-list-item.mb-5")
    
    if not items:
        print("No article items found on page")
        return []
    
    articles = []
    for item in items:
        try:
            title_tag = item.select_one("div.ar-title a")
            title = title_tag.text.strip() if title_tag else "No title"
            link = title_tag['href'] if title_tag else "No link"
            authors = item.select_one("div.ar-meta a").text.strip() if item.select_one("div.ar-meta a") else "No authors"
            year_tag = item.select_one("a.ar-year")
            year = year_tag.text.strip() if year_tag else "-"
            cited_tag = item.select_one("a.ar-cited")
            cited = cited_tag.text.strip() if cited_tag else "0 cited"
            
            # Create Article object and add to list
            article = Article(title, link, authors, year, cited)
            articles.append(article)
            
            # Print for debugging (only the title to reduce output)
            print(f"Found article: {title[:50]}...")
        except Exception as e:
            print(f"Error parsing article: {e}")
    
    return articles