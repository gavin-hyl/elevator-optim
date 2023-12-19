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
        actions = [Constants.OPEN_UP for _ in enumerate(view)]
        for i, _ in enumerate(view):
            elevator_info = view.get(f"E{i}")
            dests, loc = elevator_info.get('dst'), elevator_info.get('loc')
            flattened_info.extend(dests)
            flattened_info.append(loc)
        move.prev_actions = actions
        return actions