__all__ = ['best']

best = lambda population: [
    ind for ind in population
    if ind.fitness.values == min([i.fitness.values for i in population])
][0]