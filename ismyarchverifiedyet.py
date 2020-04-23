#!/usr/bin/env python

import subprocess
import requests

# the rebuilders we're querying
REBUILDERS = [
    'https://wolfpit.net/rebuild/',
    'https://rebuilder.fzylab.net/',
]

# number of confirms required to consider it "verified" in our stats
THRESHOLD = 1

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
    return {x['name']: [x['version'], x['status']] for x in req.json()}


def get_installed_pkgs():
    lines = subprocess.check_output(['pacman', '-Qn'], universal_newlines=True)
    return [line.split() for line in lines.split('\n') if line]


def main():
    packages = get_installed_pkgs()
    rebuilds = [get_rebuilds(rebuilder) for rebuilder in REBUILDERS]

    good = 0

    for name, version in packages:
        versions = [build[name] for build in rebuilds if name in build]
        statuses = [status for ver, status in versions if ver == version]

        confirmations = statuses.count('GOOD')
        good += THRESHOLD <= confirmations

        color = COLOR_GREEN
        if confirmations == 0: color = COLOR_RED
        if confirmations == 1: color = COLOR_YELLOW

        label = f'{name} {version}'
        print(f'{color}{label:<70}{confirmations}{COLOR_RESET}')

    total = len(packages)
    percent = 100 / total * good if total else 0
    print(f'Your system is to {percent}% verified')


if __name__ == "__main__":
    main()
