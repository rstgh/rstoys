
import math


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

    def bearing(self, lat1, lon1, lat2, lon2):
        """
        return bearing angle in degrees between (lat1, lon1) to (lat2, lon2)
        0 = North, 90 = East, -90 = West, 180 = South
        todo: fix problem when wrapping lat/lon ex: alaska > japan returns currently 97.2814
        """
        if lat1 == lat2 and lon1 == lon2:
            return None

        x1, y1 = self.project(lat1, lon1)
        x2, y2 = self.project(lat2, lon2)

        return xy_to_bearing(x2-x1, y1-y2)  # flipped y as (0,0) is left-top and (256,256) right-bottom


def xy_to_bearing(x, y):
    """
    converts coordinates x, y into absolute bearing in range [0, 360)
    for example (x=0, y=1) => 0, (x=1, y=0) => 90, (x=0, y=-1) => 180, (x=-1, y=0) => 270
    """
    b = math.degrees(math.atan2(x, y))
    b = b if b >= 0.0 else b + 360.0
    b = b if b < 360.0 else b - 360.0
    return b


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

        if (round(ax, 6) != 0.0) or (round(ay, 6) != 0.0):
            return xy_to_bearing(ax, ay)


class BearingEstimator(object):

    def __init__(self, max_samples=10, max_interval=10, projection=None):
        self.max_samples = max(2, max_samples)
        self.max_interval = max(2, max_interval)  # todo: use it to filter active locations within max_interval time
        self.projection = projection if projection else WebMercatorProjection(10)
        self.locations = []

    def clear(self):
        self.locations = []

    def add_location(self, latlon):
        timestamp = 0
        self.locations.append((latlon, timestamp))
        while len(self.locations) > self.max_samples:
            del self.locations[0]

    def last_location(self):
        return self.locations[-1][0] if len(self.locations) > 0 else None

    def get_bearing(self):

        # we need at least 2 locations to have a bearing
        if len(self.locations) < 2:
            return

        bearings = []
        for i in range(1, len(self.locations)):
            p1 = self.locations[i-1][0]
            p2 = self.locations[i][0]
            b = self.projection.bearing(p1.lat, p1.lon, p2.lat, p2.lon)
            if b is not None:
                bearings.append(b)

        return average_bearing(bearings)
