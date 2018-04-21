# #!/usr/bin/env python
# -*- coding: utf-8 -*-
# <speakers - simple signal system for python>
# Copyright (C) <2013>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
from six import text_type
import re


def slugify(text):
    return re.sub(r'\W', '-', text.strip().lower())


def underlinefy(text):
    return slugify(text).replace('-', '_')


class nicepartial(object):
    def __init__(self, func, *args, **kw):
        self.func = func
        self.args = args
        self.kwargs = kw

    def __call__(self, *args, **kw):
        new = self.kwargs.copy()
        new.update(kw)
        return self.func(*(self.args + args), **new)

    def __repr__(self):
        return text_type('partial:{0}'.format(self.func.__name__))
