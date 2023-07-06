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

REPOS = [
#   RTOLAP
    "apache/druid",
    "apache/pinot",
    "ClickHouse/ClickHouse",
    "apache/doris",
    "StarRocks/starrocks",
#   Streaming platforms
    "apache/kafka",
    "apache/pulsar",
    "redpanda-data/redpanda",
#   Stream Processors    
    "apache/flink",
    "apache/spark",
    "confluentinc/ksql",
#   Visualization
    "allegro/turnilo"
]
# TODO add superset etc.
# also it seems that after 400 requests against the stargazers endpoint for one repo, you get a 422 error for endpoint spammed
# and superset has more than 50k stars
PAGESIZE = 100
RESULTS = {}

# Thread code from https://blog.jonlu.ca/posts/async-python-http

class Worker(Thread):
    """ Thread executing tasks from a given tasks queue """

    def __init__(self, tasks):
        Thread.__init__(self)
        logging.debug(f'==== {self.name} in Worker.__init__')
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        logging.debug(f'==== {self.name} in Worker.run')
        while True:
            logging.debug(f'==== {self.name} in Worker.run before get')
            func, args, kargs = self.tasks.get()
            logging.debug(f'==== {self.name} in Worker.run after get: {func} {args}')
            try:
                logging.debug(f'==== {self.name} in Worker.run before call')
                func(*args, **kargs)
                logging.debug(f'==== {self.name} in Worker.run before call')
            except Exception as e:
                # An exception happened in this thread
                logging.error(e)
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
            logging.debug(f'adding task for {args}')
            self.add_task(func, args)

    def wait_completion(self):
        """ Wait for completion of all the tasks in the queue """
        self.tasks.join()


def get_one(url, **kw):
    """ Perform one GitHub API call. If this fails because of a rate limit, retry according to https://docs.github.com/en/rest/overview/resources-in-the-rest-api?apiVersion=2022-11-28#staying-within-the-rate-limit """

    backoff = 10
    sleepSeconds = -1
    code = -1
    while True:
        r = requests.get(url, **kw)
        code = r.status_code
        logging.info(f'-------- URL {url}: return code {code}')
        logging.debug(f'-------- URL {url}: response {r.text}')
        logging.info(f'-------- URL {url}: response headers {r.headers}')
        if code == 200:
            logging.info(f'-------- URL {url}: OK')
            break
        elif code == 404 or code == 422:
            logging.info(f'-------- URL {url}: error {code}, no retry')
            break
        elif code == 403:
            logging.info(f'-------- URL {url}: error {code}, possibly hitting rate limit')

            if 'Retry-After' in r.headers:
                sleepSeconds = r.headers['Retry-After']
                logging.info(f'-------- URL {url}: secondary rate limit hit, waiting {sleepSeconds}')
                # wait so many seconds
            elif 'X-RateLimit-Remaining' in r.headers and r.headers['X-RateLimit-Remaining'] == '0':
                timeRetry = r.headers['X-RateLimit-Reset']
                sleepSeconds = int(timeRetry) - time.time()
                logging.info(f'-------- URL {url}: global rate limit hit, waiting until {timeRetry}')
                # wait until time  
            elif backoff < 3600:
                # exponential backoff
                logging.info(f'-------- URL {url}: exponential backoff {backoff} before retry')
                sleepSeconds = backoff
                backoff *= 2
            else:
                logging.info(f'-------- URL {url}: backoff = {backoff}, giving up')
                break
            logging.info(f'-------- URL {url}: sleeping {sleepSeconds} before retry')
            time.sleep(sleepSeconds)
        else:
           logging.info(f'-------- URL {url}: error {code}, no retry')
    return r, code # return success code of last call


def get_paginated_list(url, headers):

    params = { "per_page": PAGESIZE, "page": 1 }
    resultList = []
    # print(f'-------- Getting paginated result for {url}')

    while True:
        r, lastcode = get_one(url, headers=headers, params=params)
        if lastcode == 200:
            partList = r.json()
            elements = len(partList)
            logging.info(f'-------- URL {url} Page {params["page"]}: Got {elements} elements')
            logging.debug(f'part list: {partList}')
            if elements == 0:
                break
            resultList += partList
            logging.debug(f'result list: {resultList}')
        elif lastcode == 422: # hit pagination limit, https://docs.github.com/en/rest/guides/using-pagination-in-the-rest-api?apiVersion=2022-11-28#about-pagination
            break
        params['page'] += 1
    return resultList


def get_all_starred(u):
    """ Get all repos that have been starred by user u """

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
    logging.debug(f'{username} stars: {json.dumps(starred_repos)}')
    # print(json.dumps(starred_repos))
    RESULTS[username] = u
    RESULTS[username]["starred_repo"] = OWNER + "/" + REPO
    RESULTS[username]["other_starred_repos"] = starred_repos
    # print(json.dumps(RESULTS[username]))


def get_gazers_detail(u):
    """ Get the profile of user u, including contct data """

    global RESULTS
    username = u["user"]["login"]
    logging.info(f'---- in get_gazers_detail({username})')

    url = "https://api.github.com/users/" + username
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": "Bearer " + TOKEN,
        "X-GitHub-Api-Version": "2022-11-28"
    }
 
    r, gotit = get_one(url, headers=headers)
    if gotit:
        RESULTS[username] = r.json()
        print(json.dumps(r.json()))


def get_all_stargazers(owner, repo):

    url = "https://api.github.com/repos/" + owner + "/" + repo + "/stargazers"
    headers = {
        "Accept": "application/vnd.github.star+json",
        "Authorization": "Bearer " + TOKEN,
        "X-GitHub-Api-Version": "2022-11-28"
    }
    gazers = get_paginated_list(url, headers)
    logging.debug(f'gazers: {gazers}')
    for g in gazers:
        g["starred_repo"] = owner + "/" + repo
    return gazers


def main():

    global RESULTS
    logLevel = logging.INFO
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logLevel)

    ll = []
    for repo in REPOS:
        logging.info(f'Getting users for repo {repo}')
        owner_repo = repo.split('/')
        l = get_all_stargazers(*owner_repo)
        ll += l

    get_detail = False
    if get_detail:
        logging.info(f'running {PAGESIZE} threads')
        pool = ThreadPool(PAGESIZE)

        for p in ll:

            logging.info(f'before map')
            # pool.map(get_all_starred, p)
            pool.map(get_gazers_detail, p)
            logging.info(f'after map')

        pool.wait_completion()
    else:
        for u in ll:
            print(json.dumps(u))

if __name__ == "__main__":
    main()
