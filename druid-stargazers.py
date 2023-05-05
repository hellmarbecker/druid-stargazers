import requests
import json
import os

url = "https://api.github.com/repos/hellmarbecker/blog/stargazers"
# url = "https://api.github.com/repos/apache/druid/stargazers"
token = os.environ['GITHUB_TOKEN']
headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": "Bearer " + token,
    "X-GitHub-Api-Version": "2022-11-28"
}

def get_all_stargazers():

    params = { "per_page": 10, "page": 1 }
    gazers = []

    while True:
        r = requests.get(url, headers=headers, params=params)
        partList = r.json()
        print(partList)
        elements = len(partList)
        print(params)
        print(f'#elements: {elements}')
        if elements == 0:
            break
        gazers += partList
        params['page'] += 1
    return gazers

def main():

    print("main")
    l = get_all_stargazers()
    print(l)
    for u in l:
        print u

if __name__ == "__main__":
    main()
