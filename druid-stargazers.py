import requests
import json
import os
import re

TOKEN = os.environ['GITHUB_TOKEN']
OWNER = "apache"
REPO = "druid-website-src"
# REPO = "druid"

def get_all_starred(user_record):

    url = user_record["user"]["starred_url"]
    url = re.sub(r'\{/[^\}]+\}', '', url)
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + TOKEN,
        "X-GitHub-Api-Version": "2022-11-28"
    }
    params = { "per_page": 100, "page": 1 }
    starred = []
    # print(f'-------- Getting stars for {url}')

    while True:
        r = requests.get(url, headers=headers, params=params)
        partList = r.json()
        elements = len(partList)
        # print(f'-------- Page {params}: Got {elements} elements')
        if elements == 0:
            break
        starred += partList
        params['page'] += 1
    starred_repos = [ x['full_name'] for x in starred ]
    # print(json.dumps(starred_repos))
    return starred_repos


def get_all_stargazers(owner, repo):

    url = "https://api.github.com/repos/" + owner + "/" + repo + "/stargazers"
    headers = {
        "Accept": "application/vnd.github.star+json",
        "Authorization": "Bearer " + TOKEN,
        "X-GitHub-Api-Version": "2022-11-28"
    }
    params = { "per_page": 100, "page": 1 }
    gazers = []

    while True:
        r = requests.get(url, headers=headers, params=params)
        partList = r.json()
        elements = len(partList)
        if elements == 0:
            break
        gazers += partList
        params['page'] += 1
    return gazers


def main():

    l = get_all_stargazers(OWNER, REPO)
    # print(l)
    for u in l:
        u["starred_repo"] = owner + "/" + repo
        u["other_starred_repos"] = get_all_starred(u)
        print(json.dumps(u))


if __name__ == "__main__":
    main()
