# app.py
from flask import Flask, render_template, request
import requests
import re
from urllib.parse import urlparse

app = Flask(__name__)

# === CONFIG ===
API_KEY = 'YOUR_GOOGLE_SAFE_BROWSING_API_KEY'  # Replace with your actual API key

# === Function 1: Google Safe Browsing Check ===
def check_with_google_safe_browsing(url):
    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={API_KEY}"
    headers = {"Content-Type": "application/json"}

    body = {
        "client": {
            "clientId": "phishing-checker",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    response = requests.post(endpoint, json=body, headers=headers)
    result = response.json()

    if "matches" in result:
        return "⚠️ Dangerous (Google Safe Browsing)"
    else:
        return None

# === Function 2: Rule-Based Heuristic Check ===
def rule_based_check(url):
    suspicious_keywords = ['login', 'secure', 'account', 'update', 'verify', 'webscr', 'ebay', 'paypal', 'phish']
    score = 0

    # Custom blacklist
    blacklisted_domains = ['phish.sinkingpoint.com', 'badurl.xyz']
    parsed_domain = urlparse(url).netloc
    if parsed_domain in blacklisted_domains:
        return "🚫 Blacklisted Domain"

    if '@' in url: score += 1
    if '-' in url: score += 1
    if url.count('.') > 3: score += 1
    if any(word in url.lower() for word in suspicious_keywords): score += 2
    if len(url) > 75: score += 1
    if re.search(r'\d{7,}', url): score += 1

    return "⚠️ Suspicious (Heuristic Analysis)" if score >= 2 else "✅ Likely Safe (Heuristic)"

# === Routes ===
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    url = request.form['url']
    result = check_with_google_safe_browsing(url)

    if not result:
        result = rule_based_check(url)

    return render_template("index.html", url=url, result=result)

if __name__ == '__main__':
    app.run(debug=True)
