from www.webcoro import *
from aiohttp import web
import logging
from www.models import *

logging.basicConfig(level=logging.INFO)


@get('/index')
def index(request):
    users = yield from User.findAll()
    return {
        '__template__': 'index.html',
        'users': users
    }


@get('/download')
def download(request):
    with open('/home/idouby/Pictures/sanli.jpg', 'rb') as file:
        content = file.read()
        return content


@post('/login')
def login(request):
    return web.Response(body=b'lalala')

# @post('/index')
# def pindex(request):
#     return 'I love you'
