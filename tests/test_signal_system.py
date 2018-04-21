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

from mock import Mock
from speakers.bus import Function, Speaker
from speakers.bus import _function_matches


def test_function_matches_compares_with_abs_path():
    u"speakers.bus._function_matches() should compare callback filenames with abspath"

    class fakecallback1:
        class func_code:
            co_filename = "/some/path/to/some/../file.py"
            co_firstlineno = 1

        class __code__(func_code):
            pass

    class fakecallback2:
        class func_code:
            co_filename = "/some/path/to/file.py"
            co_firstlineno = 1

        class __code__(func_code):
            pass

    assert _function_matches(fakecallback1, fakecallback2), \
        'the callbacks should have matched'


def test_function_as_string():
    "Function#as_string"

    def testing():
        pass

    s = Function(testing)

    str(s).should.equal('Function(name="testing", lineno="59", filename="tests/test_signal_system.py")')


def test_function_repr():
    "repr(#Function)"

    def testing():
        pass

    s = Function(testing)

    repr(s).should.equal('Function(name="testing", lineno="70", filename="tests/test_signal_system.py")')


def test_speaker_with_wrong_parameter():
    "Speaker takes list of strings"

    Speaker.when.called_with("Testing", "foo").should.throw(
        TypeError, "actions must be a list of strings. Got 'foo'")


def test_speaker_as_string():
    "Speaker as string"

    sp = Speaker("AwesomeSauce", ['do this', 'do that'])
    str(sp).should.eql("Speaker(name=awesomesauce, actions=OrderedDict([('do_this', partial:for_decorator), ('do_that', partial:for_decorator)]), total_hooks=0)")


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
        'before:file_created[tests.test_signal_system:obeyer:109]')


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
        RuntimeError, 'Attempt to register Function(name="<lambda>", lineno="183", filename="tests/test_signal_system.py") as an exception_handler for Speaker(name=on, actions=OrderedDict([(\'file_created\', partial:for_decorator)]), total_hooks=0), but it already has <bound method Speaker.exception_handler of Speaker(name=on, actions=OrderedDict([(\'file_created\', partial:for_decorator)]), total_hooks=0)> assigned')


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


def test_unregister_all_listeners_from_action():
    "It should be possible to unregister all listeners under an action at once"

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


def test_unregister_all_listeners_from_speaker():
    "It should be possible to unregister all listeners of a speaker at once"

    when = Speaker('when', ['ready', 'loading'])

    @when.ready
    def dont_call_me(event):
        raise RuntimeError("You got served")

    @when.loading
    def do_something(event):
        raise RuntimeError("You got served")

    when.hooks['ready'].should.have.length_of(1)
    when.hooks['loading'].should.have.length_of(1)
    when.release()
    when.hooks['ready'].should.be.empty
    when.hooks['loading'].should.be.empty


def test_unregister_all_listeners():
    "It should be possible to unregister all listeners of all speakers"

    when = Speaker('when', ['ready', 'loading'])
    after = Speaker('after', ['ready', 'loading'])

    @when.ready
    def dont_call_me(event):
        raise RuntimeError("You got served")

    @when.loading
    def do_something(event):
        raise RuntimeError("You got served")

    @after.ready
    def after_all(event):
        raise RuntimeError("You got served")

    @after.loading
    def loading_after(event):
        raise RuntimeError("You got served")

    when.hooks['ready'].should.have.length_of(1)
    when.hooks['loading'].should.have.length_of(1)
    after.hooks['ready'].should.have.length_of(1)
    after.hooks['loading'].should.have.length_of(1)
    Speaker.release_all()
    when.hooks['ready'].should.be.empty
    when.hooks['loading'].should.be.empty
    after.hooks['ready'].should.be.empty
    after.hooks['loading'].should.be.empty
