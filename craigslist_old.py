"""
craigsuck, a Craigslist RSS poller.
Copyright (c) 2011. Jake Brukhman <jbrukh@gmail.com>. See LICENSE. 
"""

from BeautifulSoup import BeautifulStoneSoup
import urllib2
import re

def append_rss(url):
    """
    A craigslist RSS feed will come in two flavors. Either it will appear
    as a GET parameter in the URL, e.g. &format=rss, or the page will be
    parameter-less, in which hase it will be the index.rss file.
    """
    if not re.search('format=rss|index.rss', url):
        if '?' in url:
            return url+'&format=rss'
        elif url.endswith('/'):
            return url+'index.rss'
    return url

def get_price_from_title(title):
    pattern = '[0-9]+'
    comp = re.compile(pattern)
    found = re.findall(comp, title)

    if found:
        return found[-1]
    else:
        return '-1' 

def get_location_from_title(title):
    pattern = '(\\([^\\(]+\\)) \\&\\#x00A5\\;'
    comp = re.compile(pattern)
    found = re.findall(comp, title)

    if found:
        return found[-1]
    else:
        return 'NOLOC' 

def get_id_from_url(url):
    pattern = '([0-9]+)\\.html'
    comp = re.compile(pattern)
    found = re.findall(comp, url)

    if found:
        return found[-1]
    else:
        return ''

def fetch(full_url):
    full_url = append_rss(full_url)
    page = urllib2.urlopen(full_url)

    # massage the pesky Craigslist CDATA tags so that entities are processed; TODO -- find out
    # if it would be better to sanitize entities separately.
    cdataMassage = [(re.compile('<!\[CDATA\[|]]>'), lambda match: '')]
    soup = BeautifulStoneSoup(page, markupMassage=cdataMassage,
                convertEntities=BeautifulStoneSoup.ALL_ENTITIES)
    for item in reversed(soup('item')):
        yield {
                'date':  item('dc:date')[0].string,
                'title': item.title.string,
                'link':  item.link.string,
                'price': get_price_from_title(item.title.string),
                'location': get_location_from_title(item.title.string),
                'id': get_id_from_url(item.link.string)
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
