from colorama import Style
from colorama import Fore

def pretty_list(target: list, lim: int = 60):
    rep = ''
    if len(target) == 0:
        return ''
    for i, person in enumerate(target):
        rep += str(person)
        if i != len(target) - 1:
            rep += ', '
        if len(rep) > lim:
            return pretty_list(target[:2], 999) + f" ... ({len(target) - 4} more), " + pretty_list(target[-2:], 999)
    return rep

def pretty_dict(summary: dict) -> None:
    print(f"\n#=============={Fore.BLUE}Summary{Style.RESET_ALL}==============#")
    for key, val in summary.items():
        print("| " + key.ljust(20) + "| " + str(val).ljust(12) + "|")
    print("#===================================#\n")
    