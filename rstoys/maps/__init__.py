
import os
import time
import math
import tempfile
import urllib.request
import logging

from ..geo import *

name = "maps"

try:
    import arcade
except Exception as e:
    print("")
    print("rstoys.maps module depends on 'arcade' module for windowed rendering")
    print("http://arcade.academy/")
    print("")
    print("please install first: pip install arcade")
    print("")
    raise e


class LocalFileCache(object):
    cache_dir = tempfile.gettempdir()

    def set_cache_dir(dir):
        LocalFileCache.cache_dir = dir

    def get_full_path(relative):
        return os.path.join(LocalFileCache.cache_dir, relative)

    def ensure_dirs(path):
        os.makedirs(path, exist_ok=True)

    def file_exists(fname):
        return True if os.path.isfile(fname) else False


class SimpleArcade(object):

    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height

        self.center_x = width / 2.0
        self.center_y = height / 2.0

        self.started = time.time()

    def preload(self):
        pass

    def on_draw(self, delta_time):
        elapsed_time = time.time() - self.started
        arcade.start_render()
        try:
            self.render(elapsed_time, delta_time)
        except Exception as ex:
            logging.error(ex)
        except:
            logging.error("Fatal exception in render()")

    def render(self, elapsed_time, delta_time):
        pass

    def run(self):
        self.preload()

        arcade.open_window(self.width, self.height, "Animation")
        arcade.set_background_color(arcade.color.BLACK)
        self.started = time.time()
        arcade.schedule(self.on_draw, 1.0 / 80.0)
        arcade.run()
        arcade.close_window()


class MapLayer(object):

    def __init__(self):
        self.map = None
        pass

    def render(self, et, dt):
        pass

    def preload(self):
        pass

    def draw_circle_outline(self, latlon, radius, color=(128,128,128), width=1):
        x, y = self.map.project(latlon)
        rx, ry = self.map.project_radius(latlon, radius)
        arcade.draw_ellipse_outline(x, y, rx, ry, color, width)

    def draw_circle_filled(self, latlon, radius, color=(128,128,128)):
        x, y = self.map.project(latlon)
        rx, ry = self.map.project_radius(latlon, radius)
        arcade.draw_ellipse_filled(x, y, rx, ry, color, 0, 36)

    def load_texture(self, filename):
        return arcade.load_texture(filename)

    def draw_texture(self, texture, latlon, rotation = 0, scale = 1):
        x, y = self.map.project(latlon)
        arcade.draw_texture_rectangle(x, y, texture.width * scale, texture.height * scale, texture, rotation)


class MapMarkerLayer(MapLayer):

    def __init__(self):
        super().__init__()
        self.markers = []

    def add_marker(self, latlon):
        self.markers.append([latlon])

    def render(self, et, dt):
        n = 0
        for m in self.markers:
            (x, y) = self.map.project(m[0])

            bounce = 10 + 20 * abs(math.sin(et * 2 + n / 4))

            arcade.draw_line(x, y, x, y + bounce, (0, 0, 0, 64), 4)
            arcade.draw_circle_filled(x, y, 4, (0,0,0,128), 18)
            arcade.draw_circle_filled(x, y + bounce, 8, arcade.color.AMAZON, 18)

            n = n + 1


class MapWayPointsLayer(MapLayer):

    def __init__(self, waypoints):
        super().__init__()
        self.waypoints = waypoints

    def render(self, et, dt):

        segments = []
        for e in self.waypoints.points:
            segments.append(self.map.project(e[0]))

        arcade.draw_line_strip(segments, (0,40,150, 64), 3)

        for e in self.waypoints.points:
            (x, y) = self.map.project(e[0])
            completed = e[1]

            if completed:
                self.draw_circle_outline(e[0], self.waypoints.radius, (0,0,0, 16))
                arcade.draw_circle_filled(x, y, 4, (192, 64, 0), 18)
            else:
                self.draw_circle_filled(e[0], self.waypoints.radius, (0,0,0, 16))
                arcade.draw_circle_filled(x, y, 4, (0,60,90), 18)


