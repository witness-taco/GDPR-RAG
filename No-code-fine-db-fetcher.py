# pip install playwright pandas
# playwright install
from playwright.sync_api import sync_playwright
import pandas as pd
import time

def scrape_fines():
    data_vault = []

    with sync_playwright() as p:
        # Launch Chromium (headless=False so you can watch it work)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.enforcementtracker.com/")
        
        # Wait for the main table to load
        page.wait_for_selector("table#finesTable") # Adjust ID if CMS changed it
        
        # Optional: Change the dropdown to "Show 100 entries" to speed up the loop
        page.select_option('select[name="finesTable_length"]', value='100')
        time.sleep(2)

        while True:
            # 1. Locate all the green '+' buttons on the current page
            # DataTables uses 'details-control' or 'dt-control' for these icons
            expand_buttons = page.locator("td.details-control")
            
            # 2. Click them all to reveal the summaries
            for i in range(expand_buttons.count()):
                button = expand_buttons.nth(i)
                # Only click if it's currently green (not yet expanded)
                if "shown" not in button.evaluate("node => node.parentElement.className"):
                    button.click()
                    time.sleep(0.1) # Be gentle to the DOM

            # 3. Scrape the revealed data
            # In DataTables, the expanded summary is usually in the immediate next row (tr.child)
            rows = page.locator("table#finesTable > tbody > tr[role='row']").all()
            
            for row in rows:
                # Extract basic visible columns (Country, Fine, Authority, etc.)
                cols = row.locator("td").all_inner_texts()
                
                # The summary is hidden in the 'child' row directly beneath this one
                summary_row = row.evaluate("node => node.nextElementSibling ? node.nextElementSibling.innerText : 'No Summary'")
                
                if len(cols) > 2:
                    data_vault.append({
                        "Country": cols[1],
                        "Date": cols[2],
                        "Fine": cols[3],
                        "Controller": cols[4],
                        "Article": cols[5],
                        "Type": cols[6],
                        "Summary": summary_row.replace('\n', ' ').strip() # Clean the text
                    })

            # 4. Navigate to the next page
            next_btn = page.locator("a.paginate_button.next")
            
            # If the next button is disabled, we've reached the end
            if "disabled" in next_btn.get_attribute("class"):
                print("Scraping Complete!")
                break
                
            next_btn.click()
            time.sleep(2) # Wait for the new page to load

        browser.close()
        
    # Export the arsenal to CSV
    df = pd.DataFrame(data_vault)
    df.to_csv("cms_fines_complete_arsenal.csv", index=False)
    print(f"Saved {len(df)} fines to CSV.")

if __name__ == "__main__":
    scrape_fines()
