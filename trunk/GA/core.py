__all__ = ['GA']

# import accessories
from aux import *
from defaults import *
# import other external modules
from random import random
from deap import creator, base, tools


class GA(object):
    def __init__(self, init_chromosome, evaluate_chromosome, **kwargs):
        def get(key):
            return kwargs.get(key, defaults[key])

        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)

        self.toolbox = base.Toolbox()
        self.toolbox.register("individual", tools.initIterate, creator.Individual, init_chromosome)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("mate", tools.cxTwoPoint)
        self.toolbox.register("mutate", tools.mutGaussian, mu=get('mu'), sigma=get('sigma'), indpb=get('indpb'))
        if kwargs.get('check_bounds') is not None:
            self.toolbox.decorate("mate", kwargs.get('check_bounds'))
            self.toolbox.decorate("mutate", kwargs.get('check_bounds'))
        self.toolbox.register("select", tools.selTournament, tournsize=get('tournsize'))
        self.toolbox.register("evaluate", evaluate_chromosome)

        self.mateProbability = get('mateProbability')
        self.mutateProbability = get('mutateProbability')
        self.generationsNumber = get('generationsNumber')
        self.epsilon = get('epsilon')

        self.population = self.toolbox.population(n=get('populationSize'))
        self.evaluate()

    def evaluate(self, population=None):
        if population is None:
            population = self.population
        fit = map(self.toolbox.evaluate, population)
        for i, f in zip(population, fit):
            i.fitness.values = f

    def run(self):
        # Select the next generation individuals
        offspring = self.toolbox.select(self.population, len(self.population))
        # Clone the selected individuals
        offspring = map(self.toolbox.clone, offspring)

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random() < self.mateProbability:
                self.toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random() < self.mutateProbability:
                self.toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        self.evaluate([ind for ind in offspring if not ind.fitness.valid])

        # The population is entirely replaced by the offspring
        self.population[:] = offspring
        self.generationsNumber -= 1

        if self.generationsNumber > 0 and best(self.population).fitness.values[0] > self.epsilon:
            self.run()