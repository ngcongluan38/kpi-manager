#!/usr/bin/python
# -*- coding: utf-8 -*-
# import re
# import socket

from hashlib import sha1
import random
from django.utils.text import slugify
from unidecode import unidecode


def slugify2(value):
    return slugify(unidecode(value))


def generate_sha1(string, salt=None):
    """
    Generates a sha1 hash for supplied string. Doesn't need to be very secure
    because it's not used for password checking. We got Django for that.

    :param string:
        The string that needs to be encrypted.

    :param salt:
        Optionally define your own salt. If none is supplied, will use a random
        string of 5 characters.

    :return: Tuple containing the salt and hash.

    """
    if not salt:
        salt = sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
    h = sha1(salt.encode('utf-8') + str(string).encode('utf-8')).hexdigest()

    return salt, h


def can_be_integer(value):
    """
    Đảm bảo giá trị đầu vào có thể ép về kiểu số Nguyên.
    :param value:
    :return:
    :rtype: bool
    """
    try:
        return isinstance(int(value), int)
    except ValueError:
        return False
