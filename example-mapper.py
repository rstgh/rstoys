
from rstoys.geo import *
from rstoys.maps import *

from rstoys.realtime import Mapper


class ExampleMapper(SimpleArcade):

    def __init__(self):
        super().__init__(300, 500)

        self.x = 0
        self.dx = 0.5

    def render_line(self, x, y, label):
        y = self.height - y * 70 - 50

        lx = self.width/2 + (self.width-3) / 2 * x
        arcade.draw_line(lx, y, lx, y+32, (255,0,0), 3)
        arcade.draw_text(label, self.width/2, y+10, (64,64,64), 20, anchor_x="center", anchor_y="center")


    def render(self, et, dt):

        arcade.draw_line(self.width/2, 0, self.width/2, self.height, (0,64,0), 1)

        self.x = self.x + self.dx * dt
        if self.x <= -1:
            self.x = -1
            self.dx = abs(self.dx)
        if self.x >= 1:
            self.x = 1
            self.dx = -abs(self.dx)

        self.render_line(self.x, 0, 'input (lin swipe -1...1)')

        x = Mapper(self.x).gap(0.25).value()
        self.render_line(x, 2, 'gap(0.25)')

        x = Mapper(self.x).gaplin(0.25).value()
        self.render_line(x, 3, 'gaplin(0.25)')

        x = Mapper(self.x).exp(10).value()
        self.render_line(x, 4, 'exp(10)')

        x = Mapper(self.x).exp(0.1).value()
        self.render_line(x, 5, 'exp(0.1)')

        x = Mapper(self.x).mul(2).trim(-0.5, 1).value()
        self.render_line(x, 6, 'mul(2).trim(-0.5, 1)')


app = ExampleMapper()
app.run()
