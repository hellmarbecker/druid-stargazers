import requests

def main():

    url = "https://api.github.com/repos/apache/druid/stargazers"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer 62f49ab49c0c2d32c40bacc81256e12dcd566dd1",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    r = requests.get(url, headers=headers)
    print(r.json())

if __name__ == "__main__":
    main()
