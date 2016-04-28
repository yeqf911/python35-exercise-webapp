# coding=utf-8

import asyncio
import functools
import inspect
import logging
import os
from aiohttp import web

logging.basicConfig(level=logging.INFO)


def get(path):
    """定义装饰器 @get('/index') 以装饰url处理函数"""
    def decorator(func):
        logging.info('decrate the method: %s /%s' % ('GET', func.__name__))
        @functools.wraps(func)  # 加上这句是为了避免装饰器将原函数(func)的__name__改成wrapper了
        def wrapper(*args, **kwargs):
            logging.info('call the root url handler(GET): %s(%s)' % (func.__name__, ', '.join(inspect.signature(func).parameters.keys())))
            return func(*args, **kwargs)
        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper
    return decorator


def post(path):
    """定义装饰器@post('/login')"""
    def decorator(func):
        logging.info('decrate the method: %s /%s' % ('POST', func.__name__))
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logging.info('call the root url handler(POST): %s(%s)' % (func.__name__, ', '.join(inspect.signature(func).parameters.keys())))
            return func(*args, **kwargs)
        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper
    return decorator


class RequestHandler(object):
    def __init__(self, app, func):
        # 经过RequestHandler处理后，封装了app 和 func信息
        self._app = app
        self._func = func

    # 定义__call__()方法可以让该类的实例可以调用，调用的逻辑就是__call__()方法的逻辑
    async def __call__(self, request):
        # kw = request.query_string  # request是aiohttp模块里的Request对象，
        logging.info('before invoke method: %s(%s) in RequestHandler' % (self._func.__name__, ', '.join(inspect.signature(self._func).parameters.keys())))
        rs = await self._func(request)
        return rs


def add_route(app, func):
    method = getattr(func, '__method__', None)
    path = getattr(func, '__route__', None)
    if method is None or path is None:  # 这里判断的依据是通过@get()或@post()定义过的函数会封装__method__和__route__属性
        raise ValueError('the method: %s has not define @get(path) or @post(path).')
    # 如果函数不是coroutine的,就将其转化成coroutine的
    if not asyncio.iscoroutinefunction(func) and not inspect.isgeneratorfunction(func):
        func = asyncio.coroutine(func)
    logging.info('add the route %s %s ==> %s(%s)' % (
        method, path, func.__name__, ', '.join(inspect.signature(func).parameters.keys())))
    # 此处传入RequestHandler对象，它实现了__call__函数，所以是可调用的，调用的时候会继续调用func函数，
    # 就相当于在进入func函数之前，通过handler处理了一遍
    app.router.add_route(method, path, RequestHandler(app, func))


def add_routes(app, model_name):
    # 找到字符串'.'最后一次出现的位置的索引，此处即是找到xx.oo.mm中的mm
    n = model_name.rfind('.')
    # 返回值 n = -1 表示没有找到
    if n == -1:
        # 此处global() 和 locals()函数起什么作用？
        # 相当于 import model_name
        mod = __import__(model_name, globals(), locals())
        logging.info('import the handler module: %s' % model_name)
    else:
        name = model_name[n + 1:]
        # 相当与 from model_name[:n] import name,
        # 因为__import__(model_name[:n], globals(), locals(), [name])即是import的模块对象，那么getattr()就是获得name属性("子模块"?)
        mod = getattr(__import__(model_name[:n], globals(), locals(), [name]), name)
        logging.info('import the handler module: %s' % name)
    # 对mod里面的每个属性进行处理，如果符合要求就加入到路由里面
    for attr in dir(mod):
        if attr.startswith('_') or attr.startswith('__'):  # 显然下划线和双下划线开头的属性不符合要求
            continue
        # 得到属性对应的对象
        func = getattr(mod, attr)
        if callable(func):  # 是可调用的就处理
            method = getattr(func, '__method__', None)
            path = getattr(func, '__route__', None)
            if method and path:
                add_route(app, func)


def add_static(app, static):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), static)
    app.router.add_static('/static/', path)
    logging.info('add static %s ==> %s' % ('/static/', path))
