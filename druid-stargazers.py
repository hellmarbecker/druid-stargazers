import requests
import json
import os
import re
import logging
import time
from queue import Queue
from threading import Thread


TOKEN = os.environ['GITHUB_TOKEN']
OWNER = "apache"
# REPO = "druid-website-src"
REPO = "druid"
PAGESIZE = 50
RESULTS = {}

# Thread code from https://blog.jonlu.ca/posts/async-python-http

class Worker(Thread):
    """ Thread executing tasks from a given tasks queue """

    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
        try:
            func(*args, **kargs)
        except Exception as e:
            # An exception happened in this thread
            print(e)
        finally:
            # Mark this task as done, whether an exception happened or not
            self.tasks.task_done()


class ThreadPool:
    """ Pool of threads consuming tasks from a queue """

    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """ Add a task to the queue """
        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        """ Add a list of tasks to the queue """
        for args in args_list:
            self.add_task(func, args)

    def wait_completion(self):
        """ Wait for completion of all the tasks in the queue """
        self.tasks.join()


def get_paginated_list(url, headers):

    params = { "per_page": PAGESIZE, "page": 1 }
    resultList = []
    # print(f'-------- Getting paginated result for {url}')

    while True:
        backoff = 10
        gotit = False
        while True:
            r = requests.get(url, headers=headers, params=params)
            code = r.status_code
            logging.info(f'-------- URL {url} Page {params["page"]} (of {params["per_page"]}): return code {code}')
            if code == 200:
                logging.info(f'-------- URL {url} Page {params["page"]}: OK')
                gotit = True
                break
            elif code == 404:
                logging.info(f'-------- URL {url} Page {params["page"]}: error, no retry')
                gotit = False
                break
            else:
                if backoff < 3600:
                    logging.info(f'-------- URL {url} Page {params["page"]}: sleeping {backoff} before retry')
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    logging.info(f'-------- URL {url} Page {params["page"]}: backoff = {backoff}, giving up')
                    break
        if gotit:
            partList = r.json()
            elements = len(partList)
            logging.info(f'-------- URL {url} Page {params["page"]}: Got {elements} elements')
            if elements == 0:
                break
            resultList.append(partList)
        params['page'] += 1
    return resultList


def get_all_starred(u):

    global RESULTS
    st_url = u["user"]["starred_url"]
    username = u["user"]["login"]
    logging.info(f'---- in get_all_starred({username})')

    url = re.sub(r'\{/[^\}]+\}', '', st_url)
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + TOKEN,
        "X-GitHub-Api-Version": "2022-11-28"
    }
    starred = get_paginated_list(url, headers)
    starred_repos = [ repo_entry['full_name'] for sublist in starred for repo_entry in sublist ]
    print(json.dumps(starred_repos))
    RESULTS[username] = u
    RESULTS[username]["starred_repo"] = OWNER + "/" + REPO
    RESULTS[username]["other_starred_repos"] = starred_repos


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

    global RESULTS
    logLevel = logging.INFO
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logLevel)

    logging.info(f'Getting users for repo {OWNER}/{REPO}')
    ll = get_all_stargazers(OWNER, REPO)

    for p in ll:

        threads = len(p)
        pool = ThreadPool(threads)

        pool.map(get_all_starred, p)
        pool.wait_completion()

    for u in l:
        u["starred_repo"] = OWNER + "/" + REPO
        logging.info(f'Getting stars for user {u["user"]["login"]}')
        u["other_starred_repos"] = get_all_starred(u["user"]["starred_url"])
        # print(json.dumps(u))


if __name__ == "__main__":
    main()
