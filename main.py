import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import ssl
import certifi
import time
import pandas as pd
import sqlite3
import random
import os

# Fix SSL Certificate Issue
ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

def fetch_jobs_selenium(location="Remote", min_results=30):
    url = f"https://www.indeed.com/jobs?q=Software+Engineer+Internship&l={location.replace(' ', '+')}"
    
    driver = uc.Chrome(headless=False)  # Set to False for debugging, True for silent scraping
    driver.get(url)
    
    all_jobs = []
    page = 0
    
    while len(all_jobs) < min_results:
        time.sleep(5)  # Allow time for page load and Cloudflare checks
        
        # Debug: Save page to check if Indeed loads
        with open(f"indeed_debug_{page}.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f"Saved Indeed page source to 'indeed_debug_{page}.html'.")
        
        jobs = fetch_jobs_from_html(f"indeed_debug_{page}.html")
        all_jobs.extend(jobs)
        
        if len(all_jobs) >= min_results:
            break
        
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "a[aria-label='Next']")
            next_button.click()
            time.sleep(5)  # Allow time for new page load
        except Exception:
            print("No more pages found.")
            break
        
        page += 1
    
    driver.quit()
    return all_jobs

def fetch_jobs_from_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, "html.parser")
    
    job_cards = soup.find_all("div", class_="job_seen_beacon")
    if not job_cards:
        job_cards = soup.find_all("td", class_="resultContent")
    
    print(f"Found {len(job_cards)} job elements in the HTML file.")
    
    jobs = []
    for job in job_cards:
        try:
            title_elem = job.find("h2", class_="jobTitle")
            company_elem = job.find("span", attrs={"data-testid": "company-name"})
            location_elem = job.find("div", attrs={"data-testid": "text-location"})
            pay_elem = job.find("div", attrs={"data-testid": "attribute_snippet_testid"})
            
            title = title_elem.text.strip() if title_elem else "Unknown Title"
            company = company_elem.text.strip() if company_elem else "Unknown Company"
            location = location_elem.text.strip() if location_elem else "Unknown Location"
            pay = pay_elem.text.strip() if pay_elem else "Not Provided"

            link_elem = job.find("a", href=True)
            link = "https://www.indeed.com" + link_elem["href"] if link_elem else "#"

            jobs.append({
                "company": company,
                "title": title,
                "location": location,
                "pay": pay,
                "link": link
            })
        except Exception as e:
            print("Error extracting job details:", e)
    
    print(f"Extraction complete! Found {len(jobs)} software engineering internship jobs.")
    return jobs

def save_to_database(jobs, db_name="internships.db"):
    conn = sqlite3.connect(db_name)
    df = pd.DataFrame(jobs)
    df.to_sql("internships", conn, if_exists="replace", index=False)
    conn.close()
    print(f"Saved {len(jobs)} internships to the database")

def save_to_csv(jobs, filename="internships.csv"):
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop", filename)
    df = pd.DataFrame(jobs)
    df.to_csv(desktop_path, index=False)
    print(f"Saved internships to {desktop_path}")

if __name__ == "__main__":
    jobs = fetch_jobs_selenium()  # Fetch multiple pages until we have 30 results
    if jobs:
        save_to_database(jobs)
        save_to_csv(jobs)
