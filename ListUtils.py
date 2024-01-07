def list_subtract(a: list, b: list):
    return [x for x in a if x not in b]

def list_intersect(a: list, b: list):
    return [x for x in a if x in b]