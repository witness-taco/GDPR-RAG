import requests
import re
import time
import pandas as pd

def update_gdpr_fines():
    # Spoof a normal web browser
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    print("1. Infiltrating main page to extract the current JSON endpoint...")
    response = requests.get("https://enforcementtracker.com/", headers=headers)
    
    # Regex to hunt for the hidden data file in the JavaScript source code
    match = re.search(r"ajax:\s*'(data[a-zA-Z0-9_]+\.json)'", response.text)
    
    if not match:
        print("Mission Failed: Could not find the JSON endpoint.")
        return
        
    json_filename = match.group(1)
    
    # Generate our own fresh timestamp for the cache-buster
    timestamp = int(time.time() * 1000)
    
    # Build the full URL
    json_url = f"https://enforcementtracker.com/{json_filename}?_={timestamp}"
    print(f"2. Target Acquired: {json_url}")
    
    print("3. Downloading the complete GDPR database...")
    json_response = requests.get(json_url, headers=headers).json()
    
    # DataTables stores the rows inside a dictionary key called "data"
    fines_data = json_response.get("data", [])
    
    # Convert the JSON array into a Pandas DataFrame
    df = pd.DataFrame(fines_data)
    
    # Save it to a clean CSV for the OpenWebUI Knowledge Base
    filename = "latest_cms_fines.csv"
    df.to_csv(filename, index=False)
    
    print(f"4. Success! {len(df)} fines successfully saved to {filename}")

if __name__ == "__main__":
    update_gdpr_fines()
