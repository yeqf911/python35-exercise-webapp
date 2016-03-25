import asyncio
import aiomysql
from www import logging


def log(sql, args=()):
    logging.info('SQL: %s' % sql)


@asyncio.coroutine
def create_pool(loop, **kwargs):
    logging.info('Create the database connection pool')
    global __pool
    __pool = yield from aiomysql.create_pool(
            host=kwargs.get('host', '127.0.0.1'),
            port=kwargs.get('port', 3306),
            user=kwargs['user'],
            password=kwargs['password'],
            db=kwargs['db'],
            charset=kwargs.get('charset', 'utf-8'),
            autocommit=kwargs.get('autocommit', True),
            maxsize=kwargs.get('maxsize', 10),
            minsize=kwargs.get('minsize', 1),
            loop=loop,
    )


@asyncio.coroutine
def select(sql, args, size=None):
    log(sql, args)
    global __pool
    with (yield from __pool) as connection:
        # 得到游标，游标可以执行SQL语句
        cursor = yield from connection.cursor(aiomysql.DictCursor)
        yield from cursor.execute(sql.replace('?', '%s'), args or ())
        if size:
            rs = yield from cursor.fetchmany(size)
        else:
            rs = yield from cursor.fetchall()
        yield from cursor.close()
        logging.info('rows returned: %s' % len(rs))
        return rs


# for INSERT UPDATE DELETE use the common function
@asyncio.coroutine
def execute(sql, args):
    log(sql)
    global __pool
    with (yield from __pool) as conn:
        try:
            cursor = yield from conn.cursor(aiomysql.DictCursor)
            yield from cursor.execute(sql.replace('?', '%s'), args)
            affected = cursor.rowcount
            yield from cursor.close()
        except BaseException as e:
            raise
        return affected


# ======================================= 基本类型 ========================================
# 基本类型的基类，
class Field(object):
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)


# 对应数据库中string类型
class StringField(Field):
    def __init__(self, name=None, colum_type='varchar(100)', primary_key=False, default=None):
        Field.__init__(self, name, colum_type, primary_key, default)


# 对应数据库中int类型
class IntegerField(Field):
    def __init__(self, name=None, column_type='int', primary_key=False, default=None):
        Field.__init__(self, name, column_type, primary_key, default)


class TextField(Field):
    def __init__(self, name=None, default=None):
        Field.__init__(self, name, 'text', False, default)  # 类型和主键都是确定的，这里就直接写了


class BooleanField(Field):
    def __init__(self, name=None, default=None):
        Field.__init__(self, name, 'boolean', False, default)  # 类型和主键都是确定的，这里就直接写了


class FloatField(Field):
    def __init__(self, name=None, primary_key=False, default=None):
        Field.__init__(self, name, 'real', primary_key, default)  # 可能是主键


def create_args_string(length):
    L = []
    for i in range(length):
        L.append('?')
    return ', '.join(L)


# ====================================== Modle原型 ======================================
class ModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
        # 排除Model本身
        if name == 'Model':
            type.__init__(cls, name, bases, attrs)
        table_name = attrs.get('__table__', None) or name
        logging.info('found model: %s (table: %s)' % (name, table_name))
        mapping = dict()
        fields = []
        primary_key = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                logging.info('found mapping: %s ----> %s', (k, v))
                mapping[k] = v
                # 如果是v存在主键，则做主键处理
                if v.primary_key:
                    if primary_key:
                        raise RuntimeError('Duplicate primary key for field: %s' % k)
                    primary_key = k
                else:
                    fields.append(k)
        if not primary_key:
            raise RuntimeError('Primary key not found.')
        for k in mapping.keys():
            attrs.pop(k)
        # map(function, sequence)函数类似于hadoop中mapreduce的机制
        # 对与sequence中的每一个item都执行function函数，返回一个list
        escaped_fields = list(map(lambda f: '\'%s\'' % f, fields))
        attrs['__mapping__'] = mapping
        attrs['__table__'] = name
        attrs['__primary_key__'] = primary_key
        attrs['__field__'] = fields
        attrs['__select__'] = 'SELECT `%s`, %s FROM `%s`' % (primary_key, ', '.join(escaped_fields), table_name)
        attrs['__insert__'] = 'INSERT INTO `%s` (%s, `%s`) VALUE (%s)' % (
            table_name, ', '.join(escaped_fields), primary_key, create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'UPDATE `%s` SET %s WHERE `%s`=?' % (
            table_name, ', '.join(map(lambda f: '`%s`=?' % mapping.get(f).name or f), fields), primary_key)
        attrs['__delete__'] = 'DELETE FROM `%s` WHERE `%s`=?' % (table_name, primary_key)
        type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kwargs):
        super(Model, self).__init__(self, **kwargs)

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError("'Model' object has no attribute '%s'" % item)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    # 获取key对应的值（如果没有就取默认值）
    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mapping__[key]
            if field is not None:
                # 如果default是可调用的，则返回调用结果，否则返回default值
                value = field.default() if callable(field.default) else field.default
                logging.info('using the default value for %s:%s' % (key, value))
                setattr(self, key, value)
        return value

    # -----------------------------------数据库相关操作----------------------------------------

    # ########################### 类函数 ######################################
    @classmethod
    @asyncio.coroutine
    def find(cls, pk):
        rs = yield from select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), pk, 1)
        if len(rs) == 0:  # 如果查找内容长度为0，表示没有找到，返回None
            return None
        logging.info('find an object type:%s' % cls.__table__)
        return cls(**rs[0])  # 返回这个类型的一个对象

    @classmethod
    @asyncio.coroutine
    def findAll(cls, where=None, args=None, **kwargs):
        sql = list(cls.__select__)
        if where:  # 如果有where条件，类似于 City='Beijing' 之类的
            sql.append('where')  # sql关键字
            sql.append(where)
        if args is None:
            args = []

        orderBy = kwargs.get('orderBy', None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)

        limit = kwargs.get('limit', None)
        # 如果有limit， limit可以传入1个或2个数字做参数，
        # limit 5,10， 表示从第5行开始检索，检索10行
        # limit 5， 表示从头开始检索5行
        if limit:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                sql.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                sql.append(limit)
            else:  # 其他情况就是语法错误了
                raise ValueError('Invalid limit value: %s' % str(limit))
        rs = yield from select(' '.join(sql), args)
        if len(rs) == 0:
            return None
        return [cls(**x) for x in rs]  # 返回符合条件的所有对象

    @classmethod
    @asyncio.coroutine
    def findNumber(cls, where=None, args=None):
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        rs = yield from select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return 0
        return rs[0]['_num_']

    # ########################### 实例函数 ################################
    @asyncio.coroutine
    def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))  # 得到这个对象的属性列表，包含所有的属性
        args.append(self.getValueOrDefault(self.__primary_key__))  # 最后吧主键加入进去，因为主键是另外处理的
        row = yield from execute(self.__insert__, args)  # 异步io存储到数据库中
        if row != 1:
            logging.warning('failed to insert record: affected rows: %s' % row)

    @asyncio.coroutine
    def updates(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        row = yield from execute(self.__update__, args)
        if rs != 1:
            logging.warning('failed to update recode: affected rows: %s' % row)

    @asyncio.coroutine
    def remove(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        row = yield from execute(self.__delete__, args)
        if rs != 1:
            logging.warning('failed to delete recode: affected rows: %s' % row)