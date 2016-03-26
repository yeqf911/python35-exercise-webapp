# g = (x * x for x in range(5))
# for i in g:
#     print(i)
#
# for i in g:
#     print('hello')
#     print(i)
#
#
# class Hello:
#     def say(self):
#         print('Hello')
#
#     @classmethod
#     def f(cls):
#         print('hello')
#
#     @staticmethod
#     def sf():
#         print('hello world')
#
# print('helo')
# Hello.f()
# Hello.sf()
# Hello().sf()
# h = Hello()
# h.f()
# h.say()
# h.sf()
#
# gifts = [1, 2, 2, 2, 3, 2]
#
# n = 6
# d = {}
#
# for x in gifts:
#     d[x] = 0
#
# for i in gifts:
#     d[i] += 1
#     if d[i] > n / 2:
#         print(i)
# s = 123
# d = 'hello'
# print('%015d%s000' % (s, d))
# import www.orm
# from www.models import User, Article, Comment
#
#
from www import orm
from www.models import User, Article, Comment
import asyncio
import aiomysql

loop = asyncio.get_event_loop()

# ------------------------------ 操作数据库的函数群补测试通过 ----------------------------------
def save(loop):
    pool = yield from orm.create_pool(loop, user='root', password='123456', db='awesome')
    user1 = User(name='xiazi', email='xaizi@outlook.com', password='123456789', image='about:blank',
                 admin='lol', )
    yield from user1.save()
    user2 = User(name='ez', email='ez@163.com', password='abcdefg', image='about:blank',
                 admin='lol', )
    yield from user1.save()


def findAll(loop):
    pool = yield from orm.create_pool(loop, user='root', password='123456', db='awesome')
    users = yield from User.findAll(where="admin='lol'")
    print(users)


def delete(loop):
    pool = yield from orm.create_pool(loop, user='root', password='123456', db='awesome')
    user = yield from User.find('000001458999416ff48f604a00e4506b879614c58c82902000')
    if user:
        yield from user.remove()


def update(loop):
    pool = yield from orm.create_pool(loop, user='root', password='123456', db='awesome')
    user = yield from User.find('001459001089325a598a8e7c388474280a9a1dac47b907a000')

    if user:
        id = user.get('id')
        print(id)
        u = User(id=id, name='yasuo', password='gfgfasshd', email='lalala@qq.com', admin='cs', image='blank')
        yield from u.updates()


def findNumber(loop):
    pool = yield from orm.create_pool(loop, user='root', password='123456', db='awesome')
    n = yield from User.findNumber(where="admin='lol'")
    print(n)

loop.run_until_complete(findNumber(loop))
