import os
import json
import urllib.parse
import requests
from bs4 import BeautifulSoup

GITHUB_USERNAME = "liniboi"
REPO_NAME = "mpce-master-data"
BRANCH = "main"
BASE_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/{BRANCH}/"

def get_keywords(text):
    # Extracts meaningful words (removes special chars, lowercases)
    import re
    return set(re.findall(r'\w+', text.lower()))

def run_cloud_automation():
    if not os.path.exists("links.txt"): return
    
    with open("links.txt", "r") as f:
        target_pages = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    local_files = [f for f in os.listdir(".") if f.endswith(('.mcpack', '.mcaddon'))]
    addons_list = []

    for page_url in target_pages:
        slug = page_url.strip("/").split("/")[-1] # Gets "bedrock-ui-plus-b69-2" from URL
        slug_keywords = get_keywords(slug)
        
        best_match = None
        highest_score = 0
        
        # Scoring system: find the file that shares the most keywords with the URL
        for filename in local_files:
            file_keywords = get_keywords(filename)
            score = len(slug_keywords.intersection(file_keywords))
            
            if score > highest_score:
                highest_score = score
                best_match = filename
        
        if best_match and highest_score > 1: # Require at least 2 matching words
            data = {"title": best_match.replace(".mcpack", "").replace(".mcaddon", ""), 
                    "description": f"Addon: {best_match}", 
                    "imageUrl": "https://media.forgecdn.net/attachments/1610/159/1775109525257-png.png"}
            
            addon_entry = {
                "title": data["title"],
                "description": data["description"],
                "imageUrl": data["imageUrl"],
                "downloadUrl": f"{BASE_RAW_URL}{urllib.parse.quote(best_match)}"
            }
            addons_list.append(addon_entry)
            print(f"Verified: '{best_match}' matched with '{slug}'")
        else:
            print(f"[-] No match found for: '{slug}'")

    with open("addons.json", "w", encoding="utf-8") as f:
        json.dump(addons_list, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    run_cloud_automation()
