

class Person:


    def __init__(self, dest: int = 1) -> None:
        self.dst = dest
        self.time = 0

    def update(self, loc: int):
        self.time += 1
        return Person.wait_cost(self.time) if loc == self.dst else 0

    def wait_cost(time: int):
        return time * time      # punishes long waiting times

    def __str__(self) -> str:
        return f"(dst={self.dst}, t={self.time})"