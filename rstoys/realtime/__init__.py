
import time
import signal
import logging
import math

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

        try:
            control(elapsed, dt)
        except Exception as ex:
            logging.error(ex)
        except:
            logging.error("Fatal exception in render()")

        # calculate extra required sleep time
        # compensating for control routine duration
        sleeptime = update_interval - (seconds() - ct)
        if sleeptime > 0:
            time.sleep(sleeptime)

        elapsed = elapsed + dt


class PID(object):

    def __init__(self, kp=1.0, ki=0.0, kd=0.0):

        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.integral = 0
        self.last_error = 0

        self.integral_min = None
        self.integral_max = None
        self.output_min = None
        self.output_max = None

    def set_output_limits(self, min, max):
        self.output_min = min
        self.output_max = max
        return self

    def set_integral_limits(self, min, max):
        self.integral_min = min
        self.integral_max = max
        return self

    def reset(self):
        self.integral = 0
        self.last_error = 0
        return self

    def compute(self, input, setpoint, dt=1.0):

        error = setpoint - input
        self.integral = self.integral + self.ki * error * dt

        # limit integral
        self.integral = self.integral_min if (self.integral_min is not None and self.integral < self.integral_min) else self.integral
        self.integral = self.integral_max if (self.integral_max is not None and self.integral > self.integral_max) else self.integral

        output = self.kp * error + self.integral + ((self.kd * (error - self.last_error)) / dt)
        self.last_error = error

        # limit output
        output = self.output_min if (self.output_min is not None and output < self.output_min) else output
        output = self.output_max if (self.output_max is not None and output > self.output_max) else output

        return output


class Mapper(object):

    def __init__(self, v):
        self.v = v

    def value(self):
        return self.v

    def __str__(self):
        return "%.6f" % (self.v)

    def copy(self):
        return Mapper(self.v)

    def trim(self, min=None, max=None):
        self.v = min if min is not None and self.v < min else self.v
        self.v = max if max is not None and self.v > max else self.v
        return self

    def mul(self, s=1.0):
        self.v = self.v * s
        return self

    def add(self, o=0.0):
        self.v = self.v + o
        return self

    def pow(self, p=1.0):
        self.v = math.pow(self.v, p) if self.v >= 0 else -math.pow(abs(self.v), p)
        return self

    def exp(self, e=math.e):
        self.v = (math.pow(e, self.v)-1.0) / (e-1.0) if self.v >= 0 else -(math.pow(e, abs(self.v))-1.0) / (e-1.0)
        return self

    def gap(self, g=0.0):
        self.v = self.v if self.v <= -g or self.v >= g else 0.0
        return self

    def gaplin(self, g=0.0, m=1.0):
        s = -1.0 if self.v < 0.0 else 1.0
        v = abs(self.v)
        self.v = 0.0 if v <= g else s*(v-g)/(m-g)
        return self


class Interval(object):

    def __init__(self, interval=1):
        self.interval = interval
        self.passed = 0

    def should(self, dt):
        self.passed = self.passed + dt
        run = False
        if self.passed >= self.interval:
            run = True
            self.passed = 0
        return run


def square_period(elapsed, period=1.0):
    return int(math.floor(elapsed / (period/2.0))) % 2


def sinus_period(elapsed, period=1.0):
    return math.sin(elapsed * math.pi * 2.0 / period)
