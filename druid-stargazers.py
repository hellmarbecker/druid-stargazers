import requests
import json
import os
import re

repo_url = "https://api.github.com/repos/apache/druid-website-src/stargazers"
# url = "https://api.github.com/repos/apache/druid/stargazers"
token = os.environ['GITHUB_TOKEN']
headers = {
    "Accept": "application/vnd.github.star+json",
    "Authorization": "Bearer " + token,
    "X-GitHub-Api-Version": "2022-11-28"
}

def get_all_starred(user_record):
    url = user_record["user"]["starred_url"]
    url = re.sub(r'\{/[^\}]+\}', '', url)
    print(url)    

def get_all_stargazers(owner, repo):

    url = "https://api.github.com/repos/" + owner + "/" + repo + "/stargazers"
    params = { "per_page": 10, "page": 1 }
    gazers = []

    while True:
        r = requests.get(url, headers=headers, params=params)
        partList = r.json()
        # print(partList)
        elements = len(partList)
        # print(params)
        # print(f'#elements: {elements}')
        if elements == 0:
            break
        gazers += partList
        params['page'] += 1
    return gazers

def main():

    # print("main")
    owner = "apache"
    repo = "druid-website-src"
    l = get_all_stargazers(owner, repo)
    # print(l)
    for u in l:
        u["starred_repo"] = owner + "/" + repo
        print(json.dumps(u))
    for u in l:
        get_all_starred(u)

if __name__ == "__main__":
    main()
