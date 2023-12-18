from random import randint

class Person:


    def __init__(self, dest: int = 1) -> None:
        self.dst = dest
        self.time = 0

    def __init__(self, src: int = 0, floor_range: tuple = None):
        if floor_range is None:
            floor_range = (0, 1)
        dest = src
        while dest == src:
            dest = randint(floor_range[0], floor_range[1])
        self.__init__(dest=dest)
        

    def check_arrived(self, loc: int = -1):
        return True if loc == self.dst else False
    
    def step_time(self):
        self.time += 1

    def cost(self):
        return self.time * self.time

    def __str__(self) -> str:
        return f"(dst={self.dst}, t={self.time})"