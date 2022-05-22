import pickle
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional, Union

import requests
from bs4 import BeautifulSoup


@dataclass
class Rule:
    path: str
    updated: bool = False


@dataclass
class TextRule:
    url: str
    key: str
    path: str
    updated: bool = False


@dataclass
class HtmlRule:
    url: str
    key: str
    adblock: Rule
    domain: Rule
    parser: Callable[[str], tuple[str, str]]


@dataclass
class StructuredRule:
    path: str
    rules: list[Union[TextRule, Rule]]


def fetch(etags: dict[str, str], rule: Union[TextRule, HtmlRule]):
    if isinstance(rule, HtmlRule):
        fetch_html(etags, rule)
    else:
        fetch_text(etags, rule)


def _fetch(etags: dict[str, str], rule: Union[TextRule, HtmlRule]) -> Optional[requests.Response]:
    if rule.key not in etags:
        headers = {}
    else:
        headers = {"If-None-Match": etags[rule.key]}
    r = requests.get(rule.url, headers=headers)
    if r.status_code == requests.codes.ok:
        return r
    else:
        print("{} {}: {}".format(r.status_code, r.reason, rule.url))


def fetch_text(etags: dict[str, str], rule: TextRule):
    r = _fetch(etags, rule)
    if r is not None:
        r.encoding = "utf-8"
        open(rule.path, "w", encoding="utf-8", newline="").write(r.text)
        rule.updated = True
        print("update: {}".format(rule.path))
        etags[rule.key] = r.headers["etag"]


def fetch_html(etags: dict[str, str], rule: HtmlRule):
    r = _fetch(etags, rule)
    if r is not None:
        adblock, domain = rule.parser(r.text)
        open(rule.adblock.path, "w", encoding="utf-8").write(adblock)
        rule.adblock.updated = True
        print("update: {}".format(rule.adblock.path))
        open(rule.domain.path, "w", encoding="utf-8").write(domain)
        rule.domain.updated = True
        print("update: {}".format(rule.domain.path))
        etags[rule.key] = r.headers["etag"]


def parse_nanj_wiki(doc: str) -> tuple[str, str]:
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


def merge(rule: StructuredRule):
    if any(r.updated for r in rule.rules):
        open(rule.path, "w", encoding="utf-8").write("".join(open(r.path, "r", encoding="utf-8").read() for r in rule.rules))
        print("update: {}".format(rule.path))


def main():
    path_etags = "cache/etags"
    today = datetime.today()
    r280_adblock = TextRule(
        url="https://280blocker.net/files/280blocker_adblock_{:%Y%m}.txt".format(today),
        key="https://280blocker.net/files/280blocker_adblock_xxxxxx.txt",
        path="dist/280blocker_adblock_filter.txt"
    )
    nanj_filter = TextRule(
        url="https://raw.githubusercontent.com/nanj-adguard/nanj-filter/master/nanj-filter.txt",
        key="https://raw.githubusercontent.com/nanj-adguard/nanj-filter/master/nanj-filter.txt",
        path="dist/nanj-filter.txt"
    )
    r280_domain = TextRule(
        url="https://280blocker.net/files/280blocker_domain_ag_{:%Y%m}.txt".format(today),
        key="https://280blocker.net/files/280blocker_domain_ag_xxxxxx.txt",
        path="dist/280blocker_domain_ag_filter.txt"
    )
    nanj_wiki = HtmlRule(
        url="https://wikiwiki.jp/nanj-adguard/%E3%81%AA%E3%82%93J%E6%8B%A1%E5%BC%B5%E3%83%95%E3%82%A3%E3%83%AB%E3%82%BF%E3%83%BC",
        key="https://wikiwiki.jp/nanj-adguard/%E3%81%AA%E3%82%93J%E6%8B%A1%E5%BC%B5%E3%83%95%E3%82%A3%E3%83%AB%E3%82%BF%E3%83%BC",
        adblock=Rule(
            path="dist/supplement_rules.txt"
        ),
        domain=Rule(
            path="dist/DNS_rules.txt"
        ),
        parser=parse_nanj_wiki
    )
    adblock_rules = StructuredRule(
        rules=[r280_adblock, nanj_filter, nanj_wiki.adblock],
        path="dist/01_adblock_rules.txt"
    )
    domain_ag_rules = StructuredRule(
        rules=[r280_domain, nanj_wiki.domain],
        path="dist/01_domain_ag_rules.txt"
    )
    try:
        etags = pickle.load(open(path_etags, "rb"))
    except IOError:
        etags = {}
    if len(sys.argv) > 1 and sys.argv[1] == "-f":
        etags = {}
    fetch(etags, r280_adblock)
    fetch(etags, nanj_filter)
    fetch(etags, r280_domain)
    fetch(etags, nanj_wiki)
    merge(adblock_rules)
    merge(domain_ag_rules)
    pickle.dump(etags, open(path_etags, "wb"))


if __name__ == '__main__':
    main()
