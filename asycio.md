```python
@asyncio.coroutine
    def resolve(self, method, path):
        allowed_methods = set()
		
        match_dict = self._match(path)
        if match_dict is None:
            return None, allowed_methods
		# 这里遍历的对象是ResourceRoute对象，而self._routes是一个列
        # 表，里面的元素就是ResourceRoute对象，这里为什么用列表存储，我
        # 想是因为可能会有多个重名的url处理函数，但是各自的method不同，
        # 比如一个GET，一个POST，多个方法可能会封装成多个ResourceRoute
        # 对象，再加入到PlantResource的_routes属性中，所以_routes是一个list
        for route in self._routes:
            route_method = route.method
            # 将每一个检测到的method加入到allowed_method集合中，后面也
            # 许还会判断处理
            allowed_methods.add(route_method)
			# 如果这个method和request的method一样，或者这个method是'*',代表匹配所有method
            if route_method == method or route_method == hdrs.METH_ANY:
                return UrlMappingMatchInfo(match_dict, route), allowed_methods
        else:
            return None, allowed_methods
```


yield from 语句要经过一层coroutine函数的处理，处理完再返回原来的调用结果。即在coroutine函数内部：
```python
...
res = func(*args, **kw)
...
return res
```

返回之后回到最初调用处
```python
@asyncio.coroutine
    def resolve(self, request):
        path = request.raw_path
        method = request.method
        allowed_methods = set()

        for resource in self._resources:
            match_dict, allowed = yield from resource.resolve(method, path) # 就是这里
            if match_dict is not None:
            	# match_dict有匹配结果，则返回它
                return match_dict
            else:
                allowed_methods |= allowed
        # 如果遍历完resources还没有匹配的，就返回相应的错误结果，以代码看，应该是返回MatchInfoError(HTTPMethodNotAllowed(method,
                                                        allowed_methods))
        else:
            if allowed_methods:
                return MatchInfoError(HTTPMethodNotAllowed(method,
                                                           allowed_methods))
            else:
                return MatchInfoError(HTTPNotFound())

```

再次回到上一次调用处：
```python
@asyncio.coroutine
    def handle_request(self, message, payload):
        if self.access_log:
            now = self._loop.time()

        app = self._app
        request = web_reqrep.Request(
            app, message, payload,
            self.transport, self.reader, self.writer,
            secure_proxy_ssl_header=self._secure_proxy_ssl_header)
        self._meth = request.method
        self._path = request.path
        try:
        	# 解析request开始
            match_info = yield from self._router.resolve(request) # 就在这里

            assert isinstance(match_info, AbstractMatchInfo), match_info

            resp = None
            # 此处把匹配完成的match_info 赋值给 request._match_info
            request._match_info = match_info
            # 获取Expect头信息，如果不存在该头部信息，则继续执行，如果有，则采取特使服务
            # expect头信息是客户端要求的特殊服务器行为
            expect = request.headers.get(hdrs.EXPECT)
            if expect:
                resp = (
                    yield from match_info.expect_handler(request))

			# 表示没有接收到Expect头信息，反正是上一句没有执行成功就会执行这里了
            if resp is None:
           		# 重头戏来了，这里我们终于看到了handler了，
                # 通过调试信息可以看到，handler是一个function类型。他里面封装了一个_app属性，不用我说也应该知道这个_app属性就是我们整个web应用的app对象了
                # 这个handler最原始的地方在哪？我们继续深入，可以发现，此处的match_info 是
                handler = match_info.handler
                # 这里终于也执行到我们的拦截器 _middlewares了，遍历我们传入的拦截器列表, 而且是反向遍历，所以说同学们传入拦截器的时候就要留心了。
                # 至于为什么要倒呢，仔细想一想其实能想明白，因为函数的返回是一层一层的，每一次的拦截器的封装都会在上一个拦截器封装完的基础上继续封装的
                # 
                for factory in reversed(self._middlewares):
                	# 然后用factory装饰我们的handler，此处的factory正是我们传入的拦截器函数，yield from 返回的结果就是新的handler了，
                    # 如果本次循环的拦截器是logger_factory，那么返回的就是 logger 了
                    # 然后继续遍历下一个拦截器，继续装饰，直到所有的拦截器都装饰完成，这个时候的handler就集成了所有拦截器的功能了，
                    handler = yield from factory(app, handler)
                # 这里的handler()的执行过程其实先执行最外层的拦截器，遇到yield from handler()就再往里层的拦截器执行，最后执行到最终的url处理函数，
                resp = yield from handler(request)

            assert isinstance(resp, web_reqrep.StreamResponse), \
                ("Handler {!r} should return response instance, "
                 "got {!r} [middlewares {!r}]").format(
                     match_info.handler, type(resp), self._middlewares)
        except web_exceptions.HTTPException as exc:
            resp = exc

        resp_msg = yield from resp.prepare(request)
        yield from resp.write_eof()

        # notify server about keep-alive
        self.keep_alive(resp_msg.keep_alive())

        # log access
        if self.access_log:
            self.log_access(message, None, resp_msg, self._loop.time() - now)

        # for repr
        self._meth = 'none'
        self._path = 'none'

```

