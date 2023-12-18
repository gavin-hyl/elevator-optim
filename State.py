from Elevator import Elevator
from Person import Person
import Constants
from numpy.random import poisson
from Vis import list_to_str as lstr

class State:
    """
    A State object for an elevator optimization problem. Contains information
    about the people distribution, the elevator positions, the time elapsed, and
    the total cost up to this point. 
    """
    def __init__(self, floors: int = 1, n_elevators: int = 1, avg_ppl: int = 0.1) -> None:
        """
        Create a new state for an elevator optimization problem. 

        Args:
            floors: the number of floors in the building
            n_elevators: the number of elevators in the building
            avg_ppl: the average number of people that will arrive on each floor per step
        """
        self.elevators = [Elevator() for _ in range(max(1, n_elevators))]
        self.floors = [[] for _ in range(max(1, floors))]
        self.time = 0
        self.cost = 0
        self.avg_ppl = max(0, avg_ppl)
    
    def update(self) -> None:
        """
        Forwards the time by 1 step. It 
        1. updates all the times for the Person objects,
        2. determines the elevator's actions by calling the logic function
        in the Elevator class, and 
        2. performs the actions.
        """
        self.time += 1
        for person in self.active_ppl():
            person.step_time()
        for i, floor in enumerate(self.floors):
            for _ in range(poisson(self.avg_ppl, 1)[0]):
                floor.append(Person.from_range(i, (0, len(self.floors))))
        view = self.view_simple()
        actions = Elevator.move_logic(view)
        for i, move in enumerate(actions):
            elevator = self.elevators[i]
            if move >= 0:
                elevator.move(move)
            else:
                self.cost += elevator.open(self.floors[elevator.loc])

    
    def view_simple(self) -> dict:
        """
        Returns a dictionary of the available information for the move logic
        implementation. That function is implemented in the Elevator class to
        prevent it from accessing information that is unknowable in reality, 
        such as the number of people on a floor.

        Returns:
            a dictionary that contains the information available in the format
            {
                'E1' : ({1, 2, 3}, 0),
                'E2' : ({1, 5}, 2),
                ...
                'En' : ({4, 6}, 5),
                'floor_buttons' : [UPDOWN, UP, NONE, DOWN, ... DOWN]
            }
        """
        floor_buttons = []
        for floor, ppl in enumerate(self.floors):
            up_pressed, down_pressed = False, False
            floor_buttons.append(Constants.NO_REQ)
            for person in ppl:
                if not up_pressed and person.dst > floor:
                    floor_buttons[floor] += Constants.UP_REQ 
                    up_pressed = True
                elif not down_pressed and person.dst < floor:
                    floor_buttons[floor] += Constants.DOWN_REQ
                    down_pressed = True
                elif up_pressed and down_pressed:
                    break
        view = {
            # e.g., E1 : destinations={3, 4, 5}, loc=2
            f'E{i}' : ({person.dst for person in elevator.ppl}, elevator.loc)
                        for i, elevator in enumerate(self.elevators)
        }
        view.update({'floor_buttons': floor_buttons})
        return view

    def cum_cost(self) -> float:
        """
        Calculates the cumulative cost of all the people still waiting to be
        sent to their destinations combined with the costs already calculated.

        Returns:
            the cumulative cost of the state
        """
        cost = 0
        for person in self.active_ppl():
            cost += person.cost()
        return cost + self.cost
        
    def active_ppl(self) -> list:
        """
        Returns a list of all the people still being tracked by this State

        Returns:
            the aforementioned list
        """
        people = []
        for floor in self.floors:
            for person in floor:
                people.append(person)
        for elevator in self.elevators:
            for person in elevator.ppl:
                people.append(person)
        return people
    
    def __str__(self) -> str:
        rep = "========\n"
        for floor, ppl in enumerate(self.floors):
            floor_rep = (f"floor {floor:02d} | " + lstr(ppl)).ljust(50) + "| "
            for i, elevator in enumerate(self.elevators):
                if elevator.loc == floor:
                    floor_rep += f"[E{i}] " + lstr(elevator.ppl) + ' '
            rep += floor_rep + '\n'
        rep += f"(time={self.time}, cost={self.cum_cost()})\n"
        rep += "========\n"
        return rep