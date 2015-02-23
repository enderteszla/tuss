from TUNM import *
import math
model = TypicalUnifiedNetworkModel(
    node_fitness=lambda chromosome, node, t: 1 if t > chromosome[node.t0] else
    math.exp(chromosome[node.A] * (chromosome[node.t0] - t)),
    edge_fitness=lambda chromosome, edge, t: 1
)

model.add_node(node_type="Router")
model.add_node(node_type="Router", connect_to='0')
model.add_node(node_type="Router", connect_to='0', openness=True)
model.add_node(node_type="Switch", connect_to='1')
model.add_node(node_type="Switch", connect_to='1')
model.add_node(node_type="Switch", connect_to='2')
model.add_node(node_type="Switch", connect_to='2')
model.add_node(node_type="Switch", connect_to='0')

model.add_node(node_type="End", connect_to='3', vlan_number='1')
model.add_node(node_type="End", connect_to='3', vlan_number='2')
model.add_node(node_type="End", connect_to='3', vlan_number='3')
model.add_node(node_type="End", connect_to='3', vlan_number='4')

model.add_node(node_type="End", connect_to='4', vlan_number='1')
model.add_node(node_type="End", connect_to='4', vlan_number='2')
model.add_node(node_type="End", connect_to='4', vlan_number='3')
model.add_node(node_type="End", connect_to='4', vlan_number='4')

model.add_node(node_type="End", connect_to='5', vlan_number='1')
model.add_node(node_type="End", connect_to='5', vlan_number='2')
model.add_node(node_type="End", connect_to='5', vlan_number='3')
model.add_node(node_type="End", connect_to='5', vlan_number='4')

model.add_node(node_type="End", connect_to='6', vlan_number='1')
model.add_node(node_type="End", connect_to='6', vlan_number='2')
model.add_node(node_type="End", connect_to='6', vlan_number='3')
model.add_node(node_type="End", connect_to='6', vlan_number='4')

model.add_node(node_type="End", connect_to='7', vlan_number='1', is_a_server=True)
model.add_node(node_type="End", connect_to='7', vlan_number='2', is_a_server=True)
model.add_node(node_type="End", connect_to='7', vlan_number='3', is_a_server=True)

model.write_graphml("reference.graphml")