__all__ = ['main']

from TUNM import *
from deap import creator, base, tools
import math
import random

generateLambda = lambda function, **kwargs: lambda *args: function(*args, **kwargs)

chromosomeInit = lambda model, defaults: \
    [defaults[entry['type']][entry['field']] for i, entry in enumerate(model.chromosome_template)]


def preliminary():
    model = TypicalUnifiedNetworkModel(
        node_fitness=lambda chromosome, node, t: 1 if t > chromosome[node.t0] else
        math.exp(chromosome[node.A] * (chromosome[node.t0] - t)),
        edge_fitness=lambda chromosome, edge, t: 1
    )
    model.read_graphml("reference.graphml")

    chromosomeInitGenerator = generateLambda(chromosomeInit, model=model, defaults={
        "Switch": {
            "t0": 10.,
            "A": 0.1
        },
        "Router": {
            "t0": 10.,
            "A": 0.1
        },
        "End": {
            "t0": 10.,
            "A": 0.1
        }
    })

    evaluate = lambda t: (lambda chromosome: model.fitness(chromosome)(t),)

    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)
    toolbox = base.Toolbox()

    toolbox.register("individual", tools.initIterate, creator.Individual, chromosomeInitGenerator)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.1)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register("evaluate", evaluate(0))

    return toolbox


def main():
    toolbox = preliminary()
    population = toolbox.population(n=50)
    CXPB, MUTPB, NGEN = 0.5, 0.2, 40

    # Evaluate the entire population
    fitnesses = map(toolbox.evaluate, population)
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = fit

    for g in range(NGEN):
        # Select the next generation individuals
        offspring = toolbox.select(population, len(population))
        # Clone the selected individuals
        offspring = map(toolbox.clone, offspring)

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # The population is entirely replaced by the offspring
        population[:] = offspring
    return population