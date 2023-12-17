from Elevator import Elevator
from random import randint
import Constants
from Vis import list_to_str as lstr

class State:


    def __init__(self, floors: int = 1, n_elevators: int = 1):
        self.elevators = [Elevator() for _ in range(n_elevators)]
        self.floors = [[] for _ in range(floors)]
        self.time = 0
        self.cost = 0
    
    def update(self):
        self.time += 1
        # TODO generate people
        view = self.view_simple()
        actions = Elevator.move_logic(view)
        for i, move in enumerate(actions):
            elevator = self.elevators[i]
            if move >= 0:
                elevator.move(move)
            else:
                elevator.open(self.floors[elevator.loc])
    
    def view_simple(self) -> dict:
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
            f'elevator{i}' : ({person.dst for person in elevator.ppl}, elevator.loc)
                            for i, elevator in enumerate(self.elevators)
        }
        view.update({'floor_buttons': floor_buttons})
        return view
    
    def __str__(self) -> str:
        rep = "========\n"
        for floor, ppl in enumerate(self.floors):
            floor_rep = (f"floor {floor:02d} | " + lstr(ppl)).ljust(50) + "| "
            for i, elevator in enumerate(self.elevators):
                if elevator.loc == floor:
                    floor_rep += f"[E{i}] " + lstr(elevator.ppl) + ' '
            rep += floor_rep + '\n'
        rep += "========\n"
        return rep