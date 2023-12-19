import Constants
from Vis import list_to_str as lstr

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
    
    def open(self, people:list=None) -> float:
        """
        Open the elevator doors. Returns the cumulative cost of people who have 
        reached their destination.

        Args:
            people: a list of people on this floor
        Returns:
            the total cost of people that left the elevator
        """
        total_cost = 0
        for person in reversed(self.ppl):
            if person.check_arrived(self.loc):
                total_cost += person.cost()
                self.ppl.remove(person)
        n_board = min(self.ppl_max - len(self.ppl), len(people))
        for _ in range(n_board):
            self.ppl.append(people.pop(0))  # TODO boarding order? Or should this be handled in the State class?
        return total_cost
        
    def move(self, target : int = 0) -> None:
        """
        Moves the elevator one time step closer to a target floor.

        Args:
            target: the target floor
        Raises:
            ValueError: if target is negative
        """
        if target < 0:
            raise ValueError('target floor must be positive')
        if abs(target - self.loc) < self.v_max:
            self.loc = target
        elif target > self.loc:
            self.loc += self.v_max
        else:
            self.loc -= self.v_max
    
    @classmethod
    def move_logic(cls, state_view: dict) -> list:
        """
        Coordinates all the elevators according to the imperfect information it
        can gather.

        Args:
            state_view: the information provided by a State class
        Returns:
            a list of the actions for each elevator, -1 indicating open doors
        """
        # raise NotImplementedError
        targets = []
        floor_buttons = state_view.pop('floor_buttons')
        for i, _ in enumerate(state_view):
            elevator_info = state_view.get(f"E{i}")
            destinations = elevator_info.get('dst')
            location = elevator_info.get('loc')
            targets.append(-1)
        return targets

    def __str__(self) -> str:
        """
        Returns a string representation of the elevator.
        """
        rep = "elevator | "
        rep += lstr(self.ppl)
        rep += f" @ floor {self.loc:02d}"
        return rep