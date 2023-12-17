def list_to_str(target: list):
    rep = ''
    if len(target) == 0:
        return '(empty)'
    for i, element in enumerate(target):
        rep += str(element)
        if i != len(target) - 1:
            rep += ', '
    return rep