from colorama import Style
from colorama import Fore
import string

def ppl_list(target: list):
    rep = ''
    if len(target) == 0:
        return ''
    for i, person in enumerate(target):
        rep += str(person)
        if i != len(target) - 1:
            rep += ', '
    return rep

def custom_justify(target:str, n_justify:int) -> str:
    # text_size = len([c for c in target if c in string.printable])
    # text_size = len([c for c in target])
    text_size = len(target)
    if text_size < n_justify:
        for _ in range(n_justify - text_size - 1):
            target += ' '
    return target