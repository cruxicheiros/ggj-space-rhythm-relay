class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

    @property
    def tuple(self):
        return (self.r, self.g, self.b)

    @tuple.setter
    def tuple(self, value):
        self.tuple = value
        self.r = value[0]
        self.g = value[1]
        self.b = value[2]


red = Color(255, 0, 0)
print(red.tuple)
red.g = 4
print(red.tuple)
