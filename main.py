from State import State
from time import sleep
import os
from Vis import print_summary

TEST_CYCLES = 30
CYCLE_DELAY_S = 1
N_FLOORS = 8
N_ELEVATORS = 3
AVG_PPL_PER_TICK = 0.3

def main():
    os.system('cls')
    state = State(floors=N_FLOORS,
                  n_elevators=N_ELEVATORS,
                  avg_ppl=AVG_PPL_PER_TICK)
    try:
        for _ in range(TEST_CYCLES):
            state.update()
            print(state)
            sleep(CYCLE_DELAY_S)
            os.system('cls')
        while len(state.active_ppl()) != 0:
            state.update(add_ppl=False)
            print(state)
            sleep(CYCLE_DELAY_S)
            os.system('cls')
    except KeyboardInterrupt:
        pass
    print_summary(state.summarize())

if __name__ == "__main__":
    main()