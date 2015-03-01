# import accessories
from aux import *
from defaults import *

import networkx as nx
from GA import *


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


def generate_lambda(function, **kwargs):
    return lambda *args: function(*args, **kwargs)


def cutoff(offspring, bounds_array):
    for child in offspring:
        for i in xrange(len(child)):
            if child[i] > bounds_array[i]['right']:
                child[i] = bounds_array[i]['right']
            elif child[i] < bounds_array[i]['left']:
                child[i] = bounds_array[i]['left']
    return offspring

# Fitness function computation
new_fitness = lambda function, chromosome, element: lambda t: function(chromosome, element, t)
mul_fitness = lambda fitness, other: lambda t: fitness(t) * other(t)
sum_fitness = lambda functions: (lambda t: 1) if len(functions) == 0 else lambda t: \
    reduce(lambda a, b: a + b, [function(t) for i, function in enumerate(functions)], 0) / len(functions)


# The Model itself
class TypicalUnifiedNetworkModel(object):
    def __init__(self, **kwargs):
        self.general_graph = kwargs.get('graph', nx.DiGraph())
        self.link_graph = None
        self.network_graph = None
        self.chromosome_template = []

        self.node_fitness = kwargs.get('node_fitness')
        self.edge_fitness = kwargs.get('edge_fitness')
        self.threshold = kwargs.get('threshold')

        self.initials = initials
        self.bounds = bounds
        self.time = time

        self.init_chromosome = lambda: \
            [self.initials[entry['type']][entry['field']] for i, entry in enumerate(self.chromosome_template)]
        self.check_bounds = lambda func: \
            lambda *args, **kw_args: \
            cutoff(
                func(*args, **kw_args),
                [self.bounds[entry['type']][entry['field']] for i, entry in enumerate(self.chromosome_template)]
            )
        self.evaluate = lambda t: (lambda chromosome: (abs(self.threshold - self.fitness(chromosome)(t)),))

        self.ga = lambda **kw_args: GA(
            init_chromosome=self.init_chromosome,
            check_bounds=self.check_bounds,
            evaluate_chromosome=self.evaluate(self.time),
            **kw_args
        )

    def set_threshold(self, value):
        self.threshold = value
        return self

    def set_initials(self, value):
        self.initials = value
        return self

    def set_bounds(self, value):
        self.bounds = value
        return self

    def set_time(self, value):
        self.time = value

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
        return self

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
        return mul_fitness(
            new_fitness(self.node_fitness, chromosome, self.general_graph.node[node_index]['node']),
            sum_fitness([
                mul_fitness(
                    new_fitness(self.edge_fitness, chromosome, self.general_graph.edge[i][node_index]['edge']),
                    self.fitness(chromosome, i))
                for i in self.general_graph.predecessors_iter(node_index)
            ])
        )