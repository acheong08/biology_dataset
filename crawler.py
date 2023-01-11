# Crawler for ib.bioninja.com.au

import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://ib.bioninja.com.au/"

class Tracker:
    """
    Tracks what has been crawled and what hasn't
    """
    def __init__(self):
        self.crawled = set()
        self.to_crawl = set()
    
    def add_to_crawl(self, url):
        if url not in self.crawled:
            self.to_crawl.add(url)
    
    def add_crawled(self, url):
        self.crawled.add(url)

    def save_progress(self, path):
        # Save as JSON
        with open(path, 'w') as f:
            f.write(json.dumps({
                'crawled': list(self.crawled),
                'to_crawl': list(self.to_crawl)
            }))
    
    def load_progress(self, path):
        # Load from JSON
        with open(path, 'r') as f:
            data = json.loads(f.read())
            self.crawled = set(data['crawled'])
            self.to_crawl = set(data['to_crawl'])

tracker = Tracker()

def crawl(url: str):
    """
    Crawl a single URL
    """
    print(f'Crawling {url}')
    # Get the page
    r = requests.get(url)
    tracker.add_crawled(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    # Find all the links
    for link in soup.find_all('a'):
        href = link.get('href')
        if not href:
            continue
        if href.startswith('#'):
            continue
        if href.startswith('mailto:'):
            continue
        if href.startswith('https://') or href.startswith('http://'):
            print(href)
            continue
        # remove everything after #
        if '#' in href:
            href = href[:href.find('#')]
        if '?' in href:
            href = href[:href.find('?')]
        modified_base = url
        modified_base = modified_base[:modified_base.rfind('/')]
        while href.count('../') > 0:
            href = href.replace('../', '', 1)
            modified_base = modified_base[:modified_base.rfind('/')]
        # If modified base does not end with a / add it
        if not modified_base.endswith('/'):
            modified_base += '/'
        next_url = modified_base + href
        if '../' in next_url:
            print(next_url)
            raise Exception('Too many ../')
        while './' in next_url:
            next_url = next_url.replace('./', '')
        tracker.add_to_crawl(next_url)
    
    # Save the page
    page_path = 'pages/' + url.replace('https://ib.bioninja.com.au', '').replace('/', '_')
    if page_path.endswith('_'):
        page_path += '.html'
    if page_path == 'pages/.html' or page_path == 'pages/_.html':
        page_path = 'pages/index.html'
    with open(page_path, 'w') as f:
        # Save only id="main-content"
        f.write(str(soup.find('div', {'id': 'main-content'}) or None))

    # Save progress
    tracker.save_progress('tracker.json')

    # # Recursively crawl next URL
    if tracker.to_crawl:
        crawl(tracker.to_crawl.pop())

if __name__ == '__main__':
    # Load progress
    try:
        tracker.load_progress('tracker.json')
    except FileNotFoundError:
        pass

    # Start crawling
    if BASE_URL not in tracker.crawled:
        tracker.add_to_crawl(BASE_URL)
    crawl(tracker.to_crawl.pop())