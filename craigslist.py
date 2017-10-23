"""
Craigslist poller
"""

from bs4 import BeautifulSoup 
import urllib2
import re

def get_price(item):
    price = item.find('span', attrs={'class': 'result-price'})
    if price is not None:
        return price.next_element
    else:
        return 'NOPRICE'

def get_location(item):
    loc = item.find('span', attrs={'class': 'result-hood'})
    if loc is not None:
        return loc.next_element
    else:
        return 'NOLOC'

def get_title(item):
    title = item.find('a', attrs={'class': 'result-title hdrlnk'})
    if title is not None:
        return title.next_element
    else:
        return 'NOTITLE' 

def get_link(item):
    link = item.find('a', attrs={'class': 'result-title hdrlnk'})
    if link is not None:
        return link.get('href')
    else:
        return 'NOLINK' 

def get_repost(item):
    x = item.get('data-repost-of')
    if x is None:
        return 'NOREPOST'
    else:
        return x

def fetch(full_url):
    page = urllib2.urlopen(full_url)
    html = page.read()

    soup = BeautifulSoup(html, 'html.parser')
    results = soup.findAll("li", { "class" : "result-row" })
    for item in reversed(results):
        yield {
            'id': item.get("data-pid"),
            'price': get_price(item),
            'date': item.find('time')['datetime'],
            'title': get_title(item),
            'location': get_location(item),
            'link': get_link(item),
            'repost': get_repost(item),
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
