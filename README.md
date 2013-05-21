# Simple usage


### declare an event

```python
from speakers import Speaker

after = Speaker('after', ['getting_sql_results'])
```

### declare as many listeners as you want

```python
@after.getting_sql_results
def print_results(event, results):
    print "Doing query results"
    print
    for r in results:
        print "Query result", r
```

### emit the event

```python
results = ['res1', 'res2', 'res3']
after.getting_sql_results.shout(results)
```

# A little history

One of the most efficient ways to extend a piece of software is to use a signal system.

Imagine the components of a software architecture as being students in
a school, and the school being a framework.

Speakers throughout the school facilities emit alerts to the students
so they know if one of them has to stop doing what is doing to
actually go to the principal's room.

Speakers has emerged from [markment's](http://gabrielfalcao.github.io/markment) but was slightly copied from [lettuce's](http://lettuce.it) codebase.
