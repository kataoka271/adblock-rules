import datetime
import urllib.request


def fetch(url, filename):
    with urllib.request.urlopen(url) as rf:
        with open(filename, "wb") as wf:
            wf.write(rf.read())


def main():
    today = datetime.datetime.today()
    adblockUrl = "https://280blocker.net/files/280blocker_adblock_{:%Y%m}.txt".format(today)
    domainUrl = "https://280blocker.net/files/280blocker_domain_ag_{:%Y%m}.txt".format(today)
    fetch(adblockUrl, "280blocker_adblock_filter.txt")
    fetch(domainUrl, "280blocker_domain_ag_filter.txt")


if __name__ == '__main__':
    main()
