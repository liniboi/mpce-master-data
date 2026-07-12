import os
import json
import urllib.parse
import requests
import re
from bs4 import BeautifulSoup

GITHUB_USERNAME = "liniboi"
REPO_NAME = "mpce-master-data"
BRANCH = "main"
BASE_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/{BRANCH}/"

def get_keywords(text):
    return set(re.findall(r'\w+', text.lower()))

def get_metadata(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get actual title and image
        title = soup.find('h1').text.strip()
        img_tag = soup.find('meta', property='og:image')
        image_url = img_tag['content'] if img_tag else ""
        
        # Get description
        paragraphs = soup.find_all('p')
        desc = next((p.text.strip() for p in paragraphs if len(p.text.strip()) > 30), f"Addon: {title}")
        
        return {"title": title, "description": desc, "imageUrl": image_url}
    except:
        return None

def run_cloud_automation():
    if not os.path.exists("links.txt"): return
    
    with open("links.txt", "r") as f:
        target_pages = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    local_files = [f for f in os.listdir(".") if f.endswith(('.mcpack', '.mcaddon'))]
    addons_list = []

    for page_url in target_pages:
        slug = page_url.strip("/").split("/")[-1].lower()
        
        best_match = None
        highest_score = 0
        
        for filename in local_files:
            # Check if the first 5 letters match (case-insensitive)
            if filename.lower()[:5] != slug[:5]:
                continue
            
            # Existing keyword matching logic
            file_keywords = get_keywords(filename)
            slug_keywords = get_keywords(slug)
            score = len(slug_keywords.intersection(file_keywords))
            
            if score > highest_score:
                highest_score = score
                best_match = filename
        
        if best_match and highest_score > 0:
            data = get_metadata(page_url)
            if data:
                addon_entry = {
                    "title": data["title"],
                    "description": data["description"],
                    "imageUrl": data["imageUrl"],
                    "downloadUrl": f"{BASE_RAW_URL}{urllib.parse.quote(best_match)}"
                }
                addons_list.append(addon_entry)
                print(f"Verified: '{best_match}' with image '{data['imageUrl']}'")

    with open("addons.json", "w", encoding="utf-8") as f:
        json.dump(addons_list, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    run_cloud_automation()
