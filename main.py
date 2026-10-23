# Python 3.10+, GitHub Actions — V3rm with Playwright
import os
import time
import re
import requests
from playwright.sync_api import sync_playwright

V3RM_WEBHOOK = "https://discord.com/api/webhooks/1562446938580844644/3ExO8a9pWQtk9mYarD-Up4otbU01Q5UCDQ-HnBqhh59bA_tJVUMLgTWBJoZgjmJ_aXol"
V3RM_URL = "https://v3rm.net/forums/roblox.19/index.rss"
V3RM_SEEN = "v3rm_seen.txt"

def load_seen(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_seen(path, seen):
    with open(path, "w") as f:
        f.write("\n".join(sorted(seen)) + ("\n" if seen else ""))

def send_discord(title, url):
    payload = {"embeds": [{"title": title[:256], "url": url, "color": 0xE74C3C, "footer": {"text": "V3rm · roblox.19"}}]}
    requests.post(V3RM_WEBHOOK, json=payload)

def check_v3rm():
    print("[v3rm] Launching real Chrome browser...")
    seen = load_seen(V3RM_SEEN)
    baseline = not seen
    
    try:
        with sync_playwright() as p:
            # Launch a real Chrome instance
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Go to the RSS feed
            page.goto(V3RM_URL, timeout=60000)
            
            # Wait for Cloudflare to pass (it usually redirects to the XML)
            time.sleep(5) 
            
            # Grab the page content (which will be the XML text)
            html_content = page.content()
            browser.close()

        # Parse the XML
        items = re.findall(r'<item>.*?<title>(.*?)</title>.*?<link>(.*?)</link>', html_content, re.DOTALL)
        print(f"[v3rm] Found {len(items)} items.")
        
        for title, link in reversed(items):
            link = link.strip()
            title = title.replace("<![CDATA[", "").replace("]]>", "").strip()
            if link in seen: continue
            if baseline:
                seen.add(link); continue
            
            send_discord(title, link)
            seen.add(link)
            
    except Exception as e:
        print("[v3rm] error:", e)
        
    if baseline: print("[v3rm] baseline:", len(seen))
    save_seen(V3RM_SEEN, seen)

if __name__ == "__main__":
    print("Starting V3rm loop...")
    start_time = time.time()
    
    while time.time() - start_time < 21000:
        check_v3rm()
        print("Sleeping for 300 seconds...")
        time.sleep(300)
