# Python 3.10+, GitHub Actions — V3rm roblox.19 → Discord
import os
import time
import re
import requests

# --- YOUR V3RM WEBHOOK ---
V3RM_WEBHOOK = "https://discord.com/api/webhooks/1562446938580844644/3ExO8a9pWQtk9mYarD-Up4otbU01Q5UCDQ-HnBqhh59bA_tJVUMLgTWBJoZgjmJ_aXol"

# --- YOUR CLOUDFLARE WORKER PROXY ---
V3RM_PROXY = "https://v3rm-proxy.ppacktreeze.workers.dev/?url=https%3A%2F%2Fv3rm.net%2Fforums%2Froblox.19%2Findex.rss"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}

V3RM_SEEN = "v3rm_seen.txt"

def load_seen(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_seen(path, seen):
    with open(path, "w") as f:
        f.write("\n".join(sorted(seen)) + ("\n" if seen else ""))

def send_discord(title, description, url):
    payload = {"embeds": [{
        "title": title[:256], "url": url, 
        "description": description[:2048], 
        "color": 0xE74C3C, "footer": {"text": "V3rm · roblox.19"}
    }]}
    try:
        r = requests.post(V3RM_WEBHOOK, json=payload, headers=HEADERS, timeout=15)
        print("[hook]", r.status_code, "::", title[:60])
        time.sleep(1)
    except Exception as e:
        print("[hook] error:", e)

def check_v3rm():
    print("[v3rm] checking...")
    seen = load_seen(V3RM_SEEN)
    baseline = not seen
    try:
        r = requests.get(V3RM_PROXY, headers=HEADERS, timeout=20)
        print("[v3rm] status:", r.status_code)
        if r.status_code != 200: return
        
        # Parse the XML for new posts
        items = re.findall(r'<item>.*?<title>(.*?)</title>.*?<link>(.*?)</link>', r.text, re.DOTALL)
        
        for title, link in reversed(items):
            link = link.strip()
            title = title.replace("<![CDATA[", "").replace("]]>", "").strip()
            if link in seen: continue
            if baseline:
                seen.add(link); continue
                
            send_discord(title, "**New post in roblox.19**", link)
            seen.add(link)
    except Exception as e:
        print("[v3rm] error:", e)
        
    if baseline: print("[v3rm] baseline:", len(seen))
    save_seen(V3RM_SEEN, seen)

if __name__ == "__main__":
    print("Starting V3rm loop...")
    start_time = time.time()
    
    # Loop for ~5 hours 50 mins
    while time.time() - start_time < 21000:
        check_v3rm()
        print("Sleeping for 300 seconds (5 minutes)...")
        time.sleep(300)  # Changed from 60 to 300 to avoid rate limits
