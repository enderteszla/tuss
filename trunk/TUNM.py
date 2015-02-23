__all__ = ['TypicalUnifiedNetworkModel']
import networkx as nx
import random
from TUNMclasses import *
from deap import creator, base, tools

""" Definitions & Declarations of the Model:
(In English only - since non-ASCII characters not provided.)

Node types:
* R - a Router;
* S - a Switch;
* N - an end node;
* F - a firewall.

(Node type-specific) node features (required by a particular fitness function formula):
1) (R)outer:
    * openness (boolean)
    ... (some unpredictable stuff that remains to be implied later)
2) (S)witch:
    ... (some unpredictable stuff that remains to be implied later)
3) (E)nd Node:
    * VLAN number (integer)
    * is a Server (boolean)
    ... (some other unpredictable stuff that remains to be implied later)

Link types:
* a link.

Link features:
1) number of directions (1 or 2 according to the form implied);
2) a start node;
3) an end node;

The Firewall should introduce the commutation map (yet it may not be implemented though.)
"""


# The Model itself
class TypicalUnifiedNetworkModel(object):
    def __init__(self, **kwargs):
        self.general_graph = kwargs.get('graph', nx.DiGraph())
        self.link_graph = None
        self.network_graph = None
        self.chromosome_template = []
        self.node_fitness = kwargs.get('node_fitness')
        self.edge_fitness = kwargs.get('edge_fitness')

    def add_node(self, node=None, connect_to=None, node_type=None, **kwargs):
        if node is None:
            node = construct_element(node_type, chromosome_template=self.chromosome_template, **kwargs)
        node.general_index = str(self.general_graph.number_of_nodes())
        self.general_graph.add_node(node.general_index, {'node': node})
        if connect_to is not None:
            self.add_edge(node.general_index, connect_to)
        return node.general_index

    def add_edge(self, source=None, target=None, **kwargs):
        edge = construct_element("Edge", chromosome_template=self.chromosome_template,
                                 source=source, target=target, **kwargs)
        self.general_graph.add_edge(source, target, {'edge': edge})

    def read_graphml(self, path):
        self.general_graph = nx.read_graphml(path)
        for index, data in self.general_graph.nodes_iter(data=True):
            node = construct_element(data['type'], chromosome_template=self.chromosome_template, **data)
            data.clear()
            data['node'] = node
        for i, j, data in self.general_graph.edges_iter(data=True):
            edge = construct_element("Edge", chromosome_template=self.chromosome_template, **data)
            data.clear()
            data['edge'] = edge

    def write_graphml(self, path):
        for i, data in self.general_graph.nodes_iter(data=True):
            for k, v in vars(data['node']).items():
                if k != 'chromosome_template' and v is not None:
                    data[k] = v
            del data['node']
        for i, j, data in self.general_graph.edges_iter(data=True):
            for k, v in vars(data['edge']).items():
                if k != 'chromosome_template' and v is not None:
                    data[k] = v
            del data['edge']
        nx.write_graphml(self.general_graph, path)
        return self

    def fitness(self, chromosome, node_index='0'):
        return add_fitness(
            new_fitness(self.node_fitness, chromosome, self.general_graph.node[node_index]['node']), [
                mul_fitness(
                    new_fitness(self.edge_fitness, chromosome, self.general_graph.edge[i][node_index]['edge']),
                    self.fitness(chromosome, i))
                for i in self.general_graph.predecessors_iter(node_index)
            ]
        )

    def ga(self, defaults):
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMin)
        toolbox = base.Toolbox()
        toolbox.register(
            "population_guess",
            lambda pcls, ind_init, chromosome_template: pcls(ind_init(c) for c in [
                defaults[entry['type']][entry['field']] for i, entry in enumerate(chromosome_template)

            ]),
            list,
            creator.Individual,
            self.chromosome_template
        )
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.1)
        toolbox.register("select", tools.selTournament, tournsize=3)
        toolbox.register("evaluate", lambda chromosome: self.fitness(chromosome)(10))

        population = toolbox.population_guess()
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