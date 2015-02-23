__all__ = ['construct_element', 'new_fitness', 'mul_fitness', 'add_fitness']

construct_element = lambda element_type, **kwargs: {
    'Router': Router,
    'Switch': Switch,
    'End': End,
    'Edge': Edge
}.get(element_type)(**kwargs)


# Element types
class Element(object):
    def __init__(self, element_type, **kwargs):
        self.type = element_type
        self.get('chromosome_template', **kwargs)

    def register(self, field):
        setattr(self, field, len(self.chromosome_template))
        self.chromosome_template.append({'type': type(self).__name__, 'field': field})
        return self

    def get(self, field, default=None, **kwargs):
        setattr(self, field, kwargs.get(field, default))
        return self


class Node(Element):
    def __init__(self, node_type, **kwargs):
        super(Node, self).__init__(node_type, **kwargs)
        self.get('general_index', **kwargs).get('link_index', **kwargs).get('network_index', **kwargs)
        self.register('t0').register('A')


class Router(Node):
    def __init__(self, **kwargs):
        super(Router, self).__init__("Router", **kwargs)
        self.get('openness', default=False, **kwargs)


class Switch(Node):
    def __init__(self, **kwargs):
        super(Switch, self).__init__("Switch", **kwargs)


class End(Node):
    def __init__(self, **kwargs):
        super(End, self).__init__("End", **kwargs)
        self.get('vlan_number', default=0, **kwargs).get('is_a_server', default=False, **kwargs)


class Edge(Element):
    def __init__(self, **kwargs):
        super(Edge, self).__init__("Edge", **kwargs)
        self.get('source', **kwargs).get('target', **kwargs)


# Fitness function computation
new_fitness = lambda function, chromosome, element: lambda t: function(chromosome, element, t)
mul_fitness = lambda fitness, other: lambda t: fitness(t) * other(t)
add_fitness = lambda fitness, others: fitness if len(others) == 0 else lambda t: fitness(t) + \
    reduce(lambda a, b: a + b, [other(t) for i, other in enumerate(others)], 0) / len(others)