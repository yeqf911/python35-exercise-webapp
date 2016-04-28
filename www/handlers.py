from www.models import *
from www.webcoro import *

logging.basicConfig(level=logging.INFO)


@get('/index')
def index(request):
    users = yield from User.findAll()
    return {
        '__template__': 'index.html',
        'users': users
    }


@get('/blog')
def blog(requests):
    users = yield from User.findAll()
    return dict(__template__='blogs.html', users=users)


@get('/download')
def download(request):
    with open('/home/idouby/Pictures/sanli.jpg', 'rb') as file:
        content = file.read()
        return content


@get('/api/users')
def users(requests):
    user = yield from User.findAll()
    return dict(users=user)


@get('/login')
def login(request):
    return web.Response(body=b'lalala')


@get('/')
def index(request):
    summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    blogs = [
        Article(id='1', name='Test Blog', summary=summary, created_time=time.time() - 120),
        Article(id='2', name='Something New', summary=summary, created_time=time.time() - 3600),
        Article(id='3', name='Learn Swift', summary=summary, created_time=time.time() - 7200)
    ]
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }
