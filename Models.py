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
        dests, loc_index, past = info.get('destinations'), info.get('location'), info.get('past')
        
        if (len(past) == 0): # assume the elevator starts from floor 0
            if (hall_calls[loc_index].up):
                actions.append(Constants.OPEN_UP)
            else:
                actions.append(elevator_v)
        else:
            new_act = scan_helper(location=loc_index, highest_floor=n_floors-1, destinations=dests, 
                                  outside_calls=hall_calls, prev_action=past[-1], v_max=elevator_v)
            actions.append(new_act)
    return actions

def scan_helper(location: int, highest_floor: int, destinations: list[bool], outside_calls: list, 
                prev_action: float | int, v_max: int) -> float | int:
    if (location != 0 and location != highest_floor): 
        # if floor button is pressed with the same direction, or it arrives at destination, open the door
        if (destinations[location]):
            if (prev_action > 0):
                return Constants.OPEN_UP
            else:
                return Constants.OPEN_DOWN
        elif (prev_action > 0 and (outside_calls[location]).up):
            return Constants.OPEN_UP
        elif (prev_action < 0 and outside_calls[location].dn):
            return Constants.OPEN_DOWN
        # move with previous direction
        else:
            if (prev_action > 0):
                # if reachable calls exist, move to that floor
                highest_v = v_max if (location + v_max <= highest_floor) else (location + v_max - highest_floor)
                for v in range(1, highest_v):
                    if (outside_calls[location + v].up or destinations[location + v]):
                        return v
                # if no reachable calls, move with max speed
                return highest_v
            else:
                # if reachable calls exist, move to that floor
                highest_v = v_max if location - v_max >= 0 else location
                for v in range(1, highest_v):
                    if (outside_calls[location - v].dn or destinations[location - v]):
                        return -1 * v
                # if no reachable calls, move with max speed
                return -1 * highest_v
    else:
        # if button pressed
        if (destinations[location]):
            if (location == 0):
                return Constants.OPEN_UP
            else:
                return Constants.OPEN_DOWN
        elif (outside_calls[location].up):
            return Constants.OPEN_UP
        elif (outside_calls[location].dn):
            return Constants.OPEN_DOWN
        # if button is not pressed, reverse the direction
        elif (location == 0):
            # if reachable calls exist, move to that floor
            for v in range(1, v_max):
                # assume that one step cannot move above the highest floor && below the lowest floor
                if (outside_calls[v].up or destinations[v]): 
                    return v
            return v_max
        else:
            # if reachable calls exist, move to that floor
            for v in range(1, v_max):
                if (outside_calls[location - v].dn or destinations[location - v]):
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

def look(view: dict) -> list[int|float]:
    hall_calls = view.pop('hall_calls')
    n_floors = view.pop('n_floors')
    elevator_v = view.pop('v_max')
    actions = []
    for i, _ in enumerate(view):
        info = view.get(f"E{i}")
        dests, loc_index, past = info.get('destinations'), info.get('location'), info.get('past')
        if (len(past) == 0):
            if (hall_calls[loc_index].up):
                actions.append(Constants.OPEN_UP)
            else:
                actions.append(elevator_v)
        else:
            new_act = look_helper(location=loc_index, highest_floor=n_floors-1, destinations=dests, 
                                  outside_calls=hall_calls, prev_action=past[-1], v_max=elevator_v)
            actions.append(new_act)
    return actions


