# Installing

```bash
pip install speakers
```

# declare an event

```python
import sure
from speakers import Speaker

after = Speaker('after', ['getting_sql_results'])
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

# unplugging events


## a single event callback

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

## unplugging an action of a speaker

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


## unplugging all actions of a speaker

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


## unplugging all actions of all existing speakers

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
