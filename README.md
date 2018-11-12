# strint
[![Build Status](https://travis-ci.org/skunkfrukt/strint.svg?branch=master)](https://travis-ci.org/skunkfrukt/strint)

A parser for numbers written as strings.

```python
from strint import strint

>>> strint("two octillion gigadollars and twelve cents")
{'dollars': 2000000000000000000000000000000000000, 'cents': 12}

>>> strint("twenty-three hours, fifty-nine minutes, 40 short seconds and 20 long seconds")
{'hours': 23, 'minutes': 59, 'short seconds': 40, 'long seconds': 20}

>>> strint("one, two, one two and three and four")
13
```
