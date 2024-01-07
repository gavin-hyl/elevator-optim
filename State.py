from Elevator import Elevator
from Person import Person
import Constants
from Vis import pretty_list as lstr
import Models
from ListUtils import list_subtract
import math

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
    DISTRIBUTION_COST_WEIGHT = 1    # incentivize going closer to people

    def __init__(self,
                 logic = None,
                 floors: int = 2,
                 n_elevators: int = 1, 
                 avg_ppl: float = 0,
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
        if n_elevators < 1 or floors < 2 or avg_ppl < 0:
            raise ValueError("Not a realistic situation")
        self.elevators: list[Elevator] = [Elevator(max_floors=floors-1) # ?
                                          for _ in range(n_elevators)]
        self.n_floors: int = floors
        self.floors: list[list[Person]] = [[] for _ in range(floors)]
        self.logic: function = logic
        self.time: int = 0
        self.total_ppl: int = 0
        self.waiting_cost: float = 0
        self.distribution_cost: float = 0
        self.avg_ppl: float = avg_ppl
        # the average number of people to arrive on each floor per tick
        # people are drawn according to a poisson distribution
        self.arrival_profile: list[float] = [self.avg_ppl for _ in range(self.n_floors)] \
                                            if ppl_generation_profile is None \
                                            else ppl_generation_profile
        # generate an inverse quadratic potential well with length of the number
        # of floors to incentivize elevators to move towards people
        _half_len = self.n_floors // 2 + 1
        self.conv_array: list[float] = [-(1/(r*r)) for r in range(1, _half_len)]
        self.conv_array = list(reversed(self.conv_array)) + self.conv_array
        if self.n_floors % 2 == 1:
            self.conv_array.insert(_half_len-1, self.conv_array[_half_len-1]-1)
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
        cost_distribution = self.hall_ppl_potential()
        for action, elevator in zip(actions, self.elevators):
            self.distribution_cost += cost_distribution[elevator.loc]
            if isinstance(action, int):
                elevator.move_delta(action)
            else:
                elevator.past.append(action)
        
        for floor, ppl in enumerate(self.floors):
            # people will automatically board the elevator with least passengers
            if len(ppl) == 0 and not self._is_elevator_on_floor(floor):
                continue
            open_up = []
            open_down = []
            ppl_up = [p for p in ppl if p.dst > floor]
            ppl_down = [p for p in ppl if p.dst < floor]
            for action, elevator in zip(actions, self.elevators):
                if elevator.loc == floor and (math.isclose(action, Constants.OPEN_UP) or math.isclose(action, Constants.OPEN_DOWN)):
                    self.waiting_cost += elevator.release()
                    if action == Constants.OPEN_UP:
                        open_up.append(elevator)
                    elif action == Constants.OPEN_DOWN:
                        open_down.append(elevator)
            ppl_up = State._distribute_ppl(open_up, ppl_up)
            ppl_down = State._distribute_ppl(open_down, ppl_down)
            self.floors[floor] = sorted(ppl_up + ppl_down, key=lambda p: p.time)

    @staticmethod  
    def _distribute_ppl(elevators: list[Elevator], people: list[Person]) -> list[Person]:
        added = []
        if len(elevators) > 1:
            for _ in people:
            # people enter the elevator with the least passengers
                least_filled = min(elevators, key=lambda e: len(e.ppl))
                added = least_filled.add_people(people=people, lim=1)
                if len(added) == 0:
                    break   # all elevators are full
            return list_subtract(people, added)
        elif len(elevators) == 1:
            added = elevators[0].add_people(people=people)
            return list_subtract(people, added)
        else:
            return people
    
    def _is_elevator_on_floor(self, floor: int):
        for elevator in self.elevators:
            if elevator.loc == floor:
                return True
        return False

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
                'hall_calls' : <list-of-bools-describing-up/down-pressed>
            }
        """
        hall_calls = self.hall_calls()
        view = {}
        for i, elevator in enumerate(self.elevators):
            destination_vector = [(floor in elevator.destinations()) 
                                  for floor in range(self.n_floors)]
            location_vector = [False for _ in range(self.n_floors)]
            location_vector[elevator.loc] = True
            view.update({f'E{i}' : {'destinations' : destination_vector, 
                                    'location' : location_vector,
                                    'past' : elevator.past}})
        view.update({'hall_calls': hall_calls})
        view.update({'n_floors': self.n_floors})
        view.update({'v_max': self.elevators[0].max_v})
        return view

    def flat_view(self) -> list[bool]:
        view = self.sys_view()
        flat = view.pop('hall_calls')
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
        if self.total_ppl > 0:
            avg_completion = self.total_ppl - len(self.active_ppl())
            for elevator in self.elevators:
                for person in elevator.ppl:
                    avg_completion += abs((elevator.loc - person.dst) / (person.src - person.dst))
            avg_completion /= self.total_ppl
            for person in self.active_ppl():
                self.waiting_cost += person.cost()
            return self.waiting_cost / self.total_ppl * self.WAITING_COST_WEIGHT \
                + (1 - avg_completion) * self.COMPLETION_COST_WEIGHT \
                + self.distribution_cost / self.time * self.DISTRIBUTION_COST_WEIGHT
        elif self.time > 0:
            # basically return to ground floor
            return self.distribution_cost / self.time * self.DISTRIBUTION_COST_WEIGHT
        else:
            return 0.0
    
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
                ppl.append(Person.from_range(src=floor, dst_range=(0, self.n_floors-1)))
    
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
        total_cost = self.total_cost()
        return {
            'time elapsed' : self.time,
            'people arrived' : self.total_ppl,
            'people left over' : len(self.active_ppl()),
            'total cost' : round(total_cost, 3),
            'average cost' : round(total_cost/self.total_ppl, 3) 
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
    
    def hall_ppl_potential(self) -> list[float]:
        """
        Computes the density of hall people to incentivize moving elevators to regions
        with more people. This is only seen by the state.

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
        distribution_cost = self.hall_ppl_potential()
        for floor, ppl in enumerate(reversed(self.floors)):
            floor = self.n_floors - floor - 1
            button_str = ''
            up, down = calls[2*floor], calls[2*floor + 1]
            up_color_str = Fore.CYAN if up else Style.DIM
            down_color_str = Fore.CYAN if down else Style.DIM
            button_str = f"{up_color_str}↑{Style.RESET_ALL} {down_color_str}↓{Style.RESET_ALL}"
            rep += f"floor {Fore.CYAN}{floor:02d}{Style.RESET_ALL} {button_str} ({round(distribution_cost[floor], 5):.3f}) | " + lstr(ppl).ljust(75) + "| "
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