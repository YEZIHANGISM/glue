import re, json
from django.http import QueryDict


def hump2snake(hump_str):
    p = re.compile(r'([a-z]|\d)([A-Z])')
    sub = re.sub(p, r'\1_\2', hump_str).lower()
    return sub


def snake2hump(snake_str):
    sub = re.sub(r'(_\w)', lambda x: x.group(1)[1].upper(), snake_str)
    return sub


class NamingTransform:

    def __init__(self, loads=False):
        self.loads = loads

    def return_json(self, data, *args, **kwargs):
        return json.dumps(data)

    def return_str(self, data, *args, **kwargs):
        return str(data)

    def return_int(self, data, *args, **kwargs):
        return int(data)

    def return_float(self, data, *args, **kwargs):
        return float(data)

    def default_return(self, data, *args, **kwargs):
        return data

    def parse_list(self, data, *args, **kwargs):
        ans = []
        for item in data:
            ans.append(self.dispath_return(item))
        return ans

    def dispath_return(self, data):
        raw_type, parse_type, parse_data = self.assuming_iterable(data)
        data_handler = getattr(self, f'parse_{parse_type}', self.default_return)
        fmt_data = data_handler(parse_data)
        return_handler = getattr(self, f'return_{raw_type}', self.default_return)
        return return_handler(fmt_data)

    def assuming_iterable(self, data):
        dtype, aftype = type(data).__name__, type(data).__name__
        if isinstance(data, str):
            # could be json
            try:
                data = json.loads(data)
                aftype = type(data).__name__
            except (TypeError, json.decoder.JSONDecodeError, AttributeError):
                pass
            else:
                if aftype not in ['int', 'float']:
                    dtype = self.loads and aftype or 'json'
        return dtype, aftype, data


class Snake(NamingTransform):

    def parse_dict(self, data, *args, **kwargs):
        return self.to_snake(data, nested=True)

    def to_snake(self, p: dict, nested=False):
        """
        hump to snake
        :param p: bounch of params
        :param nested: if set True, the return's type is dict. QueryDict, otherwise
        :rtype QueryDict
        """
        if not p: return p
        ans = nested and dict() or QueryDict(mutable=True)
        for k, v in p.items():
            v = self.dispath_return(v)
            ans[hump2snake(k)] = v
        return ans

class Hump(NamingTransform):

    def parse_dict(self, data, *args, **kwargs):
        return self.to_hump(data, nested=True)

    def to_hump(self, p, nested=False):
        """snake to hump"""
        if not p: return p
        ans = nested and dict() or QueryDict(mutable=True)
        for k, v in p.items():
            v = self.dispath_return(v)
            ans[snake2hump(k)] = v
        return ans
