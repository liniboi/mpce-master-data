import os
import json
import urllib.parse
import requests
from bs4 import BeautifulSoup

GITHUB_USERNAME = "liniboi"
REPO_NAME = "mpce-master-data"
BRANCH = "main"
BASE_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/{BRANCH}/"

def scrape_mcpedl_metadata(url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1').text.strip() if soup.find('h1') else None
        if not title:
            return None
        
        paragraphs = soup.find_all('p')
        description = ""
        for p in paragraphs[:3]:
            text = p.text.strip()
            if len(text) > 30:
                description = text
                break
        if not description:
            description = f"Custom package for {title}."

        img_tag = soup.find('meta', property='og:image')
        image_url = img_tag['content'] if img_tag else "https://media.forgecdn.net/attachments/1610/159/1775109525257-png.png"

        return {"title": title, "description": description, "imageUrl": image_url}
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def run_cloud_automation():
    if not os.path.exists("links.txt"):
        print("links.txt missing.")
        return

    with open("links.txt", "r") as f:
        target_pages = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    addons_list = []
    local_files = [f for f in os.listdir(".") if f.endswith('.mcpack')]
    
    print(f"DEBUG: Found {len(local_files)} .mcpack files in directory.")

    for page_url in target_pages:
        data = scrape_mcpedl_metadata(page_url)
        if not data:
            continue
            
        title = data["title"]
        # Generate both possible filenames
        name_with_spaces = f"{title}.mcpack"
        name_with_underscores = f"{title.replace(' ', '_')}.mcpack"
        
        actual_name = None
        
        # Check which version exists in the folder
        if os.path.exists(name_with_spaces):
            actual_name = name_with_spaces
        elif os.path.exists(name_with_underscores):
            actual_name = name_with_underscores
            
        if actual_name:
            encoded_filename = urllib.parse.quote(actual_name)
            addon_entry = {
                "title": title,
                "description": data["description"],
                "imageUrl": data["imageUrl"],
                "downloadUrl": f"{BASE_RAW_URL}{encoded_filename}"
            }
            addons_list.append(addon_entry)
            print(f"Verified: {title} (Matched: {actual_name})")
        else:
            print(f"[-] Missing: '{title}' | Checked for: '{name_with_spaces}' and '{name_with_underscores}'")

    if addons_list:
        with open("addons.json", "w", encoding="utf-8") as json_file:
            json.dump(addons_list, json_file, indent=4, ensure_ascii=False)
        print("addons.json updated.")
    else:
        print("No addons were verified. addons.json not updated.")

if __name__ == "__main__":
    run_cloud_automation()
