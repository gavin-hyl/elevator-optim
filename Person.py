from random import randint

class Person:
    """
    A single person, with a running timer and a destination.
    """
    def __init__(self, dest: int = 1) -> None:
        """
        Create a person with a destination.

        Args:
            dest: the person's destination
        """
        self.destination = dest
        self.time = 0

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
        return cls(dest)
    
    def step_time(self) -> None:
        """
        Steps the time forward for a Person.
        """
        self.time += 1

    def cost(self) -> None:
        """
        Calculates the waiting cost for this Person.

        Returns:
            the waiting cost
        """
        return self.time * self.time

    def __str__(self) -> str:
        return f"(dst={self.destination}, t={self.time})"