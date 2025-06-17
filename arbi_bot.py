import os
import praw
import re
from dotenv import load_dotenv
from datetime import datetime
import time
import json

# Load credentials from .env file
load_dotenv("auth/.env")

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT") or "arbi-bot/1.0"
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
PAYPAL_TIP_LINK = os.getenv("PAYPAL_TIP_LINK", "https://paypal.me/davidnitsan")

# Initialize Reddit client with login for messaging
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT,
    username=REDDIT_USERNAME,
    password=REDDIT_PASSWORD
)

SUBREDDITS = ["hardwareswap", "mechmarket", "AVexchange"]
BUYER_TAGS = ["wtb", "want to buy", "looking for", "need", "iso"]
SELLER_TAGS = ["fs", "for sale", "selling", "available", "wts"]

buyers, sellers = [], []

def classify(title):
    t = title.lower()
    if any(tag in t for tag in BUYER_TAGS):
        return "buyer"
    if any(tag in t for tag in SELLER_TAGS):
        return "seller"
    return None

print("🔎 Scanning posts...")
for sub in SUBREDDITS:
    for post in reddit.subreddit(sub).new(limit=100):
        kind = classify(post.title)
        if not kind:
            continue
        record = {
            "title": post.title,
            "url": f"https://www.reddit.com{post.permalink}",
            "author": str(post.author),
            "subreddit": sub,
            "created": datetime.fromtimestamp(post.created_utc, datetime.utcnow().astimezone().tzinfo).isoformat()
        }
        (buyers if kind == "buyer" else sellers).append(record)

print(f"\n🔍 Found {len(buyers)} buyers and {len(sellers)} sellers.")

# Match logic with word length condition
matches = []
for b in buyers:
    b_words = set(w for w in re.findall(r"\w+", b["title"].lower()) if len(w) >= 3)
    for s in sellers:
        s_words = set(w for w in re.findall(r"\w+", s["title"].lower()) if len(w) >= 3)
        shared = b_words & s_words
        if len(shared) >= 3 and any(len(w) >= 4 for w in shared):
            matches.append({"buyer": b, "seller": s, "shared": list(shared)})

# Save matches to file for dashboard
with open("matches.json", "w") as f:
    json.dump(matches, f, indent=2)
    print("✅ matches.json saved with", len(matches), "entries.")

# Show matches and DM users
MAX_MESSAGES = 10
sent_count = 0

for i, match in enumerate(matches, 1):
    b = match["buyer"]
    s = match["seller"]
    shared = match["shared"]

    if sent_count >= MAX_MESSAGES:
        print("🚫 Reached max messages for this run. Stopping early.")
        break

    print(f"\n🔗 Match #{i} — {len(shared)} shared words")
    print(f"🤝 Buyer:  {b['title']} | u/{b['author']} | r/{b['subreddit']}")
    print(f"↦  Seller: {s['title']} | u/{s['author']} | r/{s['subreddit']}")
    print(f"🧩 Keywords: {', '.join(shared)}")
    print(f"🔗 {b['url']} → {s['url']}")

    try:
        reddit.redditor(b['author']).message(
            subject="🎯 Match Found on Reddit",
            message=f"""Hey u/{b['author']}!

We found someone selling something related to your post:
🔹 {b['title']}

Check this out from u/{s['author']}:
💼 {s['title']}
🔗 {s['url']}

If this match helped you, consider sending us a $2 tip 🙏  
➡️ {PAYPAL_TIP_LINK}

Thanks for keeping Reddit commerce awesome!
"""
        )

        reddit.redditor(s['author']).message(
            subject="🎯 Interested Buyer Found",
            message=f"""Hey u/{s['author']}!

Someone may be interested in what you're selling:
💼 {s['title']}

Their post:
🔹 {b['title']}
🔗 {b['url']}

You can thank us later at {PAYPAL_TIP_LINK} if it helped :)
Cheers from ArbiBot 🤖
"""
        )

        print("📩 DMs sent to both buyer and seller.")
        sent_count += 1
        time.sleep(65)  # Avoid Reddit rate limit
    except Exception as e:
        print(f"❌ Could not send message: {e}")

# Optional: print unmatched buyers
if buyers:
    print("\n📋 Unmatched Buyers:")
    for buyer in buyers:
        print(f"\n👤 Buyer: {buyer['title']} | u/{buyer['author']} | r/{buyer['subreddit']}")
        print(f"🔗 {buyer['url']}")
