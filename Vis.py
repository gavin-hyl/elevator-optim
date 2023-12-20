from colorama import Style
from colorama import Fore

def list_no_brackets(target: list):
    rep = ''
    if len(target) == 0:
        return ''
    for i, person in enumerate(target):
        rep += str(person)
        if i != len(target) - 1:
            rep += ', '
    return rep

def print_summary(summary: dict) -> None:
    print(f"\n#=============={Fore.BLUE}Summary{Style.RESET_ALL}==============#")
    for key, val in summary.items():
        print("| " + key.ljust(20) + "| " + str(val).ljust(12) + "|")
    print("#===================================#\n")
    