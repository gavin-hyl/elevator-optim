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

"""
Sandy's work

1. Existing Algorithms
    a. SCAN https://en.wikipedia.org/wiki/Elevator_algorithm
    b. LOOK (and variants): C-LOOK, N-LOOK, F-LOOK, S-LOOK https://en.wikipedia.org/wiki/LOOK_algorithm

2. Dataset Generation

If the agent logic is efficient, 1 step will be approximately 2 ms / 20 = 0.1 ms.

Using 10 simulated annealing (https://en.wikipedia.org/wiki/Simulated_annealing) agents,
each looking ahead 2 steps (1296 choices for 2 elevators) and calculating 5 steps in total,
We have 10 * 1296 * 5 =  approximately 6.5 seconds. However,
if we simply take each new step as a new data point with decreased credibility, the average time for obtaining
1 data point would be simply 10 * 1296 * 1e-4 = 1.3 seconds. Obtaining 10000 samples will take about three hours.

It should be noted that the method of storing the results would greatly influence this speed.

Thankfully, training the network will be extremely fast (a few minutes).
"""