import os
import json
import urllib.parse
import requests
from bs4 import BeautifulSoup

# Configuration matched to your exact repository path
GITHUB_USERNAME = "liniboi"
REPO_NAME = "mpce-master-data"
BRANCH = "main"

# The exact base path for retrieving raw file binaries from your main branch
BASE_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/{BRANCH}/"

# Add your target MCPEDL page links here
TARGET_PAGES = [
    "https://mcpedl.com/crop-indicator-addon"  # Example page link
]

def scrape_mcpedl_metadata(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"[-] Could not connect to web page: {url}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1').text.strip() if soup.find('h1') else None
        
        if not title:
            return None

        # Safely scrape structural description text fields
        paragraphs = soup.find_all('p')
        description = ""
        for p in paragraphs[:3]:
            text = p.text.strip()
            if len(text) > 30:
                description = text
                break
        if not description:
            description = f"Custom package for {title}."

        # Scrape meta image layers for app card preview placement
        img_tag = soup.find('meta', property='og:image')
        image_url = img_tag['content'] if img_tag else "https://media.forgecdn.net/attachments/1610/159/1775109525257-png.png"

        return {
            "title": title,
            "description": description,
            "imageUrl": image_url
        }
    except Exception as e:
        print(f"[-] Metadata extraction failed: {e}")
        return None

def run_safe_automation():
    addons_list = []
    current_directory = os.getcwd()
    
    # Read local data directory contents for files ending in .mcpack
    local_files = [f for f in os.listdir(current_directory) if f.endswith('.mcpack')]
    
    print("[+] Executing asset verification flow...")
    
    for page_url in TARGET_PAGES:
        data = scrape_mcpedl_metadata(page_url)
        if not data:
            continue
            
        # Standardize space configurations with underscores for clean directory transfers
        expected_name = data["title"].replace(" ", "_") + ".mcpack"
        file_found = False
        
        if os.path.exists(expected_name):
            file_found = True
        else:
            # Automatic naming fallback detection
            for local_file in local_files:
                if local_file != expected_name:
                    print(f"[!] Rectifying layout name mismatch: '{local_file}' -> '{expected_name}'")
                    try:
                        os.rename(local_file, expected_name)
                        local_files.remove(local_file) 
                        file_found = True
                        break
                    except Exception as e:
                        print(f"[-] Local file update interrupted: {e}")

        # If localized binary is validated, append target block map
        if file_found:
            encoded_filename = urllib.parse.quote(expected_name)
            addon_entry = {
                "title": data["title"],
                "description": data["description"],
                "imageUrl": data["imageUrl"],
                "downloadUrl": f"{BASE_RAW_URL}{encoded_filename}"
            }
            addons_list.append(addon_entry)
            print(f" -> Verified and mapped: {data['title']}")
        else:
            print(f"[-] Missing local binary error: Link parsed for '{data['title']}' but no corresponding archive was discovered in local storage.")

    # Render clean output configuration block map
    if addons_list:
        with open("addons.json", "w", encoding="utf-8") as json_file:
            json.dump(addons_list, json_file, indent=4, ensure_ascii=False)
        print(f"\n[SUCCESS] addons.json configuration compiled cleanly with {len(addons_list)} active nodes.")
    else:
        print("\n[-] Index mapping incomplete. Address missing local resource locations.")

if __name__ == "__main__":
    run_safe_automation()
