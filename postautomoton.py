import requests
import feedparser

rssfeed = 'https://bitsrfr.com/rss/'

def feedchecker(url):
    feed = feedparser.parse(url)

    entries = feed.entries
    post_info_set = set()
    post_list = []

    for entry in entries:
        post_info_set.clear()
        post_info_set.add(entry.title)
        #print(entry.title)
        post_info_set.add(entry.published)
        #print(entry.published)
        post_list.append(post_info_set.copy())
        #print(post_list)
        #return entry.title
        #return entry.published
    return post_list

post_list = feedchecker(rssfeed)

print(post_list)

'''
url = 'https://mstdn.social/api/v1/statuses'
auth = {'Authorization': 'Bearer <YOUR BEARER TOKEN/API AUTH KEY GOES HERE>'}

params = {'status': 'Mastodon API request from Pythong!'}

r = requests.post(url, data=params, headers=auth)

print(r)
'''
