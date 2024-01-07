from random import randint

class Person:
    """
    A single person, with a running timer, a source, and a destination.
    """
    def __init__(self, src: int = 0, dest: int = 1, time: int = 0) -> None:
        """
        Create a person with a destination.

        Args:
            src: where the person originated
            dest: the person's destination
        """
        if src == dest:
            raise ValueError()
        self.src: int = src
        self.dst: int = dest
        self.time: int = time

    @classmethod
    def from_range(cls, src: int = 0, dst_range: tuple = None):
        """
        An alternative constructor for a Person. Randomly determines its
        destination to be an integer in floor_range which is not src.

        Args:
            src: where the person is being generated
            floor_range: a range for the person's prospective destinations
        """
        if dst_range is None:
            dst_range = (0, 1)
        dest = src
        while dest == src:  # cannot start and end on the same floor
            dest = randint(dst_range[0], dst_range[1])
        return cls(src, dest)

    def cost(self) -> float:
        """
        Calculates the waiting cost for this Person.

        Returns:
            the waiting cost
        """
        return self.time * self.time

    def __str__(self) -> str:
        return f"({self.src}→{self.dst}, {self.time}t)"