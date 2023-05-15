import json
import re
import csv
import logging
import sys


def main():

    global RESULTS
    logLevel = logging.INFO
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', level=logLevel)

    # Read stargazer records from stdin
    fieldnames = [ "starred_at", "email", "name", "login", "id", "twitter_username", "blog", "location" ] 
    set_nested_fieldnames = set(fieldnames[1:])

    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
    writer.writeheader()

    while True:
        next_line = sys.stdin.readline()

        if not next_line:
            break;
        rec = json.loads(next_line.strip())
        csvrec = { key : rec["user"][key] for key in rec["user"].keys() & set_nested_fieldnames }
        for key in csvrec:
            if type(csvrec[key]) is str:
                csvrec[key] = re.sub("\n", "", csvrec[key])

        csvrec["starred_at"] = rec["starred_at"]
        writer.writerow(csvrec)

    sys.exit(0)


if __name__ == "__main__":
    main()
