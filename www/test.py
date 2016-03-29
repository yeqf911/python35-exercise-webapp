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
# from www import orm
# from www.models import User, Article, Comment
# import asyncio
# import aiomysql
#
# loop = asyncio.get_event_loop()
#
#
# # ------------------------------ 操作数据库的函数群补测试通过 ----------------------------------
# def save(loop):
#     pool = yield from orm.create_pool(loop, user='root', password='123456', db='awesome')
#     user1 = User(name='sanli', email='sanli@outlook.com', password='123456789', image='about:blank',
#                  admin='juren', )
#     yield from user1.save()
#     # 此处这个第二个user的id会和第一个id一样，不知道为什么
#     user2 = User(name='ez', email='ez@163.com', password='abcdefg', image='about:blank',
#                  admin='lol', )
#     yield from user2.save()
#
#
# def findAll(loop):
#     pool = yield from orm.create_pool(loop, user='root', password='123456', db='awesome')
#     users = yield from User.findAll()
#     print(users)
#
#
# def delete(loop):
#     pool = yield from orm.create_pool(loop, user='root', password='123456', db='awesome')
#     user = yield from User.find('000001458999416ff48f604a00e4506b879614c58c82902000')
#     if user:
#         yield from user.remove()
#
#
# def update(loop):
#     pool = yield from orm.create_pool(loop, user='root', password='123456', db='awesome')
#     user = yield from User.find('001459001089325a598a8e7c388474280a9a1dac47b907a000')
#
#     if user:
#         id = user.get('id')
#         print(id)
#         u = User(id=id, name='yasuo', password='gfgfasshd', email='lalala@qq.com', admin='cs', image='blank')
#         yield from u.updates()
#
#
# def findAttrs(loop):
#     pool = yield from orm.create_pool(loop, user='root', password='123456', db='awesome')
#     n = yield from User.findAttrs(selectField='name', where="admin='lol'")
#     print(n)
#
#
# def find(loop):
#     pool = yield from orm.create_pool(loop, user='root', password='123456', db='awesome')
#     user = yield from User.find('001459001001479860c50e88a044b69b253118bb688fb87000')
#     print(user)
#
#
# loop.run_until_complete(save(loop))
# d = {'name': 'xoaming', 'age': 15, 'score': 99, 'addr': 'anhui'}
#
# def f(**kwargs):
#     name = kwargs.get('name', 'qianfeng')
#     age = kwargs.get('age', 10)
#     print(name, age, sep='\t')
#
# l = ('d', 5, 'ds', True)
#
# def ff(*args):
#     a = args[0]
#     b = args[2]
#     print(a, b, sep='\t')
#
#
# f(**d)
# ff(*l)

# import asyncio
#
#
# @asyncio.coroutine
# def hello():
#     print('hello world')
#     r = yield from asyncio.sleep(3)
#     print('i an last but first')
#
#
# @asyncio.coroutine
# def index():
#     print('i am coroutine')
#
#
# class Base:
#     def index(self):
#         print('i am not coroutine')
#
#
# class A(Base):
#     @asyncio.coroutine
#     def index(self):
#         print('i am corortine')
#
# a = Base()
# loop = asyncio.get_event_loop()
# loop.run_until_complete(a.index())
# loop.close()

import uuid
import time


def nextid():
    return str(time.time()) + str(uuid.uuid4().hex)


def hello(default=nextid):
    print(default() + 'hellol')

hello()
time.sleep(2)
hello()