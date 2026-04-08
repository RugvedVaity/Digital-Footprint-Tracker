import requests

def check_username(username):
    sites = {
        "GitHub": f"https://github.com/{username}",
        "Reddit": f"https://www.reddit.com/user/{username}",
        "Twitter": f"https://twitter.com/{username}"
    }

    results = {}

    for site, url in sites.items():
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                results[site] = True
            else:
                results[site] = False
        except:
            results[site] = False

    return results