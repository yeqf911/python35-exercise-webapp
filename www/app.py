import logging
import asyncio, os, json, time
from datetime import datetime
from aiohttp import web
import os
import json
from jinja2 import Environment, FileSystemLoader
from www import webcoro
from www import orm
from www import config

logging.basicConfig(level=logging.INFO)


# 初始化jinja2模板引擎
def init_jinja2(app, **kw):
    logging.info('init jinja2...')
    options = dict(
        autoescape=kw.get('autoescape', True),
        block_start_string=kw.get('block_start_string', '{%'),
        block_end_string=kw.get('block_end_string', '%}'),
        variable_start_string=kw.get('variable_start_string', '{{'),
        variable_end_string=kw.get('variable_end_string', '}}'),
        auto_reload=kw.get('auto_eload', True)
    )
    path = kw.get('path', None)
    if path is None:
        # os.path.abspath(__file__)是获取当前文件的绝对目录
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
        # create one Environment object on application initialization and use that to load templates.
    logging.info('set jinja2 template path: %s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)
    # filters是干什么的
    filters = kw.get('filters', None)
    if filters is not None:
        for k, v in filters.items():
            env.filters[k] = v
    app['__templating__'] = env


# 设置日志拦截器
async def logger_factory(app, handler):
    logging.info('logger_factory --- 2')

    async def logger(request):
        logging.info('logger_factory: request: %s %s' % (request.method, request.path))
        return await handler(request)

    return logger


# 设置数据拦截器
async def data_factory(app, handler):
    logging.info('data_factory --- 2')

    async def parse_data(request):
        if request.method == 'POST':
            if request.content_type.startwith('application/json'):
                request.__data__ = await request.json()
                logging.info('Request json: %s' % str(request.__data__))
            elif request.content_type.startwith('application/x-www-form-urlencoded'):
                request.__data__ = await request.post()
                logging.info('Request form: %s' % str(request.__data__))
        logging.info('data_factory')
        return await handler(request)

    return parse_data


# 设置response拦截器
"""
测试发现，拦截器顺序是:
    客户端发送请求 -> logger_factory -> RequestHandler -> index处理(最终的url处理函数) -> response_factory
"""


async def response_factory(app, handler):
    logging.info('response_factory --- 2')

    async def response(request):
        rs = await handler(request)
        if isinstance(rs, web.StreamResponse):
            logging.info('Response StreamResponse: %s' % (rs))
            return rs
        if isinstance(rs, bytes):
            resp = web.Response(body=rs)
            resp.content_type = 'application/octet-stream'
            logging.info('Response bytes: %s %s' % (rs, resp.content_type))
            return resp
        if isinstance(rs, str):
            resp = web.Response(body=rs.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            logging.info('Response str: %s %s' % (rs, resp.content_type))
            return resp
        if isinstance(rs, dict):
            template = rs.get('__template__')
            if template is None:
                # 将rs格式化成json格式的字符串再encode成utf8的bytes
                resp = web.Response(
                    body=json.dumps(rs, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                logging.info('Response dict(template is None): %s %s' % (rs, resp.content_type))
                return resp
            else:
                # rs['__user__'] = request.__user__
                resp = web.Response(body=app['__templating__'].get_template(template).render(**rs).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                logging.info('Response dict(template not None): %s %s' % (rs, resp.content_type))
                return resp
        if isinstance(rs, int) and 100 <= rs <= 600:
            logging.info('Response int: %s' % (str(rs)))
            return web.Response(status=rs)
        if isinstance(rs, tuple) and len(rs) == 2:
            r, s = rs
            if isinstance(r, int) and 100 <= r <= 600:
                logging.info('Response tuple: %s %s' % (str(r), str(s)))
                return web.Response(r, str(s))
        # 默认情况就直接返回文本数据
        resp = web.Response(body=str(rs).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'  # 返回的类型是无格式的纯文本
        logging.info('Response default: %s %s' % (rs, resp.content_type))
        return resp
    return response


def datetime_filter(t):
    delta = int(time.time() - t)
    if delta < 60:
        return u'一分钟前'
    if delta < 3600:
        return u'%s小时前' % (delta / 60)
    if delta < 3600 * 24:
        return u'%s天前' % (delta / 3600)
    if delta < 3600 * 24 * 30:
        return u'%s个月前' % (delta / (3600 * 24))
    if delta < 3600 * 24 * 30 * 12:
        return u'%s年前' % (delta / (3600 * 24 * 30))
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


async def init(loop):
    configs = config.configs
    await orm.create_pool(loop, **configs.get('db'))
    # 添加拦截器，请求进来和返回请求结果都可以先经过拦截器处理一下
    """
    看官方文档说：Every middleware factory should accept two parameters, an app instance and a handler,
    and return a new handler.
    但是这个handler是怎么传入的呢？当一个请求过来的时候，aiohttp内部是什么机制来将handler与我们请求的url处理函数对应上的？
    """
    app = web.Application(loop=loop, middlewares=[
        data_factory, response_factory, logger_factory])  # 生成app对象，传入事件循环
    init_jinja2(app, filters=dict(datetime=datetime_filter))
    webcoro.add_routes(app, 'handlers')
    webcoro.add_static(app, 'static')
    server = await loop.create_server(app.make_handler(), '127.0.0.1', 8000)  # 等待服务器生成
    logging.info('server has started at http://127.0.0.1:8000')  # 打印日志
    return server


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    loop.run_forever()  # 等待事务


if __name__ == '__main__':
    main()
