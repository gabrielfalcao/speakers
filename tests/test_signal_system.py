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

from mock import Mock
from speakers.bus import Function, Speaker


def test_function_as_string():
    "Function#as_string"

    def testing():
        pass

    s = Function(testing)

    str(s).should.equal('Function(name="testing", lineno="37", filename="tests/test_signal_system.py")')


def test_function_repr():
    "repr(#Function)"

    def testing():
        pass

    s = Function(testing)

    repr(s).should.equal(b'Function(name="testing", lineno="48", filename="tests/test_signal_system.py")')


def test_speaker_with_wrong_parameter():
    "Speaker takes list of strings"

    Speaker.when.called_with("Testing", "foo").should.throw(
        TypeError, "actions must be a list of strings. Got u'foo'")


def test_speaker_as_string():
    "Speaker as string"

    sp = Speaker("AwesomeSauce", ['do this', 'do that'])
    str(sp).should.eql("Speaker(name=awesomesauce, actions=OrderedDict([(u'do_this', partial:for_decorator), (u'do_that', partial:for_decorator)]), total_hooks=0)")


def test_listeners_hear_to_speakers():
    "Listeners should hear to speaker"
    before = Speaker('before', ['file_created'])

    @before.file_created
    def obeyer(event, node):
        node.received_successfully(True)

    node = Mock()
    node.path = 'foo/bar'
    before.shout('file_created', node)
    node.received_successfully.assert_called_once_with(True)


def test_speaker_keys():
    "Speakers should have keys"

    def obeyer(speaker, node):
        node.path.should.equal('foo/bar')

    sp = Speaker('before', ['file_created'])
    sp.file_created(obeyer).key.should.equal(
        'before:file_created[tests.test_signal_system:obeyer:87]')


def test_listeners_with_exceptions():
    "Listeners by default raise exceptions"
    before = Speaker('on', ['file_created'])

    @before.file_created
    def obeyer(event):
        raise IOError("You got served")

    before.shout.when.called_with('file_created').should.throw(
        IOError, "You got served")


def test_listeners_returning_values():
    "Listeners by default raise exceptions"
    before = Speaker('on', ['file_created'])

    calls = []

    @before.file_created
    def obeyer1(event):
        calls.append(event)

    @before.file_created
    def obeyer2(event):
        calls.append(event)
        return len(calls)

    before.file_created.shout().should.equal(2)


def test_listeners_with_exception_handler():
    "Speakers can have custom exception handlers"
    before = Speaker('on', ['file_created'])

    ensure = Mock()

    @before.exception_handler
    def handler(speaker, exception, args, kwargs):
        speaker.should.equal(before)
        exception.should.be.an(IOError)
        args.should.be.a(tuple)
        args.should.equal(("YAY",))
        kwargs.should.be.a(dict)
        kwargs.should.equal({'awesome': True})
        ensure.was_called()

    @before.file_created
    def obeyer(event, *args, **kwargs):
        args.should.be.a(tuple)
        args.should.equal(("YAY",))
        kwargs.should.be.a(dict)
        kwargs.should.equal({'awesome': True})
        raise IOError("You got served")

    before.shout('file_created', "YAY", awesome=True)
    ensure.was_called.assert_called_once_with()


def test_2_listeners_with_exception_handler():
    "It's forbidden to have 2 exception handlers"
    before = Speaker('on', ['file_created'])

    @before.exception_handler
    def handler(speaker, exception, args, kwargs):
        pass

    before.exception_handler.when.called_with(lambda: None).should.throw(
        RuntimeError, 'Attempt to register Function(name="<lambda>", lineno="161", filename="tests/test_signal_system.py") as an exception_handler for Speaker(name=on, actions=OrderedDict([(u\'file_created\', partial:for_decorator)]), total_hooks=0), but it already has <bound method Speaker.exception_handler of Speaker(name=on, actions=OrderedDict([(u\'file_created\', partial:for_decorator)]), total_hooks=0)> assigned')


def test_unregister_listeners():
    "It should be possible to unregister listeners"

    when = Speaker('when', ['ready'])

    @when.ready
    def dont_call_me(event):
        raise RuntimeError("You got served")

    @when.ready
    def do_something(event):
        raise RuntimeError("You got served")

    @when.ready
    def do_something_else(event):
        event.hooks['ready'].should.have.length_of(1)

    when.unplug('ready', dont_call_me)
    when.ready.unplug(do_something)
    when.ready.shout()


def test_unregister_all_listeners():
    "It should be possible to unregister all listeners at once"

    when = Speaker('when', ['ready'])

    @when.ready
    def dont_call_me(event):
        raise RuntimeError("You got served")

    @when.ready
    def do_something(event):
        raise RuntimeError("You got served")

    @when.ready
    def do_something_else(event):
        event.hooks['ready'].should.have.length_of(1)

    when.hooks['ready'].should.have.length_of(3)
    when.release('ready')
    when.hooks['ready'].should.be.empty
