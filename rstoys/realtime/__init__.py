
import time
import signal

name = "realtime"


def seconds():
    return time.time()


run_loop = None


def signal_handler(sig, frame):
    global run_loop
    run_loop = False


def loop(control, update_interval=0.02):

    elapsed = 0
    lt = seconds()

    time.sleep(update_interval)

    global run_loop

    if run_loop is None:
        signal.signal(signal.SIGINT, signal_handler)

    run_loop = True

    while run_loop:

        ct = seconds()  # current time
        dt = ct - lt  # real delta time
        lt = ct

        control(elapsed, dt)

        # calculate extra required sleep time
        # compensating for control routine duration
        sleeptime = update_interval - (seconds() - ct)
        if sleeptime > 0:
            time.sleep(sleeptime)

        elapsed = elapsed + dt
