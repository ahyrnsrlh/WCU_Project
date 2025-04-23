from usecases.scraper import scrape_articles_with_login
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()
    
    START_PAGE = 2503
    END_PAGE = 3336  
    # Get credentials from environment variables
    EMAIL = os.getenv("SINTA_EMAIL")
    PASSWORD = os.getenv("SINTA_PASSWORD")
    
    if not EMAIL or not PASSWORD:
        print("Error: Email or password not found in .env file")
        exit(1)

    scrape_articles_with_login(START_PAGE, END_PAGE, EMAIL, PASSWORD)
