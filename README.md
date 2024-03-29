# rstoys

Cross platform lightweight python library to help creating interactive real-time, remote controlled toys (typically based on Raspberry Pi). Library provides set of independent reusable modules described below.

Source code can be found at [https://github.com/rstgh/rstoys](https://github.com/rstgh/rstoys)

Please use pip to install this package:

```sh
pip install rstoys
pip install flask # if you plan to use rstoys.touchy
pip install arcade # if you plan to use rstoys.maps
```

## rstoys.realtime

Realtime module provides some functions related to realtime main loop processing functionality.
All time or interval values are expressed in `seconds`.

### `realtime.loop(callback, update_interval=0.020)`

this function enters an infinite loop calling your `callback` function with two parameters `(elapsed_time, delta_time)` at specified update_interval.

- `elapsed_time` - is an absolute elapsed time in seconds starting with 0 at the beginning
- `delta_time` - is a delta time in seconds since last execution of your callback function, can be used to scale your robot actions to make it more cpu load independent.

It is an equivalent of:

```python
while True:
    callback(elapsed_time, delta_time)
    sleep(update_interval)
```

Using the realtime.loop() has an advantage that it dynamically adjusts the sleep time to compensate for the time spent in your callback, trying to provide as stable `callback` calling interval as possible.

So far the only way to exit this loop is by pressing `CTRL+C`.

Example usage:

```python
from rstoys import realtime

def update(elapsed_time, delta_time):
    print("elapsed=%08.3fs | dt=%06.3fms" % (elapsed_time, delta_time * 1000))

# initialize my hardware here

# enter the loop that calls update function every 100ms
realtime.loop(update, 0.1)
```

### `realtime.Interval(interval = 1.0)`

Simplifies periodic execution with given interval.

Usage:

```python
from rstoys import realtime

every1s = realtime.Interval(1.0)
every3s = realtime.Interval(3.0)

def update(elapsed_time, delta_time):

    print("Every 100ms")
    
    if every1s.should(delta_time):
        print("Once per second")
        
    if every3s.should(delta_time):
        print("Once every 3 seconds")
        

realtime.loop(update, 0.1)
```  

### `realtime.Mapper(value)`

Provides fluent interface to map given input value via following methods, all methods are symmetrical for negative values.

`.copy()` # creates a copied instance

`.value()` # returns final value

`.add(o = 0.0)` # value = value + o

`.mul(s = 1.0)` # value = value * s

`.trim(min = -1.0, max = -1.0)` # trims a value into given min max range

`.exp(e = math.e)` # value = e ^ value

`.pow(p = 1.0)` # value = value ^ p

`.gap(g = 0.0)` # returns value if value <= -g or value >= g else 0.0

`.gaplin(g = 0.0, m = 1.0)` # similar to gap, but then over g interpolates linearly from 0 to m


## rstoys.touchy

This module provides a mobile friendly web interface with basic touch stick controller for (x, y) values that can be easily read in your python code for controlling your robot.

### `touchy.start_server(port=80)`

Starts simple flask webserver instance on a given port that is running in a separate thread this webserver can be reached:

Locally `http://127.0.0.1:<port>/` or remotely by using your IP address of the RPi instead of 127.0.0.1

### `touchy.stop_server()`

Stops touchy webserver and terminates its thread.

### `(x, y) = touchy.controller.getStick()`

This function returns (x, y) tupple representing touch stick controller position.
values are in range of `[-1...0...1]`.

Example code:

```python
from rstoys import touchy
from rstoys import realtime

def update(elapsed_time, delta_time):
    (x, y) = touchy.controller.getStick()
    print("elapsed=%08.3fs | dt=%06.3fms | X=%6.3f | Y=%6.3f" % (elapsed_time, delta_time * 1000, x, y))

touchy.start_server(port=5000)
realtime.loop(update)
touchy.stop_server()
```
... then open `http://<YOUR-IP-ADDRESS>:5000/` in your mobile browser and move the on-screen stick to see the changes.

## rstoys.geo

This module provides simple geo location related functionality to help building location aware navigation based on bearing adjustments. It properly calculates absolute bearing between two geo locations, provides correct `average_bearing()` method as well as simple `WebMercatorProjection` implementation. 

Please check out [example-geo.py](https://github.com/rstgh/rstoys/blob/master/example-geo.py) file for more usage examples.  

### `geo.LatLon(lat, lon)`

geo location point with latitude and longitude

```python
munich = geo.LatLon(48.133333, 11.566667)
# accepts also lat lon as string comma separated
munich = geo.LatLon('48.133333,11.566667')
```


## rstoys.maps

Provides basic open-maps window rendering using arcade framework to provide visualization of geo data.

Please check out [example-maps-sailing.py](https://github.com/rstgh/rstoys/blob/master/example-maps-sailing.py) file for some usage examples.  
 

### Development

Want to contribute? Just send me an e-mail: `rstechnology@gmail.com`

## License

MIT

Use at your own risk and have fun.
