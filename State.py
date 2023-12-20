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
            if move >= 0:
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
                    elif actions[i] == Constants.OPEN_DOWN:
                        open_down.append(elevator)
                        self.cost += elevator.release()
            if len(open_up) > 1:
                for person in ppl_up:
                    open_up.sort(key=lambda e: len(e.ppl))
                    if open_up[0].add(people=[person]) != 0:
                        ppl_up.remove(person)
                    else:   # all the elevators are full
                        break
            elif len(open_up) == 1:
                open_up[0].add(people=ppl_up)
            if len(open_down) > 1:
                for person in ppl_down:
                    open_down.sort(key=lambda e: len(e.ppl))
                    if open_down[0].add(people=[person]) != 0:
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
            elevator_dests = [False for _ in self.floors]
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
    
    def summarize(self) -> dict:
        return {
            'time elapsed' : self.time,
            'people serviced' : self.total_ppl,
            'people leftover' : len(self.active_ppl()),
            'average cost' : round( self.cum_cost() / self.total_ppl, 3)
        }

    def floor_buttons(self) -> list:
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
        return floor_buttons
    
    def __str__(self) -> str:
        floor_buttons = self.floor_buttons()
        rep = "========\n"
        for floor, ppl in enumerate(reversed(self.floors)):
            floor = self.n_floors - floor - 1
            button_state = floor_buttons[floor]
            if button_state == Constants.UP_DOWN_REQ:
                button_str = f"{Style.BRIGHT}↑ ↓{Style.RESET_ALL}"
            elif button_state == Constants.UP_REQ:
                button_str = f"{Style.BRIGHT}↑{Style.RESET_ALL} {Style.DIM}↓{Style.RESET_ALL}"
            elif button_state == Constants.DOWN_REQ:
                button_str = f"{Style.DIM}↑{Style.RESET_ALL} {Style.BRIGHT}↓{Style.RESET_ALL}"
            else:
                button_str = f"{Style.DIM}↑ ↓{Style.RESET_ALL}"
            rep += f"floor {Fore.GREEN}{floor+1:02d}{Style.RESET_ALL} {button_str} | " + Vis.ppl_list(ppl).ljust(100) + "| "
            for i, elevator in enumerate(self.elevators):
                if elevator.loc == floor:
                    rep += f"{Fore.BLUE}[E{i} ({elevator.dests()})]{Style.RESET_ALL} " + Vis.ppl_list(elevator.ppl) + ' '
            rep += '\n\n'
        rep += "--------\n"
        rep += f"({Style.BRIGHT}time={self.time}, cost={self.cum_cost()}, ppl={self.total_ppl}{Style.NORMAL})\n"
        rep += "========\n"
        return rep