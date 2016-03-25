import logging

logging.basicConfig(level=logging.INFO)
import asyncio, os, json, time
from datetime import datetime
from aiohttp import web


def index(request):
    return web.Response(body=b'<h1>Hello World!</h1>')


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)  # 生成app对象，传入事件循环
    app.router.add_route('GET', '/', index)  # 添加路由
    server = yield from loop.create_server(app.make_handler(), '127.0.0.1', 8000)  # 等待服务器生成
    logging.info('server has started at http://127.0.0.1:8000')  # 打印日志
    return server


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    loop.run_forever()  # 等待事务

if __name__ == '__main__':
    main()
