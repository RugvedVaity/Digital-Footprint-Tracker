import requests

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

def check_username(username):
    sites = {
        "GitHub": f"https://github.com/{username}",
        "Reddit": f"https://www.reddit.com/user/{username}",
        "Twitter": f"https://twitter.com/{username}"
    }

    results = {}
    found_count = 0
    headers = {'User-Agent': USER_AGENT}

    for site, url in sites.items():
        try:
            response = requests.get(url, timeout=5, headers=headers)
            if response.status_code == 200:
                results[site] = True
                found_count += 1
            else:
                results[site] = False
        except requests.RequestException:
            results[site] = False

    # Risk score logic
    total_sites = len(sites)
    risk_score = int((found_count / total_sites) * 100)

    return results, risk_score