from Elevator import Elevator
from Person import Person
import Constants
from Vis import pretty_list as lstr
import Models

from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

import numpy as np
from numpy.random import poisson

class State:
    """
    A State object for an elevator optimization problem. Contains information
    about the people distribution, the elevator positions, the time elapsed, and
    the total cost up to this point. 
    """
    WAITING_COST_WEIGHT = 1         # incentivize minimizing waiting time
    COMPLETION_COST_WEIGHT = 0.3    # incentivize bringing people closer to dst
    DISTRIBUTION_COST_WEIGHT = 0.1  # incentivize going closer to people

    def __init__(self,
                 logic = None,
                 floors: int = 1,
                 n_elevators: int = 1, 
                 avg_ppl: int = 0,
                 ppl_generation_profile: list[float] = None) -> None:
        """
        Create a new state for an elevator optimization problem. 

        Args:
            logic: elevator move logic, must return an iterable containing positive integers or Constants.OPEN_UP or Constants.OPEN_DOWN
            floors: the number of floors in the building
            n_elevators: the number of elevators in the building
            avg_ppl: the average number of people that will arrive on each floor per step
            ppl_generation_profile: average number of people to generate on each floor per step, specified for each floor.
                                    Overrides the avg_ppl parameter.
        """
        self.elevators: list[Elevator] = [Elevator(max_floors=floors-1) 
                                          for _ in range(max(1, n_elevators))]
        self.n_floors: int = max(1, floors)
        self.floors: list[list[Person]] = [[] for _ in range(self.n_floors)]
        self.logic: function = logic if logic is not None else Models.default
        self.time: int = 0
        self.total_ppl: int = 0
        self.cost: float = 0
        self.avg_ppl: float = max(0, avg_ppl)
        if ppl_generation_profile is None:
            self.arrival_profile = [self.avg_ppl for _ in range(self.n_floors)]
        else:
            self.arrival_profile = ppl_generation_profile
        self.conv_array: list[float] = [-1 for _ in range(floors)]  # TODO change to gaussian
        self.conv_array = list(map(lambda x: x * self.DISTRIBUTION_COST_WEIGHT, self.conv_array))
        colorama_init()
    
    def update(self, add_ppl: bool = True) -> None:
        """
        Forwards the time by 1 step. It 
        1. updates all the times for the Person objects,
        2. adds new people to the floors
        3. determines the elevator's actions by calling the move logic function
        in the Logic module, 
        4. performs the actions, and 
        5. Calculates the step cost.

        Args:
            add_ppl: whether or not to add people
        """
        self.time += 1
        for person in self.active_ppl():
            person.time += 1
        if add_ppl:
            self.add_ppl()
        actions = self.logic(self.sys_view())
        # first iterate over the elevators that need to move
        # then iterate over the floors to better distribute people
        cost_distribution = self.hall_ppl_distribution_cost()
        for action, elevator in zip(actions, self.elevators):
            self.cost += cost_distribution[elevator.loc]
            if isinstance(action, int):
                elevator.move_delta(action)
            else:
                elevator.past.append(action)
        
        def distribute_ppl(elevators: list[Elevator], people: list[Person]) -> None:
            if len(elevators) > 1:
                for _ in people:
                    # people enter the elevator with the least passengers
                    least_filled = min(elevators, key=lambda e: len(e.ppl))
                    if least_filled.add_people(people=people, lim=1) == 0:
                        break   # all elevators are full
            elif len(elevators) == 1:
                elevators[0].add_people(people=people)
        
        for floor, ppl in enumerate(self.floors):
            # people will automatically board the elevator with least passengers
            if len(ppl) == 0:
                continue
            open_up = []
            open_down = []
            ppl_up = [person for person in ppl if person.dst > floor]
            ppl_down = [person for person in ppl if person.dst < floor]
            for action, elevator in zip(actions, self.elevators):
                if elevator.loc == floor and isinstance(action, float):
                    self.cost += elevator.release() * self.WAITING_COST_WEIGHT
                    if action == Constants.OPEN_UP:
                        open_up.append(elevator)
                    elif action == Constants.OPEN_DOWN:
                        open_down.append(elevator)
            distribute_ppl(open_up, ppl_up)
            distribute_ppl(open_down, ppl_down)
            self.floors[floor] = sorted(ppl_up + ppl_down, key=lambda p: p.time)
            
    
    def sys_view(self) -> dict:
        """
        Returns a dictionary of the available information for the move logic
        implementation. That function is implemented in the Elevator class to
        prevent it from accessing information that is unknowable in reality,
        such as the number of people on a floor.

        Returns:
            a dictionary that contains the information available in the format
            {
                'E1' : {'dst' : [T, F, T],
                        'loc' : [F, T, F]},
                ...
                'En' : {'dst' : <list-of-bools-describing-buttons-pressed>,
                        'loc' : <location>}
                'floor_buttons' : <list-of-bools-describing-up/down-pressed>
            }
        """
        hall_calls = self.hall_calls()
        view = {}
        for i, elevator in enumerate(self.elevators):
            destination_vector = [(floor in elevator.destinations()) for floor in range(self.n_floors)]
            location_vector = [False for _ in range(self.n_floors)]
            location_vector[elevator.loc] = True
            view.update({f'E{i}' : {'destinations' : destination_vector, 
                                    'location' : location_vector,
                                    'past' : elevator.past}})
        view.update({'floor_buttons': hall_calls})
        view.update({'n_floors': self.n_floors})
        return view

    def flat_view(self) -> list[bool]:
        view = self.sys_view()
        flat = view.pop('floor_buttons')
        view.pop('n_floors')
        for _, val in view.items():
            flat.append(val.get('location'))
            flat.extend(val.get('destinations'))
        return flat

    def total_cost(self) -> float:
        """
        Calculates the cumulative cost of all the people still waiting to be
        sent to their destinations combined with the costs already calculated.

        1. total cost
        2. journey completion rate
        3. elevator aggregation to people

        Returns:
            the cumulative cost of the state
        """
        if self.total_ppl != 0:
            avg_completion = self.total_ppl - len(self.active_ppl())
            for elevator in self.elevators:
                for person in elevator.ppl:
                    avg_completion += abs((elevator.loc - person.dst) / (person.src - person.dst))
            avg_completion /= self.total_ppl
        else:
            avg_completion = 1
        for person in self.active_ppl():
            self.cost += person.cost()
        return self.cost + (1 - avg_completion) * self.COMPLETION_COST_WEIGHT

    def active_ppl(self) -> list[Person]:
        """
        Returns a list of all the people still being tracked by this State.

        Returns:
            the aforementioned list
        """
        return self.hall_ppl() + self.elevator_ppl()
    
    def add_ppl(self) -> None:
        for floor, ppl in enumerate(self.floors):
            for _ in range(poisson(lam=self.arrival_profile[floor], size=1)[0]):
                self.total_ppl += 1
                ppl.append(Person.from_range(src=floor, 
                                            dst_range=(0, self.n_floors-1)))
    
    def hall_ppl(self) -> list[Person]:
        people = []
        for floor in self.floors:
            for person in floor:
                people.append(person)
        return people
    
    def elevator_ppl(self) -> list[Person]:
        people = []
        for elevator in self.elevators:
            for person in elevator.ppl:
                people.append(person)
        return people

    def summarize(self) -> dict:
        """
        Provide a summary of the state so far.

        Returns:
            a dictionary with important information about the state
        """
        return {
            'time elapsed' : self.time,
            'people arrived' : self.total_ppl,
            'people left over' : len(self.active_ppl()),
            'total cost' : round(self.total_cost(), 3),
            'average cost' : round(self.total_cost()/self.total_ppl, 3) 
                            if self.total_ppl != 0 else 0
        }

    def hall_calls(self) -> list[bool]:
        """
        Check the floor buttons' statuses based on the people on that floor.

        Returns:
            a list of bools describing the floor buttons. Every floor gets two
            elements describing whether the up or down buttons are pressed.
        """
        buttons = [False for _ in range(2 * self.n_floors)]
        for floor, ppl in enumerate(self.floors):
            up, down = False, False
            # check people's destinations one by one
            for person in ppl:
                if not up and person.dst > floor:
                    buttons[2*floor] = True
                    up = True
                elif not down and person.dst < floor:
                    buttons[2*floor+1] = True
                    down = True
                elif up and down:
                    break
        return buttons
    
    def hall_call_distribution_cost(self) -> list[float]:
        """
        Computes the density of hall calls to incentivize moving elevators to regions
        with more calls. This is seen by the elevator.

        Returns:
            the hall call distribution cost
        """
        calls = self.hall_calls()
        distribution = []
        for i, val in enumerate(calls):
            if i%2 == 0:
                distribution.append(int(val) + int(calls[i+1]))
        return list(np.convolve(distribution, self.conv_array, mode='same'))
    
    def hall_ppl_distribution_cost(self) -> list[float]:
        """
        Computes the density of hall people to incentivize moving elevators to regions
        with more people. This is seen by the state.

        Returns:
            the people distribution cost
        """
        hall_ppl_count = []
        for floor in self.floors:
            hall_ppl_count.append(len(floor))
        cost_distribution = list(np.convolve(hall_ppl_count, self.conv_array, mode='same'))
        cost_distribution[0] -= 0.001   # make elevators return to ground floor
        return cost_distribution
    
    def __str__(self) -> str:
        """
        Try printing it.
        """
        calls = self.hall_calls()
        rep = '==========================================================\n\n'
        for floor, ppl in enumerate(reversed(self.floors)):
            floor = self.n_floors - floor - 1
            button_str = ''
            up, down = calls[2*floor], calls[2*floor + 1]
            up_color_str = Fore.CYAN if up else Style.DIM
            down_color_str = Fore.CYAN if down else Style.DIM
            button_str = f"{up_color_str}↑{Style.RESET_ALL} {down_color_str}↓{Style.RESET_ALL}"
            rep += f"floor {Fore.CYAN}{floor:02d}{Style.RESET_ALL} {button_str} | " + lstr(ppl).ljust(75) + "| "
            for i, elevator in enumerate(self.elevators):
                if elevator.loc == floor:
                    elevator_dest_str = lstr(elevator.destinations())
                    if len(elevator_dest_str) != 0:
                        elevator_dest_str = ' → ' + elevator_dest_str
                    rep += f"{Fore.CYAN}[E{i}{elevator_dest_str}]{Style.RESET_ALL} " + lstr(elevator.ppl) + ' '
            rep += '\n\n'
        rep += "----------------------------------------------------------\n\n"
        for i, elevator in enumerate(self.elevators):
            elevator_dest_str = lstr(elevator.destinations())
            if len(elevator_dest_str) != 0:
                elevator_dest_str = '→ ' + elevator_dest_str + ' '
            rep += f'{Fore.CYAN}elevator {i} @ floor {elevator.loc:02d} {elevator_dest_str}{Style.RESET_ALL}| {lstr(elevator.ppl)}\n'
            rep += f"{Fore.CYAN}\tpast: {lstr(elevator.past)}{Style.RESET_ALL}\n\n"
        rep += "----------------------------------------------------------\n"
        rep += f"time = {Fore.CYAN}{self.time}{Style.RESET_ALL}, cost = {self.total_cost():.3f}, active people = {len(self.active_ppl())}\n"
        rep += f"elevator system sees {Fore.CYAN}blue{Style.RESET_ALL}\n"
        rep += "==========================================================\n"
        return rep