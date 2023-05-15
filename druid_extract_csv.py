import json
import csv
import logging
import sys


def main():

    global RESULTS
    logLevel = logging.INFO
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logLevel)

    # Read stargazer records from stdin
    fieldnames = [ "starred_at", "email", "name", "login", "id", "twitter_username", "blog", "location" ] 

    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()

    while True:
        next_line = sys.stdin.readline()

        if not next_line:
            break;
        rec = json.loads(next_line.strip())
        csvrec = { key : rec["user"][key] for key in fieldnames[1:] }
        csvrec["starred_at"] = rec["starred_at"]
        writer.writerow(csvrec)

    sys.exit(0)


if __name__ == "__main__":
    main()
