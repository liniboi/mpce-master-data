import os
import json
import urllib.parse
import requests
import re
import difflib
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
        title = soup.find('h1').text.strip()
        img_tag = soup.find('meta', property='og:image')
        image_url = img_tag['content'] if img_tag else ""
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
            fn_low = filename.lower()
            
            # 1. Prefix and Suffix match (5 chars)
            prefix_match = fn_low[:5] == slug[:5]
            suffix_match = fn_low[-5:] == slug[-5:]
            
            # 2. Substring match (is slug inside filename?)
            substring_match = slug in fn_low
            
            # 3. Fuzzy match (Levenshtein distance <= 3)
            fuzzy_score = difflib.SequenceMatcher(None, fn_low, slug).ratio()
            fuzzy_match = fuzzy_score > 0.7 
            
            # Keyword matching
            file_keywords = get_keywords(fn_low)
            slug_keywords = get_keywords(slug)
            keyword_score = len(slug_keywords.intersection(file_keywords))
            
            # Aggregate conditions: If any trigger, consider it a match
            if prefix_match or suffix_match or substring_match or fuzzy_match or keyword_score > 0:
                # Use current score or a weight based on matching logic
                current_total_score = keyword_score + (1 if prefix_match else 0) + (1 if suffix_match else 0)
                
                if current_total_score >= highest_score:
                    highest_score = current_total_score
                    best_match = filename
        
        if best_match:
            data = get_metadata(page_url)
            if data:
                addon_entry = {
                    "title": data["title"],
                    "description": data["description"],
                    "imageUrl": data["imageUrl"],
                    "downloadUrl": f"{BASE_RAW_URL}{urllib.parse.quote(best_match)}"
                }
                addons_list.append(addon_entry)
                print(f"Verified: '{best_match}' for URL '{slug}'")

    with open("addons.json", "w", encoding="utf-8") as f:
        json.dump(addons_list, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    run_cloud_automation()
