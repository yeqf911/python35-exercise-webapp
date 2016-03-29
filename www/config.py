# coding=utf-8
from www import config_default


class ConfigDict(dict):
    def __init__(self, name=(), value=(), **kw):
        dict.__init__(self, **kw)
        if len(name) == len(value):
            for k, v in zip(name, value):
                self[k] = v

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError("'Dict' object has no attribute %s" % item)

    def __setattr__(self, key, value):
        self[key] = value


def merge(default, overrite):
    r = {}
    for k, v in default.items():
        if k in overrite.keys():
            if isinstance(v, dict):
                r[k] = merge(v, overrite[k])
            else:
                r[k] = overrite[k]
        else:
            r[k] = v
    return r


# 将dict转化成 自定义的ConfigDict
def to_dict(d):
    D = ConfigDict()
    for k, v in d.items():
        if isinstance(v, dict):
            D[k] = to_dict(v)
        else:
            D[k] = v
    return D


configs = config_default.configs

try:
    from www import config_override

    configs = merge(configs, config_override.configs)
except ImportError:
    pass

configs = to_dict(configs)