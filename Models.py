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
        floor_buttons = view.pop('hall_calls')
        n_floors = view.pop('n_floors')
        # test: all the elevators are instructed to go to the top floor
        actions = [Constants.OPEN_UP for _ in enumerate(view)]
        for i, _ in enumerate(view):
            info = view.get(f"E{i}")
            dests, loc, past = info.get('destination'), info.get('loc'), info.get('past')
        return actions

