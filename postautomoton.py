import requests
import feedparser

rssfeed = 'https://bitsrfr.com/rss/'

def feedchecker(url):
    feed = feedparser.parse(url)

    entries = feed.entries
    post_info_dict = {}
    post_list = []

    for entry in entries:
        post_info_dict.update({'title': entry.title, 'date': entry.published})
        post_list.append(post_info_dict)
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
