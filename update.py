from datetime import datetime
import os.path
import urllib.request


def can_update(date, filename):
    return not os.path.exists(filename) or (date - datetime.fromtimestamp(os.path.getmtime(filename))).days > 30


def fetch(url, filename):
    with urllib.request.urlopen(url) as rf:
        with open(filename, "wb") as wf:
            wf.write(rf.read())


def concat(file1, file2, dst):
    with open(file1, "r", encoding="utf-8") as f1:
        with open(file2, "r", encoding="utf-8") as f2:
            with open(dst, "w", encoding="utf-8") as wf:
                wf.write(f1.read())
                wf.write("\n")
                wf.write(f2.read())


def main():
    today = datetime.today()
    adblockUrl = "https://280blocker.net/files/280blocker_adblock_{:%Y%m}.txt".format(today)
    domainUrl = "https://280blocker.net/files/280blocker_domain_ag_{:%Y%m}.txt".format(today)
    nanjUrl = "https://raw.githubusercontent.com/nanj-adguard/nanj-filter/master/nanj-filter.txt"
    adblockFile = "280blocker_adblock_filter.txt"
    nanjFile = "nanj-filter.txt"
    domainFile = "280blocker_domain_ag_filter.txt"
    adblockNanjFile = "280blocker_adblock_filter_nanj.txt"
    if can_update(today, adblockFile):
        fetch(adblockUrl, adblockFile)
        print("update: {}".format(adblockFile))
    if can_update(today, domainFile):
        fetch(domainUrl, domainFile)
        print("update: {}".format(domainFile))
    if can_update(today, nanjFile):
        fetch(nanjUrl, nanjFile)
        print("update: {}".format(nanjFile))
    if can_update(today, adblockNanjFile):
        concat(adblockFile, nanjFile, adblockNanjFile)
        print("update: {}".format(adblockNanjFile))


if __name__ == '__main__':
    main()
