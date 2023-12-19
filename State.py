from Elevator import Elevator
from Logic import move
from Person import Person
import Constants
from numpy.random import poisson
import numpy as np
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
        2. adds new people to the floors
        3. determines the elevator's actions by calling the logic function
        in the Elevator class, and 
        4. performs the actions.
        """
        self.time += 1
        for person in self.active_ppl():
            person.step_time()
        for i, floor in enumerate(self.floors):
            for _ in range(poisson(self.avg_ppl, 1)[0]):
                floor.append(Person.from_range(i, (0, len(self.floors))))
        view = self.view_simple()
        print(view)
        actions = move(view)
        # first iterate over the elevators that need to move
        # then iterate over the floors to better distribute people boarding
        for i, move in enumerate(actions):
            if move >= 0:
                self.elevators[i].move(move)
        for floor, ppl in enumerate(self.floors):
            # make sure the people are distributed evenly among the elevators
            open_up = []
            open_down = []
            ppl_up = [person for person in ppl if person.dst > floor]
            ppl_down = [person for person in ppl if person.dst < floor]
            for i, elevator in enumerate(self.elevators):
                if elevator.loc == floor:
                    if actions[i] == Constants.OPEN_UP:
                        open_up.append(elevator)
                    elif actions[i] == Constants.OPEN_DOWN:
                        open_down.append(elevator)
            up_partitions = [len(x) for x in np.array_split(ppl_up, len(open_up))]
            down_partitions = [len(x) for x in np.array_split(ppl_down, len(open_down))]
            for i, elevator in enumerate(open_up):
                self.cost += elevator.open(ppl_up, up_partitions[i])
            for i, elevator in enumerate(open_down):
                self.cost += elevator.open(ppl_down, down_partitions[i])
    
    def view_simple(self) -> dict:
        """
        Returns a dictionary of the available information for the move logic
        implementation. That function is implemented in the Elevator class to
        prevent it from accessing information that is unknowable in reality, 
        such as the number of people on a floor.

        Returns:
            a dictionary that contains the information available in the format
            {
                'E1' : {'dst' : [T, F, T],
                        'loc' : 2},
                ...
                'En' : {'dst' : <list-of-bools-describing-buttons-pressed>,
                        'loc' : <location>}
                'floor_buttons' : <list-of-ints-describing-up/down-pressed>
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
        view = {}
        for i, elevator in enumerate(self.elevators):
            elevator_dests = [False for _ in enumerate(self.floors)]
            for person in elevator.ppl:
                elevator_dests[person.dst] = True
            view.update({f'E{i}' : {'dst' : elevator_dests, 
                                    'loc' : elevator.loc}})
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
        Returns a list of all the people still being tracked by this State.

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
            rep += (f"floor {floor:02d} | " + lstr(ppl)).ljust(50) + "| "
            for i, elevator in enumerate(self.elevators):
                if elevator.loc == floor:
                    rep += f"[E{i}] " + lstr(elevator.ppl) + ' '
            rep += '\n'
        rep += f"(time={self.time}, cost={self.cum_cost()})\n"
        rep += "========\n"
        return rep