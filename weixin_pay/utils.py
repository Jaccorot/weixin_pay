# -*- coding=utf-8 -*-

import hashlib
import re
from random import Random
import requests


def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Returns a bytestring version of 's', encoded as specified in 'encoding'.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
    if not isinstance(s, basestring):
        try:
            return str(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return ' '.join([smart_str(arg, encoding, strings_only,
                        errors) for arg in s])
            return unicode(s).encode(encoding, errors)
    elif isinstance(s, unicode):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s


def calculate_sign(params, api_key):
    #签名步骤一：按字典序排序参数, 在string后加入KEY
    url = "&".join(['%s=%s'%(key, smart_str(params[key])) for key in sorted(params)])
    url = '%s&key=%s' % (url, api_key)
    #签名步骤二：MD5加密, 所有字符转为大写
    return hashlib.md5(url).hexdigest().upper()


def dict_to_xml(params, sign):
    xml = ["<xml>",]
    for (k, v) in params.items():
        if (v.isdigit()):
            xml.append('<%s>%s</%s>' % (k, v, k))
        else:
            xml.append('<%s><![CDATA[%s]]></%s>' % (k, v, k))
    xml.append('<sign><![CDATA[%s]]></sign></xml>' % sign)
    return ''.join(xml)


def xml_to_dict(xml):
    if xml[0:5].upper() != "<XML>" and xml[-6].upper() != "</XML>":
        return None

    result = {}
    content = ''.join(xml[5:-6].strip().split('\n'))

    pattern = re.compile(r"<(?P<key>.+)>(?P<value>.+)</(?P=key)>") 
    m = pattern.match(content)
    while(m):
        key = m.group("key").strip()
        value = m.group("value").strip()
        pattern_inner = re.compile(r"<!\[CDATA\[(?P<inner_val>.+)\]\]>");
        inner_m = pattern_inner.match(value)
        if inner_m:
            value = inner_m.group("inner_val").strip()
        result[key] = value

        next_index = m.end("value") + len(key) + 3
        if (next_index >= len(content)):
            break;
        content = content[next_index:]
        m = pattern.match(content)

    return result


def random_str(randomlength=8):
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
    random = Random()
    return "".join([chars[random.randint(0, randomlength - 1)] for i in range(randomlength)])


def post_xml(url, xml):
    return requests.post(url, data=xml)
