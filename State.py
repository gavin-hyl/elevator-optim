from Elevator import Elevator
from random import randint
import Constants


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
        """
        0. update time
        1. generate people
        2. open doors
        3. update buttons
        4. move elevators
        """
    
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
            f'elevator{i}' : ([person.dst for person in elevator.ppl], elevator.loc)
                            for i, elevator in enumerate(self.elevators)
        }
        view.update({'floor_buttons': floor_buttons})
        return view
    
    def __str__(self) -> str:
        rep = "========\n"

        for floor, ppl in enumerate(self.floors):
            rep += f"floor {floor:02d} | "
            if len(ppl) == 0:
                rep += "(empty)\n"
                continue
            for person in ppl:
                rep += str(person) + " "
            rep += "\n"
        rep += "--------\n"
        for elevator in self.elevators:
            rep += str(elevator) + "\n"
        
        rep += "========\n"
        return rep