拦截器
```python
# 设置日志拦截器
async def logger_factory(app, handler):
	# 当你单步调试到这里的时候，你会发现，下一步直接就跳到了return logger，说明此时内部的logger并没
    # 有执行，你可以打个日志肯看是不是这样，那什么时候logger会执行呢？我们继续看...
    # 还有， 此时return logger 返回到哪了呢？
    # 继续单步执行，发现是返回到了原来的调用处。即是上面用拦截器装饰后的handler处。
    async def logger(request):
        logging.info('logger_factory: request: %s %s' % (request.method, request.path))
        return (await handler(request))
    return logger
```


request从什么地方进来的
```python
 @asyncio.coroutine
    def start(self):
        """Start processing of incoming requests.

        It reads request line, request headers and request payload, then
        calls handle_request() method. Subclass has to override
        handle_request(). start() handles various exceptions in request
        or response handling. Connection is being closed always unless
        keep_alive(True) specified.
        """
        reader = self.reader

        while True:
            message = None
            self._keep_alive = False
            self._request_count += 1
            self._reading_request = False

            payload = None
            try:
                # read http request method
                prefix = reader.set_parser(self._request_prefix)
                yield from prefix.read()

                # start reading request
                self._reading_request = True

                # start slow request timer
                if self._timeout and self._timeout_handle is None:
                    now = self._loop.time()
                    self._timeout_handle = self._loop.call_at(
                        ceil(now+self._timeout), self.cancel_slow_request)

                # read request headers
                httpstream = reader.set_parser(self._request_parser)
                message = yield from httpstream.read()

                # cancel slow request timer
                if self._timeout_handle is not None:
                    self._timeout_handle.cancel()
                    self._timeout_handle = None

                # request may not have payload
                if (message.headers.get(hdrs.CONTENT_LENGTH, 0) or
                    hdrs.SEC_WEBSOCKET_KEY1 in message.headers or
                    'chunked' in message.headers.get(
                        hdrs.TRANSFER_ENCODING, '')):
                    payload = streams.FlowControlStreamReader(
                        reader, loop=self._loop)
                    reader.set_parser(
                        aiohttp.HttpPayloadParser(message), payload)
                else:
                    payload = EMPTY_PAYLOAD

                yield from self.handle_request(message, payload)

            except asyncio.CancelledError:
                return
            except errors.ClientDisconnectedError:
                self.log_debug(
                    'Ignored premature client disconnection #1.')
                return
            except errors.HttpProcessingError as exc:
                if self.transport is not None:
                    yield from self.handle_error(exc.code, message,
                                                 None, exc, exc.headers,
                                                 exc.message)
            except errors.LineLimitExceededParserError as exc:
                yield from self.handle_error(400, message, None, exc)
            except Exception as exc:
                yield from self.handle_error(500, message, None, exc)
            finally:
                if self.transport is None:
                    self.log_debug(
                        'Ignored premature client disconnection #2.')
                    return

                if payload and not payload.is_eof():
                    self.log_debug('Uncompleted request.')
                    self._request_handler = None
                    self.transport.close()
                    return
                else:
                    reader.unset_parser()

                if self._request_handler:
                    if self._keep_alive and self._keep_alive_period:
                        self.log_debug(
                            'Start keep-alive timer for %s sec.',
                            self._keep_alive_period)
                        now = self._loop.time()
                        self._keep_alive_handle = self._loop.call_at(
                            ceil(now+self._keep_alive_period),
                            self.transport.close)
                    elif self._keep_alive and self._keep_alive_on:
                        # do nothing, rely on kernel or upstream server
                        pass
                    else:
                        self.log_debug('Close client connection.')
                        self._request_handler = None
                        self.transport.close()
                        return
                else:
                    # connection is closed
                    return
```

```python
class AbstractRoute(metaclass=abc.ABCMeta):
    METHODS = hdrs.METH_ALL | {hdrs.METH_ANY}

    def __init__(self, method, handler, *,
                 expect_handler=None,
                 resource=None):

        if expect_handler is None:
            expect_handler = _defaultExpectHandler

        assert asyncio.iscoroutinefunction(expect_handler), \
            'Coroutine is expected, got {!r}'.format(expect_handler)

        method = upstr(method)
        if method not in self.METHODS:
            raise ValueError("{} is not allowed HTTP method".format(method))
		# 假定_handler是callable()的
        assert callable(handler), handler
        if asyncio.iscoroutinefunction(handler):
            pass
        elif inspect.isgeneratorfunction(handler):
            warnings.warn("Bare generators are deprecated, "
                          "use @coroutine wrapper", DeprecationWarning)
        elif (isinstance(handler, type) and
              issubclass(handler, AbstractView)):
            pass
        else:
            handler = asyncio.coroutine(handler)

        self._method = method
        # 这里给handler赋值
        self._handler = handler
        self._expect_handler = expect_handler
        self._resource = resource

	这里的self的handler属性其实是个函数，返回的是_handler属性，_handler必须要是callable()的
    @property
   	def handler(self):
        return self._handler

```