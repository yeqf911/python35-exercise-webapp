import logging
from www.orm import Model, StringField, BooleanField, FloatField, TextField
import time
import uuid
import random

logging.basicConfig(level=logging.INFO)


def next_id():
    t = int(time.time() * 1000)
    return '%015d%s000' % (t, uuid.uuid4().hex)


class Article(Model):
    logging.info('start')
    __table__ = 'articles'
    id = StringField(primary_key=True, default=next_id(), colum_type='varchar(50)')
    user_id = StringField(colum_type='varchar(50)')
    user_name = StringField(colum_type='varchar(50)')
    user_image = StringField(colum_type='varchar(500)')
    title = StringField(colum_type='varchar(50)')
    content = TextField()
    summary = StringField(colum_type='varchar(200)')
    create_time = FloatField(default=time.time())


class Comment(Model):
    __table__ = 'comments'
    id = StringField(primary_key=True, default=next_id(), colum_type='varchar(50)')
    blog_id = StringField(colum_type='varchar(50)')
    user_id = StringField(colum_type='varchar(50)')
    user_name = StringField(colum_type='varchar(50)')
    user_image = StringField(colum_type='varchar(500)')
    content = TextField()
    create_time = FloatField(default=time.time())


class User(Model):
    __table__ = 'users'
    id = StringField(primary_key=True, default=next_id(), colum_type='varchar(50)')
    name = StringField(colum_type='varchar(50)')
    password = StringField(colum_type='varchar(100)')
    email = StringField(colum_type='varchar(50)')
    admin = BooleanField()
    image = StringField(colum_type='varchar(500)')
    create_time = FloatField(default=time.time())
