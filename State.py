from Elevator import Elevator
from Person import Person
from random import randint
import Constants
from numpy.random import poisson
import os
from Vis import list_to_str as lstr

class State:


    def __init__(self, floors: int = 1, n_elevators: int = 1, avg_ppl: int = 0.1):
        self.elevators = [Elevator() for _ in range(max(1, n_elevators))]
        self.floors = [[] for _ in range(max(1, floors))]
        self.time = 0
        self.cost = 0
        self.avg_ppl = max(0, avg_ppl)
    
    def update(self):
        self.time += 1
        for person in self:
            person.step_time()
        self.generate_ppl()
        view = self.view_simple()
        actions = Elevator.move_logic(view)
        for i, move in enumerate(actions):
            elevator = self.elevators[i]
            if move >= 0:
                elevator.move(move)
            else:
                self.cost += elevator.open(self.floors[elevator.loc])

    
    def view_simple(self) -> dict:
        '''
        Returns a dictionary of the available information for the move logic
        implementation. That function is implemented in the Elevator class to
        prevent it from accessing information that is unknowable in reality, 
        such as the number of people on a floor.
        '''
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
            f'E{i}' : ({person.dst for person in elevator.ppl},
                       elevator.loc)
                            for i, elevator in enumerate(self.elevators)
        }
        view.update({'floor_buttons': floor_buttons})
        return view

    def generate_ppl(self):
        for i, floor in enumerate(self.floors):
            for _ in range(poisson(self.avg_ppl, 1)[0]):
                floor.append(Person.from_range(i, (0, len(self.floors))))

    def cum_cost(self):
        cost = 0
        for person in self:
            cost += person.cost()
        return cost + self.cost
        
    def __iter__(self):
        ''' I know an iterator is unnecessary but hey, its fun! '''
        self.ppl = []
        for floor in self.floors:
            for person in floor:
                self.ppl.append(person)
        for elevator in self.elevators:
            for person in elevator.ppl:
                self.ppl.append(person)
        return self
    
    def __next__(self):
        if self.ppl:
            return self.ppl.pop(-1)
        raise StopIteration
    
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