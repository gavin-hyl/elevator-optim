import Constants
from Vis import pretty_list as lstr

MAX_PEOPLE_DEFAULT = 20
MAX_V_DEFAULT = 1
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
        self.ppl = []                   # list of current people in the elevator
        self.loc = 0                    # current location (floor number)
        self.v_max = max(1, v_max)      # max transfer speed between floors
        self.ppl_max = max(1, ppl_max)  # passenger capacity
        self.past = []                  # a list of deltas to the elevator's loc
                                        # might be 0.5 or -0.5 for open doors
    
    def add(self, people: list = None, lim: int = 9999) -> int:
        """
        Adds passengers to the elevator.

        Args:
            people: a list of people to add
        Returns:
            the actual number of people added
        """
        if people is None:
            return 0
        n_board = min(self.ppl_max - len(self.ppl), len(people), lim)
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
        target = max(0, target)
        if abs(target - self.loc) < self.v_max:
            self.past.append(target-self.loc)
            self.loc = target
        elif target > self.loc:
            self.loc += self.v_max
            self.past.append(self.v_max)
        else:
            self.loc -= self.v_max
            self.past.append(-1 * self.v_max)
    
    def dests(self, sort: bool = True) -> list:
        """
        Returns a list of destinations of this elevator, possibly sorted by floor.

        Args:
            sort: whether or not to sort the list by increasing floor. If not,
                    the list is automatically sorted by the people's boarding time.
        Returns:
            a list of destinations of this elevator
        """
        if sort:
            return sorted(list({person.dst for person in self.ppl}))
        else:
            return list({person.dst for person in self.ppl})

    def __str__(self) -> str:
        """
        Returns a string representation of the elevator.
        """
        rep = f"@ floor {self.loc:02d} | " + lstr(self.ppl)
        return rep