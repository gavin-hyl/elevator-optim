from Elevator import Elevator
import Logic
from Person import Person
import Constants
from numpy.random import poisson
import numpy as np
import Vis
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

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
        self.n_floors = max(1, floors)
        self.floors = [[] for _ in range(self.n_floors)]
        self.time = 0
        self.total_ppl = 0
        self.cost = 0
        self.avg_ppl = max(0, avg_ppl)
        self.arrival_profile = [self.avg_ppl for _ in range(self.n_floors)]
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
        view = self.view_simple()
        actions = Logic.move(view)
        # first iterate over the elevators that need to move
        # then iterate over the floors to better distribute people boarding
        for i, move in enumerate(actions):
            if isinstance(move, int):
                self.elevators[i].move(move)
        for floor, ppl in enumerate(self.floors):
            # people will automatically board the elevator with least passengers
            if len(ppl) == 0:
                continue
            open_up = []
            open_down = []
            ppl_up = [person for person in ppl if person.dst > floor]
            ppl_down = [person for person in ppl if person.dst < floor]
            for i, elevator in enumerate(self.elevators):
                if elevator.loc == floor:
                    if actions[i] == Constants.OPEN_UP:
                        open_up.append(elevator)
                        self.cost += elevator.release()
                        elevator.past.append(Constants.OPEN_UP)
                    elif actions[i] == Constants.OPEN_DOWN:
                        open_down.append(elevator)
                        self.cost += elevator.release()
                        elevator.past.append(Constants.OPEN_DOWN)
            if len(open_up) > 1:
                # the people are filled into the elevators with the least ppl onboard
                for person in ppl_up:
                    least_filled_elevator = min(open_up, key=lambda e: len(e.ppl))
                    if least_filled_elevator.add(people=[person]) != 0:
                        ppl_up.remove(person)
                    else:   # all the elevators are full
                        break
            elif len(open_up) == 1:
                open_up[0].add(people=ppl_up)
            if len(open_down) > 1:
                for person in ppl_down:
                    least_filled_elevator = min(open_down, key=lambda e: len(e.ppl))
                    if least_filled_elevator.add(people=[person]) != 0:
                        ppl_down.remove(person)
                    else:   # all the elevators are full
                        break
            elif len(open_down) == 1:
                open_down[0].add(people=ppl_down)
            self.floors[floor] = sorted(ppl_up + ppl_down, key=lambda p: p.time)
            # self.floors[floor].extend(ppl_down)
    
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
        floor_buttons = self.floor_buttons()
        view = {}
        for i, elevator in enumerate(self.elevators):
            dests = [(floor in elevator.dests()) for floor in range(self.n_floors)]
            view.update({f'E{i}' : {'dst' : dests, 
                                    'loc' : elevator.loc,
                                    'past' : elevator.past}})
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
            'total cost' : self.cum_cost(),
            'average cost' : round(self.cum_cost()/self.total_ppl, 3) 
                            if self.total_ppl != 0 else 0
        }

    def floor_buttons(self) -> list:
        """
        Check the floor buttons' statuses based on the people on that floor.

        Returns:
            a list of integers describing the floor buttons
        """
        buttons = []
        for floor, ppl in enumerate(self.floors):
            up, down = False, False
            buttons.append(Constants.NO_REQ)
            # check people's destinations one by one
            for person in ppl:
                if not up and person.dst > floor:
                    buttons[floor] += Constants.UP_REQ 
                    up = True
                elif not down and person.dst < floor:
                    buttons[floor] += Constants.DOWN_REQ
                    down = True
                elif up and down:
                    break
        return buttons
    
    def __str__(self) -> str:
        """ just try printing it. """
        floor_buttons = self.floor_buttons()
        rep = '==========================================================\n\n'
        for floor, ppl in enumerate(reversed(self.floors)):
            floor = self.n_floors - floor - 1
            button_state = floor_buttons[floor]
            if button_state == Constants.UP_DOWN_REQ:
                button_str = f"{Fore.CYAN}↑ ↓{Style.RESET_ALL}"
            elif button_state == Constants.UP_REQ:
                button_str = f"{Fore.CYAN}↑{Style.RESET_ALL} {Style.DIM}↓{Style.RESET_ALL}"
            elif button_state == Constants.DOWN_REQ:
                button_str = f"{Style.DIM}↑{Style.RESET_ALL} {Fore.CYAN}↓{Style.RESET_ALL}"
            else:
                button_str = f"{Style.DIM}↑ ↓{Style.RESET_ALL}"
            rep += f"floor {Fore.CYAN}{floor:02d}{Style.RESET_ALL} {button_str} | " + Vis.list_no_brackets(ppl).ljust(100) + "| "
            for i, elevator in enumerate(self.elevators):
                if elevator.loc == floor:
                    elevator_dest_str = Vis.list_no_brackets(elevator.dests())
                    if len(elevator_dest_str) != 0:
                        elevator_dest_str = ' → ' + elevator_dest_str
                    rep += f"{Fore.CYAN}[E{i}{elevator_dest_str}]{Style.RESET_ALL} " + Vis.list_no_brackets(elevator.ppl) + ' '
            rep += '\n\n'
        rep += "----------------------------------------------------------\n"
        for i, elevator in enumerate(self.elevators):
            elevator_dest_str = Vis.list_no_brackets(elevator.dests())
            if len(elevator_dest_str) != 0:
                elevator_dest_str = '→ ' + elevator_dest_str + ' '
            rep += f'{Fore.CYAN}elevator {i} @ floor {elevator.loc:02d} {elevator_dest_str}{Style.RESET_ALL}| {Vis.list_no_brackets(elevator.ppl)}\n'
            rep += f"{Fore.CYAN}\tpast: {elevator.past}{Style.RESET_ALL}\n"
        rep += "----------------------------------------------------------\n"
        rep += f"time = {Fore.CYAN}{self.time}{Style.RESET_ALL}, cost = {self.cum_cost()}, active people = {len(self.active_ppl())}\n"
        rep += f"elevator system sees {Fore.CYAN}blue{Style.RESET_ALL}\n"
        rep += "==========================================================\n"
        return rep