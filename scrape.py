import praw
import time
import logging
import configparser
from peewee import *

def fetch(sub, db):
    db.connect()
    if (not sub.display_name + '.lastfetch' in config['custom']):
        config['custom'][sub.display_name + '.lastfetch'] = '1300000000'
    if not Submission.table_exists():
        db.create_table(Submission)
    if not ImageSubmission.table_exists():
        db.create_table(ImageSubmission)
    db.close()
    imagePosts = []
    posts = []

    size = 0
    ilen = 0
    slen = 0

    for post in sub.submissions(start=int(config['custom'][sub.display_name + '.lastfetch'])):

        subm = {'uid': post.id,
                'flair': post.link_flair_text,
                'title': str(post.title),
                'url': str(post.url),
                'body': str(post.selftext)}
        if post.thumbnail == 'image' or 'imgur.com/' in post.url or '//i.redd.it' in post.url:
            imagePosts.append(subm)
            ilen += 1
        else:
            posts.append(subm)
            slen += 1
        size += 1

        if ilen != 0 and ilen % 500 == 0:
            with db.atomic():
                for dex in range(ilen - 500, len(imagePosts), 500):
                    ImageSubmission.insert_many(posts[dex:dex + 500]).execute()
                logger.info('updated image table')
        if slen != 0 and slen % 500 == 0:
                for dex in range(size - 500, len(posts), 500):
                    Submission.insert_many(posts[dex:dex + 500]).execute()
                logger.info('updated submission table')
        if size % 1000 == 0:
            logger.info('fetched ' + size.__str__() + ' posts')

    for dex in range(ilen - ilen % 500, len(imagePosts), 500):
        ImageSubmission.insert_many(posts[dex:dex + 500]).execute()
    logger.info('updated image table, total: ' + ilen)

    for dex in range(slen - slen % 500, len(posts), 500):
        Submission.insert_many(posts[dex:dex + 500]).execute()
    logger.info('updated submission table, total: ' + slen)

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

logging.info('Fetching from: ' + subb.display_name)
db = SqliteDatabase(subb.display_name + '.db')

class BaseModel(Model):
    class Meta:
        database = db

class Submission(BaseModel):
    uid = CharField()
    flair = CharField(null=True)
    title = CharField()
    url = CharField()
    body = CharField()

class ImageSubmission(Submission):
    image = CharField(null=True)

fetch(subb, db)
