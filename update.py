from bs4 import BeautifulSoup
from datetime import datetime
import pickle
import urllib.request
import urllib.error


etags = {}


def get_request(url, key=None):
    if key is None:
        key = url
    try:
        req = urllib.request.Request(url, headers={"If-None-Match": etags[key]})
    except KeyError:
        req = urllib.request.Request(url)
    return req


def fetch(url, filename, key=None) -> bool:
    req = get_request(url, key)
    try:
        rf = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        print("error: {} {}: {}".format(e.code, e.reason, url))
        return False
    else:
        if key is None:
            key = url
        try:
            etags[key] = rf.info()["etag"]
        except KeyError:
            pass
        with open(filename, "wb") as wf:
            wf.write(rf.read())
        print("update: {}".format(filename))
        rf.close()
        return True


def fetch_nanj_supplement(url, supplement_rules, dns_rules) -> bool:
    req = get_request(url)
    try:
        rf = urllib.request.urlopen(req)
    except urllib.error.HTTPError as e:
        print("error: {} {}: {}".format(e.code, e.reason, url))
        return False
    else:
        try:
            etags[url] = rf.info()["etag"]
        except KeyError:
            pass
        rules = parse(rf.read())
        with open(supplement_rules, "w", encoding="utf-8") as wf:
            wf.write(rules[0])
        print("update: {}".format(supplement_rules))
        with open(dns_rules, "w", encoding="utf-8") as wf:
            wf.write(rules[1])
        print("update: {}".format(dns_rules))
        rf.close()
        return True


def parse(doc):
    soup = BeautifulSoup(doc, "html.parser")
    quotes = soup.select("#content blockquote p.quotation")
    rules = []
    for q in quotes:
        text = q.get_text()
        if text.startswith("! Title:"):
            rules.append(text)
    if len(rules) < 2:
        raise ValueError("cannot parse content")
    return (rules[0], rules[1])


def concat(dst, sources):
    with open(dst, "w", encoding="utf-8") as wf:
        for src in sources:
            with open(src, "r", encoding="utf-8") as rf:
                wf.write(rf.read())


def load_etags(etags_file):
    global etags
    try:
        rf = open(etags_file, "rb")
    except IOError:
        etags = {}
    else:
        etags = pickle.load(rf)
        rf.close()


def save_etags(etags_file):
    with open(etags_file, "wb") as fw:
        pickle.dump(etags, fw)


def main():
    today = datetime.today()

    r280_adblock_url = "https://280blocker.net/files/280blocker_adblock_{:%Y%m}.txt".format(today)
    r280_domain_url = "https://280blocker.net/files/280blocker_domain_ag_{:%Y%m}.txt".format(today)
    nanj_ag_url = "https://raw.githubusercontent.com/nanj-adguard/nanj-filter/master/nanj-filter.txt"
    nanj_wiki_url = "https://wikiwiki.jp/nanj-adguard/%E3%81%AA%E3%82%93J%E6%8B%A1%E5%BC%B5%E3%83%95%E3%82%A3%E3%83%AB%E3%82%BF%E3%83%BC"
    r280_adblock_file = "dist/280blocker_adblock_filter.txt"
    r280_domain_file = "dist/280blocker_domain_ag_filter.txt"
    nanj_ag_file = "dist/nanj-filter.txt"
    nanj_wiki_adblock_file = "dist/supplement_rules.txt"
    nanj_wiki_domain_file = "dist/DNS_rules.txt"
    merged_adblock_nanj_file = "dist/280blocker_adblock_filter_nanj.txt"
    merged_domain_nanj_file = "dist/280blocker_domain_ag_filter_nanj.txt"

    etags_file = "cache/etags"

    load_etags(etags_file)

    b1 = fetch(r280_adblock_url, r280_adblock_file, key="https://280blocker.net/files/280blocker_adblock_xxxxxx.txt")
    b2 = fetch(r280_domain_url, r280_domain_file, key="https://280blocker.net/files/280blocker_domain_ag_xxxxxx.txt")
    b3 = fetch(nanj_ag_url, nanj_ag_file)
    b4 = fetch_nanj_supplement(nanj_wiki_url, nanj_wiki_adblock_file, nanj_wiki_domain_file)

    if b1 or b3 or b4:
        concat(merged_adblock_nanj_file, [r280_adblock_file, nanj_ag_file, nanj_wiki_adblock_file])
        print("update: {}".format(merged_adblock_nanj_file))

    if b2 or b4:
        concat(merged_domain_nanj_file, [r280_domain_file, nanj_wiki_domain_file])
        print("update: {}".format(merged_domain_nanj_file))

    save_etags(etags_file)


if __name__ == '__main__':
    main()
