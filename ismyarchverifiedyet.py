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

def get_rebuilds(rebuilder):
    url = rebuilder + 'api/v0/pkgs/list?distro=archlinux'
    print('[*] Fetching ' + url)
    r = requests.get(url)
    r.raise_for_status()
    return {x['name']: {
        'version': x['version'],
        'status': x['status']
    } for x in r.json()}

def get_installed_pkgs():
    for line in subprocess.check_output(['pacman', '-Qn']).decode('utf-8').split('\n'):
        if line:
            name, version = line.split(' ')
            yield {
                'name': name,
                'version': version,
            }

rebuilds = []
for rebuilder in REBUILDERS:
    rebuilds.append(get_rebuilds(rebuilder))

total = 0
good = 0
for pkg in get_installed_pkgs():
    total += 1
    name = pkg['name']
    version = pkg['version']

    confirms = 0
    for rb in rebuilds:
        try:
            r = rb[name]
            if r['version'] != version:
                continue
            if r['status'] == 'GOOD':
                confirms += 1
        except KeyError:
            pass

    if confirms >= THRESHOLD:
        good += 1

    if confirms == 0:
        color = '\x1b[31m'
    elif confirms == 1:
        color = '\x1b[33m'
    else:
        color = '\x1b[32m'

    label = '%s %s' % (name, version)
    print('%s%-70s %s\x1b[0m' % (color, label, confirms))

if total == 0:
    percent = 0
else:
    percent = 100 / total * good
print('Your system is to %s%% verified' % percent)
