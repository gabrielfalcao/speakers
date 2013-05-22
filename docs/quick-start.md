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

# unplugging an event

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


# unplugging all events

```python
when = Speaker('when', ['ready'])

@when.ready
def never_called(event):
    raise IOError("BOOM")

@when.ready
def called_once(event):
    assert len(event.hooks["ready"]) == 1


when.ready.release()

# nothing will happen
when.ready.shout()
```
