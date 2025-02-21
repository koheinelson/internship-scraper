import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3

def fetch_indeed_jobs(query="Software Engineer Intern", location="Remote"):
    base_url = "https://www.indeed.com/jobs"
    params = {"q": query, "l": location}
    headers = {"User-Agent": "Mozilla/5.0"}  # Prevent bot detection

    response = requests.get(base_url, params=params, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch data")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    job_cards = soup.find_all("div", class_="job_seen_beacon")
    
    jobs = []
    for job in job_cards:
        title_tag = job.find("h2", class_="jobTitle")
        company_tag = job.find("span", class_="companyName")
        location_tag = job.find("div", class_="companyLocation")
        link_tag = job.find("a", class_="jcs-JobTitle")
        
        if title_tag and company_tag and location_tag and link_tag:
            job_data = {
                "title": title_tag.text.strip(),
                "company": company_tag.text.strip(),
                "location": location_tag.text.strip(),
                "link": "https://www.indeed.com" + link_tag["href"],
            }
            jobs.append(job_data)
    
    return jobs

def save_to_database(jobs, db_name="internships.db"):
    conn = sqlite3.connect(db_name)
    df = pd.DataFrame(jobs)
    df.to_sql("internships", conn, if_exists="replace", index=False)
    conn.close()
    print(f"Saved {len(jobs)} jobs to the database")

if __name__ == "__main__":
    jobs = fetch_indeed_jobs()
    if jobs:
        save_to_database(jobs)



