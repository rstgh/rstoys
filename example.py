
from rstoys import touchy
from rstoys import realtime


def control(elapsed, dt):
    (x, y) = touchy.controller.getStick()
    print("elapsed=%08.3fs | dt=%06.3fms | X=%6.3f | Y=%6.3f" % (elapsed, dt * 1000, x, y))


# start http server
touchy.start_server(port=5000)

# enter infinite loop (CTRL+C to end)
realtime.loop(control)

# stop http server
touchy.stop_server()
