import requests
import json
import os
import re
import logging
import time


TOKEN = os.environ['GITHUB_TOKEN']
OWNER = "apache"
# REPO = "druid-website-src"
REPO = "druid"


def get_paginated_list(url, headers):

    params = { "per_page": 100, "page": 1 }
    resultList = []
    # print(f'-------- Getting paginated result for {url}')

    while True:
        backoff = 10
        while True:
            r = requests.get(url, headers=headers, params=params)
            code = r.status_code
            logging.info(f'-------- Page {params}: return code {code}')
            if code == 200:
                break
            else:
                logging.info(f'-------- Page {params}: sleeping {backoff} before retry')
                time.sleep(backoff)
                backoff *= 2
        partList = r.json()
        elements = len(partList)
        logging.info(f'-------- Page {params}: Got {elements} elements')
        if elements == 0:
            break
        resultList += partList
        params['page'] += 1
    return resultList


def get_all_starred(st_url):

    url = re.sub(r'\{/[^\}]+\}', '', st_url)
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + TOKEN,
        "X-GitHub-Api-Version": "2022-11-28"
    }
    starred = get_paginated_list(url, headers)
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
    gazers = get_paginated_list(url, headers)
    return gazers


def main():

    logLevel = logging.INFO
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logLevel)

    logging.info(f'Getting users for repo {OWNER}/{REPO}')
    l = get_all_stargazers(OWNER, REPO)
    # print(l)

    # testlist = get_all_starred('https://api.github.com/users/chinnurtb/starred{/owner}{/repo}')
    # print(json.dumps(testlist))
    # l = []

    for u in l:
        u["starred_repo"] = OWNER + "/" + REPO
        logging.info(f'Getting stars for user {u["user"]["login"]}')
        u["other_starred_repos"] = get_all_starred(u["user"]["starred_url"])
        print(json.dumps(u))


if __name__ == "__main__":
    main()
