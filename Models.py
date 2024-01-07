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
        dests, loc, past = info.get('destinations'), info.get('location'), info.get('past')
    return actions

'''
Existing Algorithms
    a. SCAN https://en.wikipedia.org/wiki/Elevator_algorithm
    b. LOOK (and variants): C-LOOK, N-LOOK, F-LOOK, S-LOOK https://en.wikipedia.org/wiki/LOOK_algorithm
'''

def scan(view: dict) -> list[int|float]:

    hall_calls = view.pop('hall_calls')
    n_floors = view.pop('n_floors')
    elevator_v = view.pop('v_max')
    actions = []
    for i, _ in enumerate(view):
        info = view.get(f"E{i}")
        dests, loc, past = info.get('destinations'), info.get('location'), info.get('past')
        loc_index = 0   # get the index of the current location of the elevator
        for ind, b in enumerate(loc):
            if b:
                loc_index = ind
                break
        if (len(past) == 0):
            if (hall_calls[loc_index]):
                actions.append(Constants.OPEN_UP)
            else:
                actions.append(elevator_v)
        else:
            new_act = scan_helper(location=loc_index, highest_floor=n_floors-1, destinations=dests, 
                                  outside_calls=hall_calls, prev_action=past[-1], v_max=elevator_v)
            actions.append(new_act)
    return actions

def scan_helper(location: int, highest_floor: int, destinations: list[bool], outside_calls: list[bool], 
                prev_action: float | int, v_max: int) -> float | int:
    # if not lowest or highest floor
    if (location != 0 and location != highest_floor): 
        # if floor button is pressed with the same direction, or it arrives at destination, open the door
        if (destinations[location]):
            # if prev_action is moving up, open up
            if (prev_action > 0):
                return Constants.OPEN_UP
            # if prev_action is moving down, open down
            else:
                return Constants.OPEN_DOWN
        # if prev_action is moving up, open up
        elif (prev_action > 0 and outside_calls[2 * location]):
            return Constants.OPEN_UP
        # if prev_action is moving down, open down
        elif (prev_action < 0 and outside_calls[2 * location + 1]):
            return Constants.OPEN_DOWN
        # move with previous direction
        else:
            # if previous action moves upward, continuously moving up
            if (prev_action > 0):
                # if reachable calls exist, move to that floor
                highest_v = v_max if (location + v_max <= highest_floor) else (location + v_max - highest_floor)
                for v in range(1, highest_v):
                    if (outside_calls[2 * (location + v)] or destinations[location + v]):
                        return v
                # if no reachable calls, move with max speeed
                return highest_v
            # if previous action moves down, continuously moving down
            else:
                # if reachable calls exist, move to that floor
                highest_v = -1 * v_max if location - v_max >= 0 else -1 * location
                for v in range(1, highest_v):
                    if (outside_calls[2 * (location - v) + 1] or destinations[location - v]):
                        return -1 * v
                # if no reachable calls, move with max speeed
                return highest_v
    # if the elevator reaches the highest / lowest floor
    else:
        # if button pressed
        if (destinations[location]):
            if (location == 0):
                return Constants.OPEN_UP
            else:
                return Constants.OPEN_DOWN
        elif (outside_calls[2 * location+1] and location == 0):
            return Constants.OPEN_UP
        elif (outside_calls[2 * location] and location == highest_floor):
            return Constants.OPEN_DOWN
        # if button is not pressed, reverse the direction
        elif (location == 0):
            # if reachable calls exist, move to that floor
            for v in range(1, v_max):
                # assume that one step cannot move above the highest floor && below the lowest floor
                if (outside_calls[2 * v] or destinations[2 * v]): 
                    return v
            return v_max
        else:
            # if reachable calls exist, move to that floor
            for v in range(1, v_max):
                if (outside_calls[2 * (location - v) + 1] or destinations[location - v]):
                    return -1 * v
            return -1 * v_max

'''
LOOK Algorithm
The LOOK algorithm, similar to the SCAN algorithm, honors requests on both sweep directions of the disk 
head, however, it additionally "looks" ahead to see if there are any requests pending in the direction 
of head movement. If no requests are pending in the direction of head movement, then the disk head 
traversal will be reversed to the opposite direction and requests on the other direction can be served. 
In LOOK scheduling, the arm goes only as far as final requests in each direction and then reverses 
direction without going all the way to the end.
'''

