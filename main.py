from State import State
from Vis import pretty_dict
from time import sleep
import Constants
import os
import time
import multiprocessing

def simulate(state: State = State(),
            test_cycles: int = Constants.N_STEPS,
            max_linger: int = Constants.N_TRAILING_STEPS,
            cycle_print_delay: float = Constants.PRINT_DELAY_S,
            show: bool = True) -> float:
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
    if show:
        pretty_dict(state.summarize())

def simulate_full():
    state = State(logic=None,
                    floors=Constants.N_FLOORS,
                    n_elevators=Constants.N_ELEVATORS,
                    avg_ppl=Constants.AVG_PPL_PER_FLOOR_TICK)
    simulate(state, max_linger=0, show=False)

TEST_CYCLES = 10000

def single():
    start = time.perf_counter()
    for _ in range(TEST_CYCLES):
        simulate_full()
    end = time.perf_counter()
    print(f'single = {(end-start)/TEST_CYCLES * 1000 :.3f} ms')

def multi():
    cpu_cnt = multiprocessing.cpu_count()
    start = time.perf_counter()
    processes = []
    def core_repeat():
        for _ in range(int(TEST_CYCLES / cpu_cnt)):
            simulate_full()
    # initiate processes
    for _ in range(cpu_cnt):
        core_task = multiprocessing.Process(target=core_repeat())
        core_task.start()
        processes.append(core_task)
    # wait for all to finish
    for process in processes:
        process.join()
    end = time.perf_counter()
    print(f'multi = {(end-start)/TEST_CYCLES * 1000 :.3f} ms')


if __name__ == "__main__":
    single()    # approximately 1.9 ms per 20-step simulation * 10000
    multi()     # approximately 1.5 ms per 20-step simulation * 10000

"""
If the agent logic is efficient, 1 step will be approximately 2 ms / 20 = 0.1 ms.

Using 10 agents, each looking ahead 2 steps (1296 choices for 2 elevators) and calculating 5 steps in total,
We have 10 * 1296 * 5 = 64,800 moves per sample, approximately 6.5 seconds. However,
if we simply take each new step as a new data point with decreased credibility, the average time for obtaining
1 data point would be simply 10 * 1296 * 1e-4 = 1.3 seconds. Obtaining 10000 samples will take about three hours.

It should be noted that the method of storing the results would greatly influence this speed.

Thankfully, training the network will be extremely fast (a few minutes).
"""