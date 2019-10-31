
from rstoys.geo import *
from rstoys.maps import *


path = WayPoints()

path.append(LatLon(50.608124, -1.946433))
path.append(LatLon(50.609949, -1.943380))
path.append(LatLon(50.611304, -1.950127))
path.append(LatLon(50.610208, -1.952272))
path.append(LatLon(50.614055, -1.954800))
path.append(LatLon(50.608348, -1.954082))



estimator = BearingEstimator(2)


class Boat(MapLayer):

    def __init__(self):
        super().__init__()

        self.position = LatLon(50.607915, -1.950507)
        self.heading = 45

        self.rudder = 0
        self.speed = 150

        self.texture = arcade.load_texture("assets/boat-64.png")
        self.t = 0

        self.drop = []

    def render(self, et, dt):

        x, y = self.map.project(self.position)
        arcade.draw_texture_rectangle(x, y, self.texture.width, self.texture.height, self.texture, -self.heading)

        r = math.radians(self.rudder)
        df = math.cos(r)
        hf = math.sin(r)

        self.position.move(self.heading, df * dt * 0.277778 * self.speed)
        self.heading = self.heading + hf * dt * self.speed / 2

        s = "%s | R=%.1f°" % (str(self.position), self.rudder)
        arcade.draw_text(s, self.map.wh - 40, self.map.hh, (0,0,0,192), 18)

        for p in self.drop:
            x, y = self.map.project(p)
            arcade.draw_point(x, y, (255,0,0), 6)

        self.t = self.t + dt

        if self.t < 0.3:
            return

        self.t = 0


        if path.completed():
            self.speed = 0
            self.rudder = 0
            print("DONE")
            return

        location = LatLon(self.position.lat, self.position.lon)

        self.drop.append(location)

        estimator.add_location(location)
        target = path.target(location)

        if target is None:
            return

        target_bearing = location.bearing(target)
        course_bearing = estimator.get_bearing()

        if course_bearing is None or target_bearing is None:
            return

        error_bearing = diff_bearing(course_bearing, target_bearing)

        r = error_bearing

        if r > 30:
            r = 30
        if r < -30:
            r = -30

        self.rudder = r

        print(
            "loc = (%s) | target = (%s) | target_b = %5.1f | course_b = %5.1f | error_b = %5.1f | progress = %3.0f%%"
            % (location, target, target_bearing, course_bearing, error_bearing, path.progress())
        )






boat = Boat()


map = Map(1400, 800)

swanage = LatLon(50.607915, -1.950507)

map.set_center(LatLon(50.609915, -1.950507)).set_zoom(16)
map.add_layer(wikimedia_tile_layer)

markers = MapMarkerLayer()
map.add_layer(markers)
map.add_layer(MapWayPointsLayer(path))
map.add_layer(boat)


markers.add_marker(swanage)
markers.add_marker(LatLon(50.609346, -1.949220))
markers.add_marker(LatLon(50.607525, -1.944220))
markers.add_marker(LatLon(50.611611, -1.963500))  # parking

#chiemsee = LatLon(47.8821879, 12.4588497)
#map.set_center(chiemsee).set_zoom(13)
#markers.add_marker(LatLon(47.871746, 12.427946))
#markers.add_marker(LatLon(47.836403, 12.374442))  # Schollkopf



#map.set_center(LatLon(48.1026031,11.6333739)).set_zoom(4) #  home

map.run()
