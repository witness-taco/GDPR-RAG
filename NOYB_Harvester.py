# pip install requests beautifulsoup4 pandas
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def reap_noyb_cases():
    base_url = "https://noyb.eu"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    # --- STEP 1: The Crawler (Get all Case URLs) ---
    print("Step 1: Harvesting case URLs...")
    case_urls = []
    
    # We loop through the Drupal pagination (?page=0, ?page=1, etc.)
    page = 0
    while True:
        url = f"{base_url}/en/project/cases?page={page}"
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the table rows
        rows = soup.select("table.views-table tbody tr")
        
        if not rows:
            break # No more rows found, we reached the end
            
        for row in rows:
            # Find the link inside the first column (e.g., "C001")
            link_tag = row.select_section("td.views-field-noyb-case-number a")
            if link_tag:
                href = link_tag.get('href')
                case_urls.append(base_url + href)
                
        print(f"Scraped page {page}. Total URLs found: {len(case_urls)}")
        page += 1
        time.sleep(1) # Be polite to their server

    # --- STEP 2: The Harvester (Scrape individual pages) ---
    print(f"\nStep 2: Extracting data from {len(case_urls)} cases...")
    master_database = []

    for index, case_url in enumerate(case_urls):
        print(f"Processing {index+1}/{len(case_urls)}: {case_url}")
        response = requests.get(case_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        case_data = {
            "URL": case_url,
            "Case_ID": "",
            "Controller": "",
            "DPA": "",
            "Status": "",
            "Summary": "",
            "Protocol": ""
        }
        
        # Extract the Header Info (Usually in a sidebar or specific div classes)
        # Note: You will need to inspect the NOYB HTML to get the exact class names
        title_tag = soup.find("h1", class_="page-title")
        if title_tag:
            case_data["Case_ID"] = title_tag.text.strip()
            
        summary_tag = soup.find("div", class_="field--name-body")
        if summary_tag:
            case_data["Summary"] = summary_tag.text.strip()
            
        # Extract the Protocol Table
        protocol_table = soup.find("table")
        if protocol_table:
            protocol_text = []
            for tr in protocol_table.find_all("tr")[1:]: # Skip header
                cols = tr.find_all("td")
                if len(cols) >= 2:
                    date = cols[0].text.strip()
                    event = cols[1].text.strip()
                    protocol_text.append(f"[{date}] {event}")
            case_data["Protocol"] = " | ".join(protocol_text)
            
        master_database.append(case_data)
        time.sleep(1) # Crucial: Don't overload the NGO's server
        
    # --- STEP 3: Export to Knowledge Base ---
    df = pd.DataFrame(master_database)
    df.to_csv("noyb_case_arsenal.csv", index=False)
    print("Mission Accomplished. NOYB data saved!")

if __name__ == "__main__":
    reap_noyb_cases()
