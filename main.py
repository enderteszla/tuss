__all__ = ['main']

from TUNM import *
import math


model = TypicalUnifiedNetworkModel(
    node_fitness=lambda chromosome, node, t: 1 if t > chromosome[node.t0] else
    2. - math.pow(2., t / chromosome[node.t0]),
    edge_fitness=lambda chromosome, edge, t: 1,
    threshold=0.94
)
model.read_graphml("reference.graphml")


def main():
    for n in [20, 200, 2000]:
        ga = model.ga(generationsNumber=n)
        ga.run()
        print best(ga.population)
        print best(ga.population).fitness.values

main()