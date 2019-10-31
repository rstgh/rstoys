
from rstoys.geo import *
from rstoys.maps import *


class AreaLayer(MapLayer):

    def __init__(self):
        super().__init__()

    def render(self, et, dt):

        # draw a darker circle with 100 meter radius
        self.draw_circle_filled(self.map.center, 100, (0,0,0,64))

        # draw a circle with 1 km radius
        self.draw_circle_outline(self.map.center, 200, (0,0,0,32))


elba = LatLon(42.7468184,10.2406661)

map = Map(1400, 800).set_center(elba).set_zoom(15)

map.add_layer(wikimedia_tile_layer)
map.add_layer(AreaLayer())

map.run()
