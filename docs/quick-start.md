# Installing

```bash
pip install speakers
```

# declare an event

```python
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
results = connection.query("SELECT * FROM blabla")
after.getting_sql_results.shout(results)
```
