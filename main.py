from State import State
from time import sleep
import os

TEST_CYCLES = 30
CYCLE_DELAY_S = 1

def main():
    # Test script
    os.system('cls')
    state = State(floors=5, n_elevators=2)
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
    print(state.summarize())

if __name__ == "__main__":
    main()