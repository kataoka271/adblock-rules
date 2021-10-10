from bs4 import BeautifulSoup
from datetime import datetime
import os.path
import urllib.request


def can_update(date, filename):
    return not os.path.exists(filename) or (date - datetime.fromtimestamp(os.path.getmtime(filename))).days > 30


def fetch(url, filename):
    with urllib.request.urlopen(url) as rf:
        with open(filename, "wb") as wf:
            wf.write(rf.read())


def fetch_nanj_supplement_filter(supplement_rules, dns_rules):
    url = "https://wikiwiki.jp/nanj-adguard/%E3%81%AA%E3%82%93J%E6%8B%A1%E5%BC%B5%E3%83%95%E3%82%A3%E3%83%AB%E3%82%BF%E3%83%BC"
    with urllib.request.urlopen(url) as rf:
        soup = BeautifulSoup(rf.read(), "html.parser")
        quotes = soup.select("#content blockquote p.quotation")
        rules = []
        for q in quotes:
            text = q.get_text()
            if text.startswith("! Title:"):
                rules.append(text)
    if len(rules) < 2:
        raise ValueError("cannot parse content", url)
    with open(supplement_rules, "w", encoding="utf-8") as wf:
        wf.write(rules[0])
    with open(dns_rules, "w", encoding="utf-8") as wf:
        wf.write(rules[1])


def main():
    today = datetime.today()
    adblock_url = "https://280blocker.net/files/280blocker_adblock_{:%Y%m}.txt".format(today)
    domain_url = "https://280blocker.net/files/280blocker_domain_ag_{:%Y%m}.txt".format(today)
    nanj_url = "https://raw.githubusercontent.com/nanj-adguard/nanj-filter/master/nanj-filter.txt"
    adblock_file = "280blocker_adblock_filter.txt"
    nanj_file = "nanj-filter.txt"
    domain_file = "280blocker_domain_ag_filter.txt"
    nanj_supplement_file = "supplement_rules.txt"
    nanj_dns_file = "DNS_rules.txt"
    adblock_nanj_file = "280blocker_adblock_filter_nanj.txt"
    domain_nanj_file = "280blocker_domain_ag_filter_nanj.txt"
    if can_update(today, adblock_file):
        fetch(adblock_url, adblock_file)
        print("update: {}".format(adblock_file))
    if can_update(today, domain_file):
        fetch(domain_url, domain_file)
        print("update: {}".format(domain_file))
    if can_update(today, nanj_file):
        fetch(nanj_url, nanj_file)
        print("update: {}".format(nanj_file))
    if can_update(today, nanj_supplement_file) or can_update(today, nanj_dns_file):
        fetch_nanj_supplement_filter(nanj_supplement_file, nanj_dns_file)
        print("update: {}, {}".format(nanj_supplement_file, nanj_dns_file))
    if can_update(today, adblock_nanj_file):
        with open(adblock_nanj_file, "w", encoding="utf-8") as wf:
            with open(adblock_file, "r", encoding="utf-8") as rf:
                wf.write(rf.read())
            with open(nanj_file, "r", encoding="utf-8") as rf:
                wf.write(rf.read())
            with open(nanj_supplement_file, "r", encoding="utf-8") as rf:
                wf.write(rf.read())
        print("update: {}".format(adblock_nanj_file))
    if can_update(today, domain_nanj_file):
        with open(domain_nanj_file, "w", encoding="utf-8") as wf:
            with open(domain_file, "r", encoding="utf-8") as rf:
                wf.write(rf.read())
            with open(nanj_dns_file, "r", encoding="utf-8") as rf:
                wf.write(rf.read())
        print("update: {}".format(domain_nanj_file))


if __name__ == '__main__':
    main()
