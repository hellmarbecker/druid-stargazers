import requests
import json
import os
import re
import logging
import time
import sys
from queue import Queue
from threading import Thread


TOKEN = os.environ['GITHUB_TOKEN']
OWNER = "apache"
REPO = "druid-website-src"
#REPO = "druid"
PAGESIZE = 100
RESULTS = {}


def get_gazers_detail(username):

    # global RESULTS
    logging.info(f'---- in get_gazers_detail({username})')

    url = "https://api.github.com/users/" + username
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + TOKEN,
        "X-GitHub-Api-Version": "2022-11-28"
    }
 
    backoff = 10
    while True:
        r = requests.get(url, headers=headers)
        code = r.status_code
        logging.info(f'-------- URL {url}: return code {code}')
        if code == 200:
            logging.info(f'-------- URL {url}: OK')
            gotit = True
            return r.json()
        elif code == 404:
            logging.info(f'-------- URL {url}: error 404, no retry')
            gotit = False
            break
        else:
            logging.info(f'-------- URL {url}: response {r.text}')
            if backoff < 3600:
                logging.info(f'-------- URL {url}: sleeping {backoff} before retry')
                time.sleep(backoff)
                backoff *= 2
            else:
                logging.info(f'-------- URL {url}: backoff = {backoff}, giving up')
                break
    return None


def main():

    global RESULTS
    logLevel = logging.INFO
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logLevel)

    # Read stargazer records from stdin

    while True:
        next_line = sys.stdin.readline()

        if not next_line:
            break;
        rec = json.loads(next_line.strip())
        uname = rec["user"]["login"]
        profile = get_gazers_detail(uname)
        if profile is not None:
            rec["user"] = profile
        print(json.dumps(rec))

    sys.exit(0)


if __name__ == "__main__":
    main()
