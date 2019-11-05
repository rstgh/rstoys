
from rstoys.geo import *
from rstoys.maps import *
from rstoys.realtime import Interval


class Boat(MapLayer):

    def __init__(self, position=LatLon(0,0), heading=0, speed=0):

        super().__init__()

        self.position = position.copy()
        self.heading = heading
        self.speed = speed
        self.rudder = 0
        self.texture = self.load_texture("assets/boat-64.png")

    def render(self, et, dt):

        # draw the boat texture
        self.draw_texture(self.texture, self.position, -self.heading)

        # simulate boat physics
        r = math.radians(self.rudder)
        df = math.cos(r)
        hf = math.sin(r)
        self.position.move(self.heading, df * dt * 0.277778 * self.speed)
        self.heading = self.heading + hf * dt * self.speed / 2


class TrackingBoat(Boat):

    def __init__(self, position=LatLon(0,0), heading=0, speed=0):

        super().__init__(position, heading, speed)

        self.update_interval = Interval(0.2)
        self.tracker = WayPointsBearingTracker(path, 2)
        self.trail = None


    def render(self, et, dt):

        if self.trail is None:
            self.trail = arcade.ShapeElementList()
        else:
            self.trail.draw()

        super().render(et, dt)

        # execute control every interval time
        if self.update_interval.should(dt):
            self.control()


    def control(self):

        # append a trailing dot
        if self.trail is not None:
            self.trail.append(arcade.create_ellipse_filled(*self.map.project(self.position), 2, 2, (128,0,0,64), 0, 6))

        # calculate bearing error and steer the rudder
        error = self.tracker.get_bearing_error(self.position)
        if error is not None:
            self.rudder = max(-30, min(30, error))

        if self.tracker.path.completed():
            print("Completed the path... Starting over...")
            self.tracker.path.reset()


swanage = LatLon(50.607915, -1.950507)

path = WayPoints(50) # waypoints with 50m radius
path.append(LatLon(50.608124, -1.946433))
path.append(LatLon(50.609949, -1.943380))
path.append(LatLon(50.611304, -1.950127))
path.append(LatLon(50.610208, -1.952272))
path.append(LatLon(50.614055, -1.954800))
path.append(LatLon(50.608348, -1.954082))


boat = TrackingBoat(swanage, 45, 160) # boat at swanage, initially with 45 heading, and speed 160 km/h

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


# five extra funny constant speed boats running in circles
c = map.center.copy().move(68, 800) # c is 800 meters at 68 deg from map center
n = 5
for i in range(0, n):
    a = 360 * i / n
    b = Boat(c.copy().move(a, 150), a, 200)
    b.rudder = 20
    map.add_layer(b)


map.run()
