#!/usr/bin/python3

#
# Check RSS feed for posts published in past __ hours
# If any, share post title and URL to Mastodon
#

import requests
import feedparser
from datetime import datetime, timedelta
import pytz

#### GLOBAL CONSTANTS ####

# Set URL of RSS feed to check
RSS_FEED_URL = 'https://bitsrfr.com/rss/'

# Set authorization token of Mastodon account
MASTODON_ACCESS_TOKEN = ''

# Set hostname (e.g. mstdn.social) of Mastodon account
MASTODON_HOST = 'mstdn.social'

# How often (in hours) will you run this script?
HOURS_SINCE_LAST_RUN = 24

#### FUNCTIONS ####

# Parse the RSS feed
# Add each post's title, URL, and published date to all_rss_posts
def parse_rss_feed():
    rss_feed = feedparser.parse(RSS_FEED_URL)
    rss_feed_entries = rss_feed.entries
    rss_post_info_dict = {}
    all_rss_posts = []

    for entry in rss_feed_entries:
        rss_post_info_dict.update({'title': entry.title, 'link': entry.link, 'date': entry.published})
        all_rss_posts.append(rss_post_info_dict.copy())
    return all_rss_posts

'''
# NOT USED IN CURRENT IMPLEMENTATION
# Call Mastodon API, supply access token, and obtain the user account ID
# ID is needed to check status updates posted by an account
def get_mastodon_account_id():
    mastodon_api_url = f'https://{MASTODON_HOST}/api/v1/accounts/verify_credentials'
    mastodon_api_auth = {'Authorization': f'Bearer {MASTODON_ACCESS_TOKEN}'}

    response = requests.get(mastodon_api_url, headers=mastodon_api_auth)

    json_response = response.json()
    mastodon_account_id = json_response['id']
    return mastodon_account_id

# NOT USED IN CURRENT IMPLEMENTATION
# Call Mastodon API, supply account ID, and obtain account's status updates
# Extract only the content of each status update
def parse_mastodon_account_statuses(mastodon_account_id):
    mastodon_api_url = f'https://{MASTODON_HOST}/api/v1/accounts/{mastodon_account_id}/statuses'

    response = requests.get(mastodon_api_url)

    status_updates = response.json()

    mastodon_account_statuses = []

    for entry in status_updates:
        mastodon_account_statuses.append(entry['content'])
    return mastodon_account_statuses
'''

# Convert the RSS post date/time to UTC, and make it offset-aware
def convert_rss_post_datetime_to_utc(rss_post):
    rss_post_date = datetime.strptime(rss_post['date'], "%a, %d %b %Y %H:%M:%S %Z")
    
    ### figuring out the UTC offset of the timezone of the post date
    # parse string and pull last 3 characters
    third_to_last_of_rss_date = rss_post['date'][-3]
    # if number, then use %z in formatting the post date
    if third_to_last_of_rss_date.isdigit():
        rss_post_date_offset_aware = datetime.strptime(rss_post['date'], "%a, %d %b %Y %H:%M:%S %z")
    # note: RSS feed specs only allow for either timezone code (GMT, EST, etc) or UTC offset (+0000, -0500, etc)
    # That's why we only need to check if third to last value of string is a digit
    # else they are letters, then convert to UTC offset
    else:
        # get the last 3 values of the RSS post's date string
        rss_post_timezone_code = rss_post['date'][-3:]
        # convert the last 3 values of the RSS post's date string into a datetime timezone object
        rss_post_timezone = pytz.timezone(rss_post_timezone_code)
        # Calculate the UTC offset value of the RSS post's timezone
        rss_post_date_offset = rss_post_date.astimezone(rss_post_timezone).strftime('%z')
        # Remove the timezone abbreviation and convert the RSS post's date to a string
        rss_post_date_no_timezone = rss_post_date.strftime('%a, %d %b %Y %H:%M:%S')
        # Concatenate the new RSS post date string with the RSS post's UTC offset
        rss_post_date_offset_aware_string = rss_post_date_no_timezone + " " + rss_post_date_offset
        
        # Convert the string to datetime object
        rss_post_date_offset_aware = datetime.strptime(rss_post_date_offset_aware_string, "%a, %d %b %Y %H:%M:%S %z")
        
    return rss_post_date_offset_aware

# Look through RSS posts to see if there has been a new post in past 24 hours
# If so, add to list of new_rss_posts
def get_new_rss_posts(all_rss_posts):
    current_time_utc_offset_aware = datetime.now(pytz.utc)
    new_rss_posts = []

    for rss_post in all_rss_posts:
        rss_post_date_offset_aware = convert_rss_post_datetime_to_utc(rss_post)
        last_rss_feed_check = current_time_utc_offset_aware - timedelta(hours=HOURS_SINCE_LAST_RUN)
        if rss_post_date_offset_aware > last_rss_feed_check:
            print("Item to share to Mastodon: ")
            print(rss_post['title'])
            new_rss_posts.append(rss_post)
    return new_rss_posts

# Share new_rss_posts via status update to Mastodon
def share_rss_posts_to_mastodon(new_rss_posts):
    mastodon_api_responses = []

    for rss_post in new_rss_posts:
        rss_post_title = rss_post['title']
        rss_post_url = rss_post['link']
        mastodon_status_update_text = f'NEW POST! {rss_post_title} :: {rss_post_url}'
        mastodon_api_url = f'https://{MASTODON_HOST}/api/v1/statuses'
        mastodon_api_auth = {'Authorization': f'Bearer {MASTODON_ACCESS_TOKEN}'}
        mastodon_api_params = {'status': f'{mastodon_status_update_text}'}
        mastodon_api_response = requests.post(mastodon_api_url, data=mastodon_api_params, headers=mastodon_api_auth)
        mastodon_api_responses.append(mastodon_api_response)
    return mastodon_api_responses

#### THE ACTION ####

all_rss_posts = parse_rss_feed()
# mastodon_account_id = get_mastodon_account_id()
# mastodon_account_statuses = parse_mastodon_account_statuses(mastodon_account_id)
new_rss_posts = get_new_rss_posts(all_rss_posts)
mastodon_api_responses = share_rss_posts_to_mastodon(new_rss_posts)

# Print the status of the Mastodon API post
for response in mastodon_api_responses:
    if response.status_code == 200:
        print("Success!")
    else:
        print(f'Failure with status code: {response.status_code}')

# Joseph Kreydt
# The Lord is our God, the Lord alone!
