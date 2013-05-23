# Installing

```bash
pip install speakers
```

# declare an event

Speaker takes a `name` and a list of `events`,

```python
import sure
from mock import Mock
from speakers import Speaker

after = Speaker('after', ['getting_sql_results'])
```

Another example, let's say you are building a DOM API

```python
on = Speaker('on', ['ready', 'loading'])

@on.ready
def show_ready(event, dom):
    print "The DOM is ready!"
    print "The page title is", dom.cssselect("title")[0].text

@on.loading
def show_loading(event):
    print "Loading DOM, please wait"

on.loading.shout()


fake_dom = Mock()
fake_dom.cssselect.return_value = ["A cool title!"]

on.loading.shout()
on.ready.shout(fake_dom)
```


# declare as many listeners as you want

```python
@after.getting_sql_results
def print_results(event, results):
    print "Doing query results"
    print
    for r in results:
        print "Query result", r
```

# emit the event

```python
results = ["res1", "res2", "res3"]
after.getting_sql_results.shout(results)
```

# declare exception handlers

Speakers allows you to declare a single exception handler function per speaker instance.

You can decorate a function that must take 4 arguments:

* `event`: the Speaker instance
* `exc`: the exception instance, you could use the [`traceback`](http://docs.python.org/2/library/traceback.html#traceback.format_exc) module to print the full exception trace if you want.
* `args` a tuple containing the arguments passed to the callback which raised the current exception
* `kwargs` a dictionary containing the keyword arguments passed to the callback which raised the current exception.

Example:

```python
on = Speaker('on', ['ready', 'loading'])

@on.exception_handler
def print_exception(event, exc, args, kwargs):
    exc.should.be.a(TypeError)

    print exc

@on.loading
def show_loading(event):
    # this should raise a TypeError
    range(10) + {'foo': 'bar'}

on.loading.shout()
```

# unplugging events


### a single event callback

```python
when = Speaker('when', ['ready'])

@when.ready
def never_called(event):
    raise IOError("BOOM")

@when.ready
def called_once(event):
    assert len(event.hooks["ready"]) == 1


when.ready.unplug(never_called)

# calls the function `called_once`
when.ready.shout()
```

### unplugging an action of a speaker

```python
when = Speaker('when', ['ready'])

@when.ready
def never_called(event):
    raise IOError("BOOM")

@when.ready
def called_once(event):
    assert len(event.hooks["ready"]) == 1


when.release('ready')

# nothing will happen
when.ready.shout()
```


### unplugging all actions of a speaker

```python
when = Speaker('when', ['ready', 'loading'])

@when.ready
def dont_call_me(event):
    raise RuntimeError("You got served")

@when.loading
def do_something(event):
    raise RuntimeError("You got served")

when.release()

# nothing will happen
when.ready.shout()
```


### unplugging all actions of all existing speakers

```python
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

Speaker.release_all()

when.ready.shout()
```
