from pygame import draw
from math import atan2, pi
from threading import Timer

class Entity:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def shift(self, delta_x, delta_y):
        self.x += delta_x
        self.y += delta_y

class Circle(Entity):
    def __init__(self, x, y, radius, color):
        Entity.__init__(self, x, y)
        self.radius = radius
        self.color = color

    def __increment_radius(self):
        self.radius += 1

    def __decrement_radius(self):
        self.radius -= 1

    def draw(self, display):
        draw.circle(display, self.color.tuple, (int(self.x), int(self.y)), self.radius)

    def pulse(self, start, size, speed):
        for i in range(start, start + size):
            Timer(speed*i, self.__increment_radius).start()

        for i in range(start + size, start + (2*size)):
            Timer(speed*i, self.__decrement_radius).start()

    def timed_pulse(self, timings):
        for i in timings:
            self.pulse(int(floor(i)), 10, 1/500)

class Planet(Circle):
    def __init__(self, x, y, radius, color):
        Circle.__init__(self, x, y, radius, color)

class Satellite(Circle):
    def __init__(self, radius, color, body, offset = 0):
        Circle.__init__(self, body.x + body.radius, body.y + body.radius, radius, color)
        self.body = body

    @property
    def angle(self):  # Returns angle in radians
        return atan2(self.y - self.body.y, self.x - self.body.x)

    @property
    def quadrant(self):
        angle = self.angle
        if angle >= -pi and angle < -pi/2:
            quadrant = 0
        elif angle >= -pi/2 and angle < 0:
            quadrant = 1
        elif angle >= 0 and angle < pi/2:
            quadrant = 2
        else:
            quadrant = 3

        return quadrant

    @property
    def opposite(self): # Returns angle in radians
        opposite = self.angle + pi
        if opposite > pi:
            opposite = opposite - 2*pi

        return opposite

    
    def orbit(self, theta):
        self.x = self.x - (self.y - self.body.y)*theta
        self.y = self.y + (self.x - self.body.x)*theta

