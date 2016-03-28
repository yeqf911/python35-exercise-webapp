from www.webcoro import *
from aiohttp import web
import logging

logging.basicConfig(level=logging.INFO)


@get('/index')
def index(request):
    return 404


@post('/login')
def login(request):
    return web.Response(body=b'lalala')


@post('/index')
def pindex(request):
    return 'I love you'
