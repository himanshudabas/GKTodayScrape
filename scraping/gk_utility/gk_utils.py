import re
import requests
from bs4 import BeautifulSoup
from scraping.gk_utility import req_head, YEARS, MONTHS


# headers for requests


# get year month and data from the string
def get_year_month_date(date_string):
    year_re = r'\d{4}'
    month_re = r'^[a-zA-Z]*'
    date_re = r'[0-9].*,'
    yr = re.findall(year_re, date_string)[0]
    mth = re.findall(month_re, date_string)[0]
    try:
        dt = re.findall(date_re, date_string)[0]
    except IndexError:
        dt = date_string.replace(yr, "")
        dt = dt.replace(mth, "")
        dt = dt.lstrip()
        dt = dt.rstrip()
    dt = dt.replace(",", "")
    return yr, mth.title(), dt


# function to map year and month
def map_year_month(yr, mth):
    _yr, _mth = None, None
    for i in range(len(YEARS)):
        if yr == YEARS[i]:
            _yr = i
            break
        else:
            _yr = 1

    for i in range(len(MONTHS)):
        if mth == MONTHS[i]:
            _mth = i
            break
        else:
            _mth = 0

    return _yr, _mth


# fetch article soup from the url
def fetch_article_soup(url):
    # request page using `requests`
    req_page = None
    while req_page is None:
        try:
            req_page = requests.get(url=url, headers=req_head)
        except Exception:
            print("-" * 30)
            print("connection error")
            req_page = None
    html = req_page.text
    # parse page using beautiful soup
    soup = BeautifulSoup(html, 'html.parser')
    return soup


# function to get the post_no. and mth from the fetched article
def get_month_post_no(url, mth, post_no):
    soup = fetch_article_soup(url)
    next_date_of_article = soup.find("span", {"class": "meta_date"}).text
    _, next_mth, _ = get_year_month_date(next_date_of_article)
    if mth.lower() != next_mth.lower():
        post_no = 1
    else:
        post_no += 1
    mth = next_mth
    return mth, post_no, soup
