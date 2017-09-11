from peewee import *

class Submission(Model):
    uid = CharField()
    flair = CharField()
    title = CharField()
    url = CharField()
    body = CharField()

class ImageSubmission(Submission):
    image = CharField()