import Constants
from Vis import pretty_list as lstr
from Person import Person

MAX_PEOPLE_DEFAULT = 20
MAX_V_DEFAULT = 2
class Elevator:
    """
    Elevator container and logic.
    """
    def __init__(self,
                 max_floors: int = Constants.N_FLOORS,
                 v_max: int = MAX_V_DEFAULT,
                 ppl_max: int = MAX_PEOPLE_DEFAULT) -> None:
        """
        Create an elevator object at floor 0 and no people inside.

        Args:
            v_max: the max speed of the elevator
            ppl_max: the max passenger capacity of the elevator
        """
        self.ppl: list[Person] = []                   # list of current people in the elevator
        self.loc: int = 0                    # current location (floor number)
        self.max_v: int = max(1, v_max)      # max transfer speed between floors
        self.max_ppl: int = max(1, ppl_max)  # passenger capacity
        self.past: list[float] = [] # a list of deltas to the elevator's loc, might be 0.5 or -0.5 for open doors
        self.max_floor: int = max_floors     # index of max floor
    
    def add_people(self, people: list = None, lim: int = 9999) -> int:
        """
        Adds passengers to the elevator.

        Args:
            people: a list of people to add
        Returns:
            the actual number of people added
        """
        if people is None:
            return 0
        n_board = min(self.max_ppl - len(self.ppl), len(people), lim)
        for _ in range(n_board):
            self.ppl.append(people.pop(0))
        return n_board
    
    def valid_moves(self) -> set:
        valid = []
        for delta_loc in range(-1 * self.max_v, self.max_v + 1):
            if self.loc + delta_loc <= self.max_floor and self.loc + delta_loc >= 0:
                valid.append(delta_loc)
        if self.loc != 0:
            valid.append(Constants.OPEN_DOWN)
        if self.loc != self.max_floor:
            valid.append(Constants.OPEN_UP)
        return valid
        
    
    def release(self) -> float:
        """
        ELevator releases the people who have arrived at their destination.

        Returns:
            the cumulative cost of the people who left the elevator
        """
        cost = 0
        removed = []
        for person in self.ppl:
            if person.dst == self.loc:
                cost += person.cost()
                removed.append(person)
        self.ppl = [person for person in self.ppl if person not in removed]
        return cost

        
    def move_to_target(self, target: int = 0) -> None:
        """
        Moves the elevator one time step closer to a target floor.

        Args:
            target: the target floor
        """
        if not (target <= self.max_floor and target >= 0):
            raise ValueError()
        if abs(target - self.loc) < self.max_v:
            self.past.append(target-self.loc)
            self.loc = target
        elif target > self.loc:
            self.loc += self.max_v
            self.past.append(self.max_v)
        else:
            self.loc -= self.max_v
            self.past.append(-1 * self.max_v)
    
    def move_delta(self, delta: int = 0) -> None:
        """
        Moves the elevator according to the delta of its location

        Args:
            delta: the elevator's location change
        """
        if delta not in self.valid_moves():
            raise ValueError()
        self.loc += delta
        self.past.append(delta)
    
    def destinations(self, sort: bool = True) -> list[bool]:
        """
        Returns a list of destinations of this elevator, possibly sorted by floor.

        Args:
            sort: whether or not to sort the list by increasing floor. If not,
                    the list is automatically sorted by the people's boarding time.
        Returns:
            a list of destinations of this elevator
        """
        if sort:
            return sorted([person.dst for person in self.ppl])
        else:
            return [person.dst for person in self.ppl]

    def __str__(self) -> str:
        """
        Returns a string representation of the elevator.
        """
        return f"@ floor {self.loc:02d} | " + lstr(self.ppl)