def look(view: dict) -> list:
    hall_calls = view.pop('hall_calls')
    n_floors = view.pop('n_floors')
    elevator_v = view.pop('v_max')
    actions = []
    for i, _ in enumerate(view):
        info = view.get(f"E{i}")
        dests, loc, past = info.get('destinations'), info.get('location'), info.get('past')
        loc_index = 0   # get the index of the current location of the elevator
        for ind, b in enumerate(loc):
            if b:
                loc_index = ind
                break


def look_helper(location: int, highest_floor: int, destinations: list[bool], outside_calls: list[bool], 
                prev_action: float | int, v_max: int) -> float | int:
    # if not lowest or highest floor
    if (location != 0 and location != highest_floor): 
        # if floor button is pressed with the same direction, or it arrives at destination, open the door
        if (destinations[location]):
            # if prev_action is moving up, open up
            if (prev_action > 0):
                return Constants.OPEN_UP
            # if prev_action is moving down, open down
            else:
                return Constants.OPEN_DOWN
        # if prev_action is moving up, open up
        elif (prev_action > 0 and outside_calls[2 * location]):
            return Constants.OPEN_UP
        # if prev_action is moving down, open down
        elif (prev_action < 0 and outside_calls[2 * location + 1]):
            return Constants.OPEN_DOWN
        # move with previous direction
        else:
            # if previous action moves upward, continuously moving up
            if (prev_action > 0):
                # if reachable calls exist, move to that floor
                highest_v = v_max if (location + v_max <= highest_floor) else (location + v_max - highest_floor)
                for v in range(1, highest_v + 1):
                    if (outside_calls[2 * (location + v)] or destinations[location + v]):
                        return v
                # if no reachable calls, check if there's call ahead
                new_direction = -1 # default: moving down
                for loc in range(location+v_max+1, highest_floor+1):
                    if (outside_calls[2 * loc] or destinations[loc]):
                        new_direction *= -1
                        break
                if (new_direction < 0): # change direction to moving down
                    reverse_direction(location, highest_floor, destinations, outside_calls, new_direction, v_max)
                # move with max speeed
                else:
                    return v_max
            # if previous action moves down, continuously moving down
            else:
                # if reachable calls exist, move to that floor
                highest_v = -1 * v_max if location - v_max >= 0 else -1 * location
                for v in range(1, highest_v):
                    if (outside_calls[2 * (location - v) + 1] or destinations[location - v]):
                        return -1 * v
                # if no reachable calls, move with max speeed
                return highest_v
    # if the elevator reaches the highest / lowest floor
    else:
        # if button pressed
        if (outside_calls[location] or destinations[location]):
            if (location == 0):
                return Constants.OPEN_UP
            else:
                return Constants.OPEN_DOWN
        # if button is not pressed, reverse the direction
        elif (location == 0):
            # if reachable calls exist, move to that floor
            for v in range(1, v_max):
                # assume that one step cannot move above the highest floor && below the lowest floor
                if (outside_calls[2 * v] or destinations[2 * v]): 
                    return v
            return v_max
        else:
            # if reachable calls exist, move to that floor
            for v in range(1, v_max):
                if (outside_calls[2 * (location - v) + 1] or destinations[location - v]):
                    return -1 * v
            return -1 * v_max

def reverse_direction(location: int, highest_floor: int, destinations: list[bool], outside_calls: list[bool], 
                      new_direction: int, v_max: int) -> float | int:
    if (new_direction > 0):
        highest_v = v_max if (location + v_max <= highest_floor) else (location + v_max - highest_floor)
        # if reachable calls exist, move to that floor
        for v in range(1, highest_v):
            # assume that one step cannot move above the highest floor && below the lowest floor
            if (outside_calls[2 * v] or destinations[2 * v]): 
                return v
        return highest_v
    else:
        highest_v = -1 * v_max if location - v_max >= 0 else -1 * location
        # if reachable calls exist, move to that floor
        for v in range(1, highest_v):
            if (outside_calls[2 * (location - v) + 1] or destinations[location - v]):
                return -1 * v
        return -1 * highest_v