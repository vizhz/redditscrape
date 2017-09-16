import configparser
import logging

import praw
from peewee import *

config = configparser.ConfigParser()
config.read('praw.ini')

db = SqliteDatabase(config['custom']['sub'].lower() + '.db')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def authenticate():
    reddit = praw.Reddit('scrap', user_agent='pyscript')
    logging.info('Authenticated as ' + reddit.user.me().__str__())

    subb = reddit.subreddit(config['custom']['sub'].lower())
    logging.info('Working subreddit: ' + subb.display_name)
    return reddit, subb


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
