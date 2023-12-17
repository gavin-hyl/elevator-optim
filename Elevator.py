import Constants


class Elevator:


    MAX_PEOPLE_DEFAULT = 20
    MAX_V_DEFAULT = 1

    def __init__(self, speed=MAX_V_DEFAULT, max=MAX_PEOPLE_DEFAULT):
        '''
        Create an elevator object at floor 0 and no people inside.
        '''
        self.ppl = []
        self.loc = 0
        self.v_max = speed
        self.ppl_max = max
    
    def open(self, people):
        '''
        Open the elevator doors. 
        '''
        total_cost = 0
        for person in reversed(self.ppl):   # fixes indexing issues stemming from popping elements
            if self.loc == person.dst:
                self.ppl.remove(person)
            total_cost += person.update(self.loc)
        n_board = min(self.ppl_max - len(self.ppl), len(people))
        for _ in range(n_board):
            self.ppl.append(people.pop(0))  # TODO boarding order issues
        
        return total_cost
        
    def move(self, target: int = 0):
        if abs(target - self.loc) < self.v_max:
            self.loc = target
        elif target > self.loc:
            self.loc += self.v_max
        else:
            self.loc -= self.v_max
    
    def move_logic(state_view: dict):
        '''
        Coordinates all elevators' movements in state_view.
        The heart of the algorithm.
        '''
        
    
    def end(self) -> int:
        total_cost = 0
        for person in self.ppl:
            total_cost += person.update(person.dst)
        return total_cost

    def __str__(self) -> str:
        rep = "elevator | "
        if len(self.ppl) == 0:
            rep += "(empty) "
        else:
            for person in self.ppl:
                rep += str(person) + " "
        rep += f"@ floor {self.loc:02d}"
        return rep

    def verbose(self) -> str:
        return f"{self.ppl} | loc = {self.loc} | max speed = {self.v_max} | max passengers = {self.ppl_max}"