def look_helper(location: int, highest_floor: int, destinations: list[bool], outside_calls: list[bool], 
                prev_action: float | int, v_max: int) -> float | int:
    # if not lowest or highest floor
    if (location != 0 and location != highest_floor): 
        # if floor button is pressed with the same direction, or it arrives at destination, open the door
        if (destinations[location]):
            if (prev_action > 0):
                return Constants.OPEN_UP
            else:
                return Constants.OPEN_DOWN
        # if prev_action is moving up, open up
        elif (prev_action > 0 and outside_calls[location].up): # TODO: 反方向hall call
            return Constants.OPEN_UP
        # if prev_action is moving down, open down
        elif (prev_action < 0 and outside_calls[location].dn):
            return Constants.OPEN_DOWN
        # if no calls with the same direction ahead, check if opposite direction call exists
        elif (prev_action > 0  and outside_calls[location].dn):
            same_direction = False # call with the same direction?
            for loc in range(location, highest_floor+1):
                if (outside_calls[loc].up or destinations[loc]):
                    same_direction = True
                    break
            if (not same_direction):
                return Constants.OPEN_DOWN
            else:
                return move_with_dir(location, highest_floor, destinations, outside_calls, prev_action, v_max)
        elif (prev_action < 0 and outside_calls[location].up):
            same_direction = False # call with the same direction?
            for loc in range(0, location+1):
                if (outside_calls[loc].dn or destinations[loc]):
                    same_direction = True
                    break
            if (not same_direction):
                return Constants.OPEN_UP
            else: # TODO: 继续往下走
                return move_with_dir(location, highest_floor, destinations, outside_calls, prev_action, v_max)
        else: # no call on this floor
            # if previous action moves upward, continuously moving up
            if (prev_action > 0):
                # if reachable calls exist, move to that floor
                highest_v = v_max if (location + v_max <= highest_floor) else (location + v_max - highest_floor)
                for v in range(1, highest_v + 1): # highest_v included
                    if (outside_calls[location + v].up or destinations[location + v]):
                        return v
                # if no reachable calls, check if there's call ahead
                change_direction = True
                same_direction = False
                for loc in range(location, highest_floor+1):
                    if (outside_calls[loc].up or outside_calls[loc].dn or destinations[loc]):
                        change_direction = False # TODO: 什么时候更换方向？
                        if (outside_calls[loc].up or destinations[loc]):
                            same_direction = True
                            break
                if (change_direction): # change direction to moving down
                    return move_with_dir(location, highest_floor, destinations, outside_calls, -1, v_max)
                # move with max speeed
                else:
                    if (same_direction):
                        return highest_v
                    else:
                        for v in range(1, highest_v):
                            if (outside_calls[location + v].dn):
                                return v
                    return highest_v
            # if previous action moves down, continuously moving down
            else:
                # if reachable calls exist, move to that floor
                highest_v = v_max if location - v_max >= 0 else location
                for v in range(1, highest_v+1):
                    if (outside_calls[location - v].dn or destinations[location - v]):
                        return -1 * v
                # if no reachable calls, check if there's call ahead
                change_direction = True
                same_direction = False
                for loc in range(0, location+1):
                    if (outside_calls[loc].up or outside_calls[loc].dn or destinations[loc]):
                        change_direction = False # TODO: same question
                        if (outside_calls[loc].dn or destinations[loc]):
                            same_direction = True
                            break
                if (change_direction): # change direction to moving up
                    return move_with_dir(location, highest_floor, destinations, outside_calls, 1, v_max)
                # move with max speeed
                else:
                    if (same_direction):
                        return -1 * highest_v
                    else:
                        for v in range(1, highest_v):
                            if (outside_calls[location].up):
                                return -1 * v
                        return -1 * highest_v
    # if the elevator reaches the highest / lowest floor
    else:
        # if button pressed
        if (destinations[location]):
            if (location == 0):
                return Constants.OPEN_UP
            else:
                return Constants.OPEN_DOWN
        elif (outside_calls[location].up):
            return Constants.OPEN_UP
        elif (outside_calls[location].dn):
            return Constants.OPEN_DOWN
        elif (location == 0):
            # if reachable calls exist, move to that floor
            for v in range(1, v_max):
                # assume that one step cannot move above the highest floor && below the lowest floor
                if (outside_calls[v].up or destinations[v]): 
                    return v
            return v_max
        else:
            # if reachable calls exist, move to that floor
            for v in range(1, v_max):
                if (outside_calls[location - v].dn or destinations[location - v]):
                    return -1 * v
            return -1 * v_max
        

# move with previous direction
def move_with_dir(location: int, highest_floor: int, destinations: list[bool], outside_calls: list[bool], 
                    direction: float, v_max: int) -> float | int:
    # if previous action moves upward, continuously moving up
    if (direction > 0):
        # if reachable calls exist, move to that floor
        highest_v = v_max if (location + v_max <= highest_floor) else (location + v_max - highest_floor)
        for v in range(1, highest_v + 1): # highest_v included
            if (outside_calls[location + v].up or destinations[location + v]):
                return v
        # move with max speeed
        else:
            return highest_v
    else:
        highest_v = v_max if location - v_max >= 0 else location
        # if reachable calls exist, move to that floor
        for v in range(1, highest_v):
            if (outside_calls[location - v].dn or destinations[location - v]):
                return -1 * v
        return -1 * highest_v

'''
C-LOOK
the head services request only in one direction(either left or right) until all 
the requests in this direction are not serviced and then jumps back to the farthest
request in the other direction and services the remaining requests which gives a 
better uniform servicing as well as avoids wasting seek time for going till the 
end of the disk.
'''

def c_look(view: dict) -> list[int|float]:
    hall_calls = view.pop('hall_calls')
    n_floors = view.pop('n_floors')
    elevator_v = view.pop('v_max')
    actions = []
    for i, _ in enumerate(view):
        info = view.get(f"E{i}")
        dests, loc_index, past = info.get('destinations'), info.get('location'), info.get('past')
        if (len(past) == 0):
            if (hall_calls[loc_index].up):
                actions.append(Constants.OPEN_UP)
            else:
                actions.append(elevator_v)
        else:
            new_act = look_helper(location=loc_index, highest_floor=n_floors-1, destinations=dests, 
                                  outside_calls=hall_calls, prev_action=past[-1], v_max=elevator_v)
            actions.append(new_act)
    return actions