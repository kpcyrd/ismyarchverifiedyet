#!/usr/bin/env python

import argparse
import subprocess
import requests

# the rebuilders we're querying
REBUILDERS = [
    'https://reproducible.archlinux.org/',
    'https://wolfpit.net/rebuild/',
    'https://r-b.engineering.nyu.edu/',
    'https://rebuilder.pitastrudl.me/',
    'https://reproducible.crypto-lab.ch/'
]

# number of confirms required to consider it "verified" in our stats
THRESHOLD = 1
GOOD = 'good'
BAD = 'bad'

# ansi escape sequences
COLOR_RED = '\x1b[31m'
COLOR_GREEN = '\x1b[32m'
COLOR_YELLOW = '\x1b[33m'
COLOR_RESET = '\x1b[0m'


def get_rebuilds(rebuilder):
    url = f'{rebuilder}api/v0/pkgs/list?distro=archlinux'
    print(f'[*] Fetching {url}')
    req = requests.get(url)
    req.raise_for_status()
    return {(x["name"], x["version"]): x['status'] for x in req.json()}


def get_installed_pkgs():
    lines = subprocess.check_output(['pacman', '-Qn'], universal_newlines=True)
    return [line.split() for line in lines.split('\n') if line]


def main(status):
    packages = get_installed_pkgs()
    rebuilds = []
    for rebuilder in REBUILDERS:
        try:
            r = get_rebuilds(rebuilder)
        except Exception as e:
            print(f'[-] Error: {e}')
        else:
            rebuilds.append(r)

    good = 0

    for name, version in packages:
        pkg = (name, version)
        statuses = [build[pkg] for build in rebuilds if pkg in build]

        confirmations = statuses.count('GOOD')
        good += THRESHOLD <= confirmations

        if status == BAD and THRESHOLD <= confirmations:
            continue
        elif status == GOOD and THRESHOLD > confirmations:
            continue

        color = COLOR_GREEN
        if confirmations == 0:
            color = COLOR_RED
        if confirmations == 1:
            color = COLOR_YELLOW

        label = f'{name} {version}'
        print(f'{color}{label:<70}{confirmations}{COLOR_RESET}')

    total = len(packages)
    percent = 100 / total * good if total else 0
    print(f'Your system is to {percent:.1f}% verified')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Shows the amount of reproducible packages on your system.')
    parser.add_argument('--status', type=str, choices=[GOOD, BAD], help='Filter results on reproducible status')

    args = parser.parse_args()
    main(args.status)
