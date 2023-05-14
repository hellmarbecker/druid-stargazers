import json
import logging
import sys


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
        all_other = rec.pop("other_starred_repos", None)

        for other in all_other:
            partrec = rec
            partrec["other_repo"] = other
            print(json.dumps(partrec))

    sys.exit(0)


if __name__ == "__main__":
    main()
