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

from __future__ import unicode_literals

import os
import sys
from collections import OrderedDict, defaultdict
from functools import wraps

from six import text_type as unicode
from six import binary_type
from six import PY3

from .handy import underlinefy, nicepartial
ENCODE = 'utf-8'


def force_bytes(s):
    if PY3:
        return binary_type(s, 'ascii').decode('ascii')

    return binary_type(s)


def _function_matches(one, other):
    one_code = get_code(one)
    other_code = get_code(other)
    return (os.path.abspath(one_code.co_filename) == os.path.abspath(other_code.co_filename) and
            one_code.co_firstlineno == other_code.co_firstlineno)


def get_code(func):
    return getattr(func, 'func_code', getattr(func, '__code__'))


class Function(object):
    def __init__(self, func):
        self.call = func
        self.name = func.__name__
        self.code = get_code(func)
        self.filename = os.path.relpath(self.code.co_filename)
        self.lineno = self.code.co_firstlineno + 1

    @property
    def module_name(self):
        return self.filename_without_extension.replace(os.sep, '.')

    @property
    def filename_without_extension(self):
        return os.path.splitext(self.filename)[0]

    def as_string(self, **kwargs):
        kw = OrderedDict()
        kw['name'] = self.name
        kw['lineno'] = self.lineno
        kw['filename'] = self.filename

        kw.update(kwargs)
        itemize = lambda d: ", ".join(['{0}="{1}"'.format(k, d[k]) for k in d])
        return 'Function({0})'.format(itemize(kw))

    def __str__(self):
        return self.as_string()

    def __repr__(self):
        return unicode(self.as_string())

    def __call__(self, *args, **kw):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        return self.call(*args, **kw)


SPEAKERS = OrderedDict()


class Speaker(object):
    def __init__(self, name, actions, output=None):
        self.name = underlinefy(name)
        self.actions = OrderedDict()
        self.hooks = defaultdict(list)
        self.default_exception_handler = Function(self.__base_exc_handler)
        self._exception_handler = self.default_exception_handler
        if not isinstance(actions, list):
            raise TypeError('actions must be a list of strings. Got %r' % actions)

        for action in map(underlinefy, actions):
            self.actions[action] = nicepartial(self.for_decorator, action)
            self.actions[action].shout = nicepartial(self.shout, action)
            self.actions[action].unplug = nicepartial(self.unplug, action)
            setattr(self, action, self.actions[action])

        SPEAKERS[name] = self

    def __str__(self):
        return 'Speaker(name={0}, actions={1}, total_hooks={2})'.format(
            self.name, self.actions, len(self.hooks))

    def __repr__(self):
        return unicode(self)

    def __base_exc_handler(self, speaker, exception, args, kwargs):
        raise

    def exception_handler(self, callback):
        if self._exception_handler is not self.default_exception_handler:
            raise RuntimeError('Attempt to register {0} as an exception_handler for {1}, but it already has {2} assigned'.format(
                Function(callback),
                self,
                self.exception_handler,
            ))

        self._exception_handler = Function(callback)
        return callback

    def for_decorator(self, action, callback):
        safe_action = underlinefy(action)

        responder = Function(callback)

        @wraps(responder.call)
        def wrapper(*args, **kw):
            try:
                res = callback(self, *args, **kw)
            except Exception as exc:
                if self.exception_handler:
                    return self._exception_handler(self, exc, args, kw)

            return res

        responder.key = force_bytes('{speaker}:{action}[{module}:{hook}:{lineno}]'.format(
            speaker=self.name,
            action=safe_action,
            module=responder.module_name,
            hook=wrapper.__name__,
            lineno=responder.lineno,
        ))
        wrapper.callback = callback
        wrapper.responder = responder
        self.hooks[action].append(wrapper)
        return responder

    def shout(self, action, *args, **kw):
        for hook in self.hooks[action]:
            result = hook(*args, **kw)
            if result:
                return result

    def unplug(self, action, callback):
        hooks = self.hooks[action]
        for hook in hooks:
            if callback.call == hook.callback:
                hooks.remove(hook)

    def release(self, action=None):
        if action is None:
            return list(map(self.release, self.hooks.keys()))

        while self.hooks[action]:
            self.hooks[action].pop()

    @classmethod
    def release_all(cls):
        for instance in SPEAKERS.values():
            instance.release()
