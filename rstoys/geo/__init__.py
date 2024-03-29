
import math

name = "geo"


class LatLon(object):

    def __init__(self, lat, lon=None):

        if lon is None and type(lat) == str:
            a = lat.split(",")
            if len(a) == 2:
                lat = a[0].strip()
                lon = a[1].strip()
            else:
                raise Exception("Invalid LatLon input: " + str(lat))

        self.lat = float(lat)
        self.lon = float(lon)

    def __str__(self):
        return "%.7f,%.7f" % (self.lat, self.lon)

    def copy(self):
        return LatLon(self.lat, self.lon)

    def bearing(self, latlon):
        return bearing(self, latlon)

    def distance(self, latlon):
        """ returns distance in meters """
        lat1 = math.radians(self.lat)
        lon1 = math.radians(self.lon)
        lat2 = math.radians(latlon.lat)
        lon2 = math.radians(latlon.lon)
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return 6373000.0 * c

    def move(self, heading, distance):

        latdeg = 111320  # meters per lat degree
        londeg = math.cos(math.radians(self.lat)) * 111320

        r = math.radians(heading)
        self.lat = self.lat + math.cos(r) * distance / latdeg
        self.lon = self.lon + math.sin(r) * distance / londeg

        return self


class WebMercatorProjection:

    def __init__(self, zoom=0):
        self.zoom = 0
        self.zoom_factor = 0
        self.set_zoom(zoom)

    def set_zoom(self, zoom):
        self.zoom = zoom
        self.zoom_factor = (256.0 * math.pow(2.0, self.zoom)) / (2.0 * math.pi)

    def project(self, lat, lon=None):
        """
        convert lat,lon into x,y in our projection
        """
        if lon is None:  # so we can also pass LatLon object
            lon = lat.lon
            lat = lat.lat

        x = self.zoom_factor * (math.radians(lon) + math.pi)
        y = self.zoom_factor * (math.pi - math.log(math.tan(math.pi / 4.0 + math.radians(lat) / 2.0)))
        return x, y


def xy_to_bearing(x, y):
    """
    converts coordinates x, y into absolute bearing in range [0, 360)
    for example (x=0, y=1) => 0, (x=1, y=0) => 90, (x=0, y=-1) => 180, (x=-1, y=0) => 270
    """
    if x == 0.0 and y == 0.0:
        return None

    b = math.degrees(math.atan2(x, y))
    b = b if b >= 0.0 else b + 360.0
    b = b if b < 360.0 else b - 360.0
    return b


def bearing(latlon1, latlon2):
    """
    return bearing angle in degrees between (latlon1) to (latlon2)
    0 = North, 90 = East, -90 = West, 180 = South
    todo: fix problem when wrapping lat/lon ex: alaska > japan returns currently 97.2814
    """
    x1, y1 = bearing_projection.project(latlon1)
    x2, y2 = bearing_projection.project(latlon2)

    return xy_to_bearing(x2 - x1, y1 - y2)  # flipped y as (0,0) is left-top and (256,256) right-bottom


def normalize_bearing(b):
    """ normalizes bearing into [0...360) range, so -1 becomes 359 and 721 will return 1 """
    while b < 0:
        b = b + 360.0
    while b >= 360.0:
        b = b - 360.0
    return b


def diff_bearing(b1, b2):
    """ calculate bearing difference between b2 and b1, returns angle difference in range (-179 ... 180] """
    d = normalize_bearing(b2) - normalize_bearing(b1)
    d = d + 360.0 if d <= -180.0 else d
    d = d - 360.0 if d > 180.0 else d
    return d


def average_bearing(bearings):
    """
    calculate an average bearing from a list of bearing readouts
    properly handling an the the edge cases: [350, 10] returns 0, [90, 270] returns None etc...
    """
    if len(bearings) > 0:

        xs = []
        ys = []

        for b in bearings:
            xs.append(math.sin(math.radians(b)))
            ys.append(math.cos(math.radians(b)))

        ax = sum(xs) / len(xs)
        ay = sum(ys) / len(ys)

        if (round(ax, 8) != 0.0) or (round(ay, 8) != 0.0):
            return xy_to_bearing(ax, ay)


class CourseManager(object):

    def __init__(self, max_samples=10, max_interval=10):
        self.max_samples = max(2, max_samples)
        self.max_interval = max(2, max_interval)  # todo: use it to filter active locations within max_interval time
        self.locations = []

    def __str__(self):
        return "Bearing %.1f deg" % (self.get_bearing()) if len(self.locations) > 1 else "Bearing None"

    def clear(self):
        self.locations = []

    def add_location(self, latlon):
        timestamp = 0
        self.locations.append((latlon, timestamp))
        while len(self.locations) > self.max_samples:
            del self.locations[0]

    def get_last_location(self):
        return self.locations[-1][0] if len(self.locations) > 0 else None

    def get_bearing(self):

        # we need at least 2 locations to have a bearing
        if len(self.locations) < 2:
            return

        bearings = []
        for i in range(1, len(self.locations)):
            b = bearing(self.locations[i-1][0], self.locations[i][0])
            if b is not None:
                bearings.append(b)

        return average_bearing(bearings)


class WayPoints(object):

    def __init__(self, completion_radius=20):
        self.radius = completion_radius
        self.points = []

    def append(self, waypoint):
        """ append new waypoint to the list """
        self.points.append([waypoint, False])

    def completed(self):
        """ returns True if all waypoints have been completed """
        for e in self.points:
            if not e[1]:
                return False
        return True

    def clear(self):
        """ clears all the waypoints """
        self.points = []

    def reset(self):
        """ sets the state of all waypoints to not-completed """
        for e in self.points:
            e[1] = False

    def target(self, location):
        """ returns next waypoint (target) to follow and checks if it was reached """
        while not self.completed():

            e = None
            for e in self.points:
                if not e[1]:
                    break
            if e is None:
                return None

            # check if current target is completed
            if location.distance(e[0]) <= self.radius:
                e[1] = True  # mark as completed
            else:
                return e[0]

        return None

    def progress(self):
        """ simpliest completion progress, todo: use distance for beter estimation """
        n = len(self.points)
        c = 0
        for e in self.points:
            if e[1]:
                c = c + 1

        return float(c * 100.0) / float(max(1, n))


class WayPointsBearingTracker(object):

    def __init__(self, waypoints, samples=2):
        self.path = waypoints
        self.manager = CourseManager(samples) # course manager averaging 2 last location samples

    def get_bearing_error(self, location):

        location = location.copy()

        self.manager.add_location(location)

        if not self.path.completed():

            target = self.path.target(location)
            if target is not None:

                target_bearing = location.bearing(target)
                course_bearing = self.manager.get_bearing()

                if course_bearing is not None and target_bearing is not None:
                    return diff_bearing(course_bearing, target_bearing)


bearing_projection = WebMercatorProjection(10)
