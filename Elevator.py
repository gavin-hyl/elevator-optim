import Constants
from Vis import ppl_list as lstr

MAX_PEOPLE_DEFAULT = 20
MAX_V_DEFAULT = 2
class Elevator:
    """
    Elevator container and logic.
    """
    def __init__(self, v_max: int = MAX_V_DEFAULT, ppl_max: int = MAX_PEOPLE_DEFAULT) -> None:
        """
        Create an elevator object at floor 0 and no people inside.

        Args:
            v_max: the max speed of the elevator
            ppl_max: the max passenger capacity of the elevator
        """
        self.ppl = []
        self.loc = 0
        self.v_max = max(1, v_max)
        self.ppl_max = max(1, ppl_max)
    
    def add(self, people: list = None) -> int:
        """
        Adds passengers to the elevator.

        Args:
            people: a list of people to add
        Returns:
            the actual number of people added
        """
        if people is None:
            return 0
        n_board = min(self.ppl_max - len(self.ppl), len(people))
        for _ in range(n_board):
            self.ppl.append(people.pop(0))
        return n_board
    
    def release(self) -> float:
        """
        ELevator releases the people who have arrived at their destination.

        Returns:
            the cumulative cost of the people who left the elevator
        """
        cost = 0
        for person in reversed(self.ppl):
            if person.dst == self.loc:
                cost += person.cost()
                self.ppl.remove(person)
        return cost

        
    def move(self, target : int = 0) -> None:
        """
        Moves the elevator one time step closer to a target floor.

        Args:
            target: the target floor
        """
        target = max(0, target) # must be non-negative
        if abs(target - self.loc) < self.v_max:
            self.loc = target
        elif target > self.loc:
            self.loc += self.v_max
        else:
            self.loc -= self.v_max
    
    def dests(self) -> list:
        return sorted(list({person.dst for person in self.ppl}))

    def __str__(self) -> str:
        """
        Returns a string representation of the elevator.
        """
        rep = "elevator | "
        rep += lstr(self.ppl)
        rep += f" @ floor {self.loc:02d}"
        return rep