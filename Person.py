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
        self.dst = dest
        self.time = 0

    @classmethod
    def from_range(cls, src: int = 0, floor_range: tuple = None):
        """
        An alternative constructor for a Person. Randomly determines its
        destination to be an integer in floor_range.

        Args:
            src: where the person is being generated
            floor_range: a range for the person's prospective destinations
        """
        if floor_range is None:
            floor_range = (0, 1)
        dest = src
        while dest == src:  # cannot start and end on the same floor
            dest = randint(floor_range[0], floor_range[1])
        return cls(dest)

    def check_arrived(self, loc: int = -1) -> bool:
        """
        Checks if a person has arrived at their destination.

        Args:
            loc: the person's current location
        Returns:
            True if a person has arrived at their destination, False otherwise
        """
        return loc == self.dst
    
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
        return f"(dst={self.dst}, t={self.time})"