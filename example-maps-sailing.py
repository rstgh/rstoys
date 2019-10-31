
from rstoys.geo import *
from rstoys.maps import *


class Boat(MapLayer):

    def __init__(self, position=LatLon(0,0), heading=0, speed=0):

        super().__init__()

        self.position = position.copy()
        self.heading = heading
        self.speed = speed

        self.rudder = 0

        self.texture = self.load_texture("assets/boat-64.png")

        self.t = 0
        self.trail = []

        self.tracker = WayPointsBearingTracker(path, 2)


    def render(self, et, dt):

        # draw trailing dots
        for p in self.trail:
            x, y = self.map.project(p)
            arcade.draw_point(x, y, (255,0,0), 6)

        s = "%s | R=%.1f°" % (str(self.position), self.rudder)
        arcade.draw_text(s, self.map.wh - 40, self.map.hh, (0,0,0,192), 18)

        # draw the boat
        self.draw_texture(self.texture, self.position, -self.heading)

        # simulate boat physics
        r = math.radians(self.rudder)
        df = math.cos(r)
        hf = math.sin(r)
        self.position.move(self.heading, df * dt * 0.277778 * self.speed)
        self.heading = self.heading + hf * dt * self.speed / 2

        # execute control every interval time
        interval = 0.3
        self.t = self.t + dt
        if self.t > interval:
            self.t = 0
            self.control()


    def control(self):

        # append a trailing dot
        self.trail.append(self.position.copy())

        # calculate bearing error and steer the rudder
        error = self.tracker.get_bearing_error(self.position)
        if error is not None:
            self.rudder = max(-30, min(30, error))

        if self.tracker.path.completed():
            self.rudder = 0
            self.speed = 0
            print("Completed the path...")


swanage = LatLon(50.607915, -1.950507)

path = WayPoints(50) # waypoints with 50m radius
path.append(LatLon(50.608124, -1.946433))
path.append(LatLon(50.609949, -1.943380))
path.append(LatLon(50.611304, -1.950127))
path.append(LatLon(50.610208, -1.952272))
path.append(LatLon(50.614055, -1.954800))
path.append(LatLon(50.608348, -1.954082))


boat = Boat(swanage, 45, 160) # boat at swanage, initially with 45 heading, and speed 160 km/h

map = Map(1400, 800)

map.set_center(swanage.copy().move(0, 200)).set_zoom(16)

markers = MapMarkerLayer()
markers.add_marker(swanage)
markers.add_marker(LatLon(50.609346, -1.949220))
markers.add_marker(LatLon(50.607525, -1.944220))
markers.add_marker(LatLon(50.611611, -1.963500))  # parking

map.add_layer(wikimedia_tile_layer)
# map.add_layer(watercolor_tile_layer)

map.add_layer(markers)
map.add_layer(MapWayPointsLayer(path))
map.add_layer(boat)

map.run()