class MapTileLayer(MapLayer):

    def __init__(self, name, url, min_zoom=0, max_zoom=20):

        super().__init__()

        self.name = name
        self.url = url
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.textures = {}

    def get_texture(self, z, x, y):

        n = math.pow(2, z) - 1
        if z < self.min_zoom or z > self.max_zoom or x < 0 or y < 0 or x > n or y > n:
            return None

        key = "t-%d-%d-%d" % (z, x, y)
        file = self.get_tile_filename(z, x, y)

        if key in self.textures:
            texture = self.textures[key]
        else:
            texture = arcade.load_texture(file)
            self.textures[key] = texture

        return texture

    def iterate(self):

        # center tile number
        cnx = math.floor(self.map.center_x / 256.0)
        cny = math.floor(self.map.center_y / 256.0)

        # center tile offset
        cox = self.map.center_x - (cnx * 256.0)
        coy = self.map.center_y - (cny * 256.0)

        # center tile position
        x0 = self.map.wh - cox + 128
        y0 = self.map.hh + coy - 128

        ox = max(0, math.ceil(self.map.width / 256.0 / 2.0))
        oy = max(0, math.ceil(self.map.height / 256.0 / 2.0))

        for ny in range(0 - oy, 1 + oy):
            for nx in range(0 - ox, 1 + ox):
                tx = x0 + (nx * 256.0)
                ty = y0 - (ny * 256.0)
                if tx+128 > 0 and ty+128 > 0 and tx-128 < self.map.width and ty-128 < self.map.height:
                    yield self.map.zoom, cnx + nx, cny + ny, tx, ty

    def preload(self):
        for e in self.iterate():
            z, x, y, tx, ty = e
            self.get_texture(z, x, y)

    def render(self, et, dt):

        for e in self.iterate():
            z, x, y, tx, ty = e
            texture = self.get_texture(z, x, y)
            if texture is not None:
                arcade.draw_texture_rectangle(tx, ty, 256, 256, texture, 0)

    def get_tile_filename(self, z, x, y):
        filename = self.tile_filename(z, x, y)
        if not LocalFileCache.file_exists(filename):
            url = self.tile_url(z, x, y)
            self.download(url, filename)
        return filename

    def tile_url(self, z, x, y):
        return self.url \
            .replace('${z}', str(math.floor(z))) \
            .replace('${x}', str(math.floor(x))) \
            .replace('${y}', str(math.floor(y)))

    def tile_filename(self, z, x, y):
        return LocalFileCache.get_full_path("maptiles/%s/%d-%d-%d.png" % (self.name, z, x, y))

    def download(self, url, file):
        print("Downloading [%s] into [%s]" % (url, file))
        LocalFileCache.ensure_dirs(LocalFileCache.get_full_path(os.path.join("maptiles", self.name)))
        req = urllib.request.Request(url, data=None, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        })
        with urllib.request.urlopen(req) as response, open(file, 'wb') as out_file:
            data = response.read()
            out_file.write(data)


class Map(SimpleArcade):

    def __init__(self, width=800, height=600):

        super().__init__(width, height)

        self.width = width
        self.height = height

        self.wh = round(self.width / 2.0)
        self.hh = round(self.height / 2.0)

        self.center = None
        self.center_x = None
        self.center_y = None

        self.zoom = 0
        self.projection = WebMercatorProjection(self.zoom)
        self.layers = []

    def set_center(self, center):
        self.center = center
        x, y = self.projection.project(self.center)
        self.center_x = round(x)
        self.center_y = round(y)
        return self

    def set_zoom(self, zoom):
        self.zoom = zoom
        self.projection.set_zoom(self.zoom)
        if self.center is not None:
            self.set_center(self.center)
        return self

    def add_layer(self, layer):
        layer.map = self
        self.layers.append(layer)
        return self

    def preload(self):
        for layer in self.layers:
            layer.preload()

    def render(self, et, dt):
        for layer in self.layers:
            layer.render(et, dt)

    def project(self, latlon):
        (x, y) = self.projection.project(latlon)
        return self.wh + x - self.center_x, self.hh - (y - self.center_y)

    def project_radius(self, latlon, meters):

        x1, y1 = self.project(latlon)

        p = LatLon(latlon.lat, latlon.lon)
        p = p.move(45, meters * 1.41421356237)
        x2, y2 = self.project(p)

        return abs(x2-x1), abs(y2-y1)


standard_tile_layer = MapTileLayer('standard', 'https://a.tile.openstreetmap.org/${z}/${x}/${y}.png', 0, 19)
wikimedia_tile_layer = MapTileLayer('wikimedia', 'https://maps.wikimedia.org/osm-intl/${z}/${x}/${y}.png', 0, 19)
watercolor_tile_layer = MapTileLayer('watercolor', 'http://c.tile.stamen.com/watercolor/${z}/${x}/${y}.jpg', 0, 17)
seamarks_tile_layer = MapTileLayer('seamarks', 'http://tiles.openseamap.org/seamark/${z}/${x}/${y}.png', 0, 17)
