"""
Craigslist poller
"""

import bs4
from bs4 import BeautifulSoup
import urllib2
import re

def get_price(item):
    price = item.find('span', attrs={'class': 'result-price'})
    if price is not None:
        return price.contents[0]
    else:
        return 'NOPRICE'

def get_location(item):
    loc = item.find('span', attrs={'class': 'result-hood'})
    if loc is not None:
        return loc.contents[0]
    else:
        return 'NOLOC'

def get_title(item):
    title = item.find('a', attrs={'class': 'result-title hdrlnk'})
    if title is not None:
        return title.contents[0]
    else:
        return 'NOTITLE' 

def get_link(item):
    link = item.find('a', attrs={'class': 'result-title hdrlnk'})
    if link is not None:
        return link.get('href')
    else:
        #there is almost no such case
        return 'NOLINK' 

def get_repost(item):
    x = item.get('data-repost-of')
    if x is None:
        return 'NOREPOST'
    else:
        return x

def get_body(link):
    page = urllib2.urlopen(link)
    html = page.read()

    soup = BeautifulSoup(html, 'html.parser')
    # get only raw text
    result = soup.find("section", { "id" : "postingbody" })

    if result is not None:
        ret = list(filter(lambda x: (x.__class__ != bs4.element.Tag and x != u'\n'), result.contents[2:]))
    else:
        ret = 'NOBODY'

    return ret
    

def fetch(full_url):
    page = urllib2.urlopen(full_url)
    html = page.read()

    soup = BeautifulSoup(html, 'html.parser')
    results = soup.findAll("li", { "class" : "result-row" })
    for item in reversed(results):
        link = get_link(item)
        page_body = get_body(link)
        yield {
            'id': item.get("data-pid"),
            'price': get_price(item),
            'date': item.find('time')['datetime'],
            'title': get_title(item),
            'location': get_location(item),
            'link': link,
            'repost': get_repost(item),
            'body': page_body
        }

def fetch_with_pages_back(full_url, pages=1):
    s = range(100*(pages-1),-1,-100) # page offsets: cl "s=" parameter
    urls = map(
               lambda p: '%s&s=%s' % (full_url, p),
               s
           )
    return fetch_all(urls)

def fetch_all(queries):
    for query in queries:
        for listing in fetch(query):
               yield listing
    
#if __name__ == '__main__':
#    url = 'https://tokyo.craigslist.jp/d/for-sale/search/sss?lang=en&cc=us'
#    fetch(url)
