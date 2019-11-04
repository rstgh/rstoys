
from rstoys import realtime

every1s = realtime.Interval(1.0)
every3s = realtime.Interval(3.0)
every5s = realtime.Interval(5.0)

counter = 0

def control(elapsed, dt):

    global counter

    counter = counter + 1

    print("%8d" % (counter), end="")

    if every1s.should(dt):
        print(" : 1", end="")

    if every3s.should(dt):
        print(" : 3", end="")

    if every5s.should(dt):
        print(" : 5", end="")

    print("")


# enter infinite loop (CTRL+C to end)
# calling control every 100 milliseconds
realtime.loop(control, 0.1)

