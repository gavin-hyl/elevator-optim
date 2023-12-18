from Elevator import Elevator
from Person import Person
from State import State

def main():
    # Test script
    state = State(floors=5)
    print(state)
    while input('(any key for next, ctrl+C to stop)') is not None:
        state.update()
        print(state)

if __name__ == "__main__":
    main()