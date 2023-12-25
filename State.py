from Elevator import Elevator
from Person import Person
import Constants
from Vis import pretty_list as lstr
import Models

from colorama import init as colorama_init
from colorama import Fore
from colorama import Style\

import numpy as np
from numpy.random import poisson

class State:
    """
    A State object for an elevator optimization problem. Contains information
    about the people distribution, the elevator positions, the time elapsed, and
    the total cost up to this point. 
    """
    def __init__(self,
                 logic = None,
                 floors: int = 1,
                 n_elevators: int = 1, 
                 avg_ppl: int = 0,
                 ppl_generation_profile: list = None) -> None:
        """
        Create a new state for an elevator optimization problem. 

        Args:
            logic: elevator move logic, must return an iterable containing positive integers or Constants.OPEN_UP or Constants.OPEN_DOWN
            floors: the number of floors in the building
            n_elevators: the number of elevators in the building
            avg_ppl: the average number of people that will arrive on each floor per step
            ppl_generation_profile: average number of people to generate on each floor per step, specified for each floor
        """
        self.elevators = [Elevator() for _ in range(max(1, n_elevators))]
        self.n_floors = max(1, floors)
        self.floors = [[] for _ in range(self.n_floors)]
        self.logic = logic if logic is not None else Models.default
        self.time = 0
        self.total_ppl = 0
        self.cost = 0
        self.avg_ppl = max(0, avg_ppl)
        # for further customization
        if ppl_generation_profile is None:
            self.arrival_profile = [self.avg_ppl for _ in range(self.n_floors)]
        else:
            self.arrival_profile = ppl_generation_profile
        colorama_init()
    
    def update(self, add_ppl: bool = True) -> None:
        """
        Forwards the time by 1 step. It 
        1. updates all the times for the Person objects,
        2. adds new people to the floors
        3. determines the elevator's actions by calling the move logic function
        in the Logic module, and 
        4. performs the actions.
        """
        self.time += 1
        for person in self.active_ppl():
            person.step_time()
        if add_ppl:
            for floor, ppl in enumerate(self.floors):
                for _ in range(poisson(self.arrival_profile[floor], 1)[0]):
                    self.total_ppl += 1
                    ppl.append(Person.from_range(src=floor, 
                                                dst_range=(0, self.n_floors-1)))
        actions = self.logic(self.elevator_view())
        # first iterate over the elevators that need to move
        # then iterate over the floors to better distribute people
        for action, elevator in zip(actions, self.elevators):
            if isinstance(action, int):
                elevator.move_to_target(action)
            else:
                # opening doors are handled by logic below
                elevator.past.append(action)
        
        def distribute_ppl(elevators: list, people: list):
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
            ppl_up = [person for person in ppl if person.destination > floor]
            ppl_down = [person for person in ppl if person.destination < floor]
            for action, elevator in zip(actions, self.elevators):
                if elevator.loc == floor and isinstance(action, float):
                    self.cost += elevator.release()
                    if action == Constants.OPEN_UP:
                        open_up.append(elevator)
                    elif action == Constants.OPEN_DOWN:
                        open_down.append(elevator)
            distribute_ppl(open_up, ppl_up)
            distribute_ppl(open_down, ppl_down)
            self.floors[floor] = sorted(ppl_up + ppl_down, key=lambda p: p.time)
    
    def elevator_view(self) -> dict:
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
                'floor_buttons' : <list-of-bools-describing-up/down-pressed>
            }
        """
        floor_buttons = self.floor_button_status()
        view = {}
        for i, elevator in enumerate(self.elevators):
            destinations = [(floor in elevator.destinations()) for floor in range(self.n_floors)]
            view.update({f'E{i}' : {'destinations' : destinations, 
                                    'location' : elevator.loc,
                                    'past' : elevator.past}})
        view.update({'floor_buttons': floor_buttons})
        view.update({'n_floors': self.n_floors})
        return view

    def flat_view(self) -> list:
        view = self.elevator_view()
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
        return self.floor_ppl() + self.elevator_ppl()
    
    def floor_ppl(self) -> list:
        people = []
        for floor in self.floors:
            for person in floor:
                people.append(person)
        return people
    
    def elevator_ppl(self) -> list:
        people = []
        for elevator in self.elevators:
            for person in elevator.ppl:
                people.append(person)
        return people
    
    def summarize(self) -> dict:
        """
        Provide a summary of the state so far.

        Returns:
            a dictionary with critical information about the state
        """
        return {
            'time elapsed' : self.time,
            'people arrived' : self.total_ppl,
            'people left over' : len(self.active_ppl()),
            'total cost' : self.total_cost(),
            'average cost' : round(self.total_cost()/self.total_ppl, 3) 
                            if self.total_ppl != 0 else 0
        }

    def floor_button_status(self) -> list:
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
                if not up and person.destination > floor:
                    buttons[2*floor] = True
                    up = True
                elif not down and person.destination < floor:
                    buttons[2*floor+1] = True
                    down = True
                elif up and down:
                    break
        return buttons
    
    def __str__(self) -> str:
        """ just try printing it. """
        buttons = self.floor_button_status()
        rep = '==========================================================\n\n'
        for floor, ppl in enumerate(reversed(self.floors)):
            floor = self.n_floors - floor - 1
            button_str = ''
            up, down = buttons[2*floor], buttons[2*floor + 1]
            up_color_str = Fore.CYAN if up else Style.DIM
            donw_color_str = Fore.CYAN if down else Style.DIM
            button_str = f"{up_color_str}↑{Style.RESET_ALL} {donw_color_str}↓{Style.RESET_ALL}"
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
        rep += f"time = {Fore.CYAN}{self.time}{Style.RESET_ALL}, cost = {self.total_cost()}, active people = {len(self.active_ppl())}\n"
        rep += f"elevator system sees {Fore.CYAN}blue{Style.RESET_ALL}\n"
        rep += "==========================================================\n"
        return rep