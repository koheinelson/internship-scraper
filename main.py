import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import ssl
import certifi
import time
import pandas as pd
import sqlite3
import random

# Fix SSL Certificate Issue
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

def fetch_jobs_selenium(query="Software Engineer Intern", location="Remote"):
    url = f"https://www.indeed.com/jobs?q={query.replace(' ', '+')}&l={location.replace(' ', '+')}"
    
    # Start undetected Chrome browser
    driver = uc.Chrome(headless=False)  # Set to False for debugging, True for silent scraping
    driver.get(url)
    
    time.sleep(5)  # Allow time for Cloudflare to pass
    
    # Debug: Save page to check if Indeed loads
    with open("indeed_debug.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Saved Indeed page source to 'indeed_debug.html'. Open it to check what Indeed returned.")
    
    # Simulate human behavior to avoid bot detection
    actions = ActionChains(driver)
    actions.move_by_offset(5, 5).perform()
    time.sleep(random.uniform(1, 3))
    
    for _ in range(5):  # Scroll down incrementally to load more results
        driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(random.uniform(1, 3))
    
    # Wait for job listings to appear
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//a[@role="link"]'))
        )
    except:
        print("Timeout: No job listings found.")
        driver.quit()
        return []
    
    job_cards = driver.find_elements(By.XPATH, '//a[@role="link"]')
    print(f"Found {len(job_cards)} job elements.")
    
    # Debug: Print the first few job elements
    for job in job_cards[:5]:
        print("Job Element HTML:", job.get_attribute("outerHTML"))
    
    jobs = []
    for job in job_cards:
        try:
            title = job.find_element(By.CLASS_NAME, "jobTitle").text
            company = job.find_element(By.CLASS_NAME, "companyName").text
            location = job.find_element(By.CLASS_NAME, "companyLocation").text
            link = job.get_attribute("href")
            
            print(f"Extracted Job: {title} at {company} in {location}, Link: {link}")
            
            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "link": link
            })
        except Exception as e:
            print("Error extracting job details:", e)
    
    driver.quit()
    print(f"Scraping complete! Found {len(jobs)} jobs.")
    return jobs

def save_to_database(jobs, db_name="internships.db"):
    conn = sqlite3.connect(db_name)
    df = pd.DataFrame(jobs)
    df.to_sql("internships", conn, if_exists="replace", index=False)
    conn.close()
    print(f"Saved {len(jobs)} jobs to the database")

if __name__ == "__main__":
    jobs = fetch_jobs_selenium()
    if jobs:
        save_to_database(jobs)



