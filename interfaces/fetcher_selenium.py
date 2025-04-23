from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from entities.article import Article

def login_to_sinta(driver, email, password):
    driver.get("https://sinta.kemdikbud.go.id/logins")

    try:
        # Tunggu sampai elemen username muncul
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        # Isi input username dan password
        username_input = driver.find_element(By.NAME, "username")
        password_input = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.XPATH, "//button[@type='submit' and contains(text(), 'Login')]")

        username_input.clear()
        username_input.send_keys(email)

        password_input.clear()
        password_input.send_keys(password)

        login_button.click()

        # Tunggu hingga redirect berhasil (asumsi ke dashboard atau halaman affiliation)
        WebDriverWait(driver, 10).until_not(EC.url_contains("login"))

        print("Login berhasil!")

    except Exception as e:
        print("Gagal login:", e)
        with open("login_debug.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

def fetch_articles_from_page(page_number, driver):
    """
    Fetches articles from a specific page in SINTA
    
    Args:
        page_number: The page number to fetch articles from
        driver: Selenium webdriver instance
        
    Returns:
        List of Article objects
    """
    # Navigate to the articles page with the given page number
    url = f"https://sinta.kemdikbud.go.id/journals/detail?page={page_number}&id=1&view=documents"
    driver.get(url)
    
    # Wait for the articles to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.kr-journal-detail-items"))
    )
    
    # Find all article items
    article_items = driver.find_elements(By.CSS_SELECTOR, "div.kr-journal-detail-items > div.item")
    
    articles = []
    for item in article_items:
        try:
            # Extract article details
            title_element = item.find_element(By.CSS_SELECTOR, "a.title-article")
            title = title_element.text.strip()
            link = title_element.get_attribute("href")
            
            # Extract authors if available
            try:
                authors_element = item.find_element(By.CSS_SELECTOR, "div.authors")
                authors = authors_element.text.strip()
            except:
                authors = ""
            
            # Extract year and citation count
            try:
                year_element = item.find_element(By.CSS_SELECTOR, "span.year")
                year = year_element.text.strip()
            except:
                year = ""
                
            try:
                cited_element = item.find_element(By.CSS_SELECTOR, "div.stats > div:nth-child(1)")
                cited = cited_element.text.strip().replace("Cited by: ", "")
            except:
                cited = "0"
            
            # Create and add Article object
            article = Article(title, link, authors, year, cited)
            articles.append(article)
            
        except Exception as e:
            print(f"Error parsing article: {e}")
    
    return articles
