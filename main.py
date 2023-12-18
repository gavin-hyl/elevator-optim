from Elevator import Elevator
from Person import Person
from State import State

def main():
    elevator1 = Elevator()
    person = Person()
    person2 = Person(3)
    person3 = Person()
    state = State(5)
    # print(person)
    person.check_arrived(2)
    # print(person)
    # print(elevator1)

    state.floors[0].append(person)
    state.floors[0].append(person3)
    state.floors[4].append(person2)
    # print(state)
    # print(state.view_simple())
    # state.elevators[0].open(state.floors[0])
    # print(state)
    # state.elevators[0].move(1)
    # state.elevators[0].open(state.floors[1])
    # print(state)
    # print(state.view_simple())

    print("----------------------------")
    state.update()
    print(state)
    state.update()
    print(state)
    state.elevators[0].move(1)
    print(state)
    state.cost += state.elevators[0].open([])
    print(state)

if __name__ == "__main__":
    main()