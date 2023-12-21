import pygad.nn
import pygad.gann
from State import State

TEST_CYCLES = 10
CYCLE_DELAY_S = 0.1
N_FLOORS = 5
N_ELEVATORS = 2
AVG_PPL_PER_TICK = 0.3
MAX_LINGERING_CYCLES = 2

def fitness(this_instance, solution, sol_idx) -> float:
    global GANN_instance
    def logic(inputs: list):
        actions = []
        for n in range(N_ELEVATORS):
            pygad.nn.predict(last_layer=GANN_instance.population_networks[sol_idx],
                                   data_inputs=inputs)
    state = State(logic=logic,
                    floors=N_FLOORS,
                    n_elevators=N_ELEVATORS,
                    avg_ppl=AVG_PPL_PER_TICK)
    
    for _ in range(TEST_CYCLES):
        state.update()
    counter = 0
    while len(state.active_ppl()) != 0 and counter < MAX_LINGERING_CYCLES:
        counter += 1
    return 1 / state.summarize().get('average cost')


state = State(floors=N_FLOORS,
                n_elevators=N_ELEVATORS,
                avg_ppl=AVG_PPL_PER_TICK)
num_inputs = len(state.flat_view())
num_classes = N_FLOORS + 2
num_solutions = 10
GANN_instance = pygad.gann.GANN(num_solutions=num_solutions,
                                    num_neurons_input=num_inputs,
                                num_neurons_hidden_layers=[50],
                                num_neurons_output=num_classes,
                                hidden_activations=["relu"],
                                    output_activation="softmax")
population_vectors = pygad.gann.population_as_vectors(population_networks=GANN_instance.population_networks)

initial_population = population_vectors.copy()
def callback_generation(ga_instance):
    population_matrices = pygad.gann.population_as_matrices(population_networks=GANN_instance.population_networks, population_vectors=ga_instance.population)
    GANN_instance.update_population_trained_weights(population_trained_weights=population_matrices)
ga_instance = pygad.GA(num_generations=100, 
                  num_parents_mating=4, 
                    initial_population=initial_population,
                    fitness_func=fitness,
                       mutation_percent_genes=10,
                       parent_selection_type="sss",
                       crossover_type="single_point",
                       mutation_type="random",
                       keep_parents=1,
                       on_generation=callback_generation)
    
ga_instance.run()