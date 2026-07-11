def run_cloud_automation():
    if not os.path.exists("links.txt"):
        return

    with open("links.txt", "r") as f:
        target_pages = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    addons_list = []
    
    for page_url in target_pages:
        data = scrape_mcpedl_metadata(page_url)
        if not data:
            continue
            
        # Create expected name, but do not rename anything
        expected_name = data["title"].replace(" ", "_") + ".mcpack"
        
        # Only add to list if the file ACTUALLY exists with that specific name
        if os.path.exists(expected_name):
            encoded_filename = urllib.parse.quote(expected_name)
            addon_entry = {
                "title": data["title"],
                "description": data["description"],
                "imageUrl": data["imageUrl"],
                "downloadUrl": f"{BASE_RAW_URL}{encoded_filename}"
            }
            addons_list.append(addon_entry)
            print(f"Verified: {data['title']}")
        else:
            print(f"[-] Missing file for: {data['title']} (Expected: {expected_name})")

    # Save and update JSON
    with open("addons.json", "w", encoding="utf-8") as json_file:
        json.dump(addons_list, json_file, indent=4, ensure_ascii=False)
