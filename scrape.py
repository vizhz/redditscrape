import praw
import time
import logging
import configparser
from submission import *


def fetch(sub):
    logging.info('Fetching from: ' + sub.display_name)
    db = SqliteDatabase(sub.display_name + '.db')
    db.connect()
    if (not sub.display_name + '.lastfetch' in config['custom']):
        config['custom'][sub.display_name + '.lastfetch'] = '1300000000'

    db.create_tables([Submission,ImageSubmission])
    db.close()
    imagePosts = []
    posts = []

    size = 0
    ilen = 0
    slen = 0

    for post in sub.submissions(start=int(config['custom'][sub.display_name + '.lastfetch'])):

        subm = {'uid': post.id,
                'flair': '' if post.link_flair_text == None else post.link_flair_text,
                'title': str(post.title),
                'url': str(post.url),
                'body': str(post.selftext)}
        if post.thumbnail == 'image':
            imagePosts.append(subm)
            ilen += 1
        else:
            posts.append(subm)
            slen += 1
        size += 1

        if ilen % 500 == 0:
            with db.atomic():
                for dex in range(ilen - 500, len(imagePosts), 500):
                    ImageSubmission.insert_many(posts[dex:dex + 500]).execute()
                logger.info('updated image table')
        if slen % 500 == 0:
                for dex in range(size - 500, len(posts), 500):
                    Submission.insert_many(posts[dex:dex + 500]).execute()
                logger.info('updated image table')
        if size % 1000 == 0:
            logger.info('fetched ' + size.__str__() + ' posts')

    config['custom'][sub.display_name + '.lastfetch'] = time.time().__int__().__str__()
    with open('praw.ini', 'w') as f:
        config.write(f)



config = configparser.ConfigParser()
config.read('praw.ini')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

reddit = praw.Reddit('scrap', user_agent='pyscript')
logging.info('Authenticated as ' + reddit.user.me().__str__())

subb = reddit.subreddit(config['custom']['sub'].lower())

fetch(subb)
