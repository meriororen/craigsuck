#!/usr/bin/env python3.6

# -*- coding: utf-8 -*-
import random
import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import telepot
import string
import time
import sys

class LookupQueue(object):
    def __init__(self, size):
        self.s = set()
        self.q = []
        self.size = size

    def push(self, *items):
        for item in items:
            if item not in self.s:
                if len(self.q) == self.size:
                    self.pop()
                self.s.add(item)
                self.q.append(item)
                return item

    def pop(self):
        item = self.q.pop(0)
        self.s.remove(item)
        return item

    def __contains__(self, item):
        return item in self.s

    def __len__(self):
        return len(self.q)

    def __str__(self):
        return self.q.__str__()

    def __repr__(self):
        return self.q.__str__()


def get_price(item):
    price = item.find('div', attrs={'class': 'items-box-price'})
    return price.contents[0]

def get_id(item):
    link = item.find('a')
    return link.get('href').lstrip("https://item.mercari.com/jp/").strip("/")

def get_title(item):
    title = item.find('h3', attrs={'class': 'items-box-name'})
    return title.contents[0]

def fetch():
  args = { 'keyword':'ps4 ジャンク', 'sort_order':'created_desc', 'status_on_sale':'1' }
  hdr = { 'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
          'accept-encoding': 'deflate, br',
          'accept-language': 'en-US,en;q=0.9,ja;q=0.8,en-GB;q=0.7',
          'cache-control': 'max-age=0',
          'dnt': '1',
          'referer': 'https://www.mercari.com/jp/',
          'upgrade-insecure-requests': '1',
          'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36', }

  url = "https://www.mercari.com/jp/search/?" + urlencode(args, 'utf-8')
  req = urllib.request.Request(url, headers=hdr)
  res = urllib.request.urlopen(req)

  html = res.read().decode('utf8')
  soup = BeautifulSoup(html, 'html.parser')
  results = soup.findAll("section", { "class": "items-box" })
  for item in reversed(results):
      yield {
        'id' : get_id(item),
        'price' : get_price(item),
        'title' : get_title(item)
            }


def main():
    bot = telepot.Bot('460955917:AAFZgQBMKs3gzsRFuM1k9F-Pom5RGXgtALc')
    response = bot.getUpdates()
    _id = '320374704'
    
    queue = LookupQueue(100)
    while True:
        listings = fetch()
        new_listings = [l for l in listings if queue.push(l['id'])]
        for listing in new_listings:
            message = '<' + listing['price'] + '>' + listing['title'].replace("_", "\\_") + ' mercari://item/openDetail?id=m' + listing['id']
            #print('sending %s' % message)
            bot.sendMessage(_id, message, parse_mode='Markdown')
        time.sleep(15 + random.randrange(1, 30))

if __name__ == '__main__':
    main()
