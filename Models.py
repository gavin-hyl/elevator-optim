import Constants

def default(view: dict) -> list:
        """
        Coordinates all the elevators according to the imperfect information it
        can gather.

        Args:
            state_view: the information provided by a State class
        Returns:
            a list of the actions for each elevator. Positive numbers indicate
            the elevator's move targets, while negative numbers indicate open
            door status. See Constants.py
        """
        floor_buttons = view.pop('floor_buttons')
        n_floors = view.pop('n_floors')
        # test: all the elevators are instructed to go to the top floor
        actions = [Constants.OPEN_UP for _ in enumerate(view)]
        for i, _ in enumerate(view):
            info = view.get(f"E{i}")
            dests, loc, past = info.get('destination'), info.get('loc'), info.get('past')
        return actions

def scan(destinations, location, floor_buttons, prev_action):
    highest_floor = len(destinations)-1
    # if not lowest or highest floor
    if (location != 0 and location != highest_floor):
        # if floor button is pressed, or it arrives at destination, open the door
        if (floor_buttons[location] or destinations[location]):
            # if prev_action is moving up, open up
            if (prev_action == highest_floor or prev_action == Constants.OPEN_UP):
                return Constants.OPEN_UP
            # if prev_action is moving down, open down
            else:
                return Constants.OPEN_DOWN
        # move with previous direction
        
    # else, reverse the direction
    else:
        if (location == 0):
            return len(destinations)-1
        else:
            return 0
print("test")