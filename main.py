from State import State
from Vis import pretty_dict
from time import sleep
import Constants
import os

def simulate(state: State = State(),
            test_cycles: int = Constants.N_STEPS,
            max_linger: int = Constants.N_TRAILING_STEPS,
            cycle_print_delay: float = Constants.PRINT_DELAY_S,
            show: bool = True) -> float:
    os.system('cls')
    try:
        for _ in range(test_cycles):
            if show:
                os.system('cls')
                print(state)
                sleep(cycle_print_delay)
            state.update()
        counter = 0
        while len(state.active_ppl()) != 0 and counter < max_linger:
            if show:
                os.system('cls')
                print(state)
                sleep(cycle_print_delay)
            state.update(add_ppl=False)
            counter += 1
    except KeyboardInterrupt:
        pass
    pretty_dict(state.summarize())

def main():
    state = State(logic=None,
                floors=Constants.N_FLOORS,
                n_elevators=Constants.N_ELEVATORS,
                avg_ppl=Constants.AVG_PPL_PER_FLOOR_TICK)
    # simulate(state, max_linger=0, show=True)
    simulate(state, max_linger=0, show=True)

if __name__ == "__main__":
    main()