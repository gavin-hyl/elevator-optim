import Constants

def move(view: dict) -> list:
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
        flattened_info = floor_buttons  # fixed size array
        actions = [len(floor_buttons)-1 for _ in enumerate(view)]
        for i, _ in enumerate(view):
            elevator_info = view.get(f"E{i}")
            dests, loc = elevator_info.get('dst'), elevator_info.get('loc')
            flattened_info.extend(dests)
            flattened_info.append(loc)
        move.prev_actions = actions
        return actions

# def move(view: dict) -> list:
#         """
#         Coordinates all the elevators according to the imperfect information it
#         can gather.

#         Args:
#             state_view: the information provided by a State class
#         Returns:
#             a list of the actions for each elevator. Positive numbers indicate
#             the elevator's move targets, while negative numbers indicate open
#             door status. See Constants.py
#         """
#         floor_buttons = view.pop('floor_buttons')
#         flattened_info = floor_buttons  # fixed size array
#         for i, _ in enumerate(view):
#             elevator_info = view.get(f"E{i}")
#             dests, loc, past = elevator_info.get('dst'), elevator_info.get('loc'), elevator_info.get('past')
#             flattened_info.extend(dests)
#             flattened_info.append(loc)
#             try:
#                 move.actions[i] = scan(dests, loc, floor_buttons, move.actions[i])
#             except AttributeError:
#                 move.actions[i] = [Constants.OPEN_UP for _ in enumerate(view)]
#         return move.actions


def scan(destinations: list, location: int, floor_buttons: list, prev_action: int):
    # if not lowest or highest floor
    highest_floor = len(destinations) - 1
    if (location != 0 and location != highest_floor):
        # if floor button is pressed, or it arrives at destination, open the door
        if (floor_buttons[location] or destinations[location]):
            # if prev_action is moving up, open up
            if (prev_action == highest_floor or prev_action == Constants.OPEN_UP):
                return Constants.OPEN_UP
            # if prev_action is moving down, open down
            else:
                return Constants.OPEN_DOWN
        # move with previoud direction
        return highest_floor
    # else, reverse the direction
    else:
        if (location == 0):
            return highest_floor
        else:
            return 0