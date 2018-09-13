import geometryTaskGraph as gtg

graph = gtg.GEOMETRY_TASK_GRAPH()

graph.add_one_node_by_name('A')
graph.add_one_node_by_name('B')
graph.add_one_node_by_name('C')
graph.add_one_node_by_name('D')
graph.add_one_node_by_name('E')

# (from_node_name, to_node_name, is_bidirectional, capacity, min_pass_time, max_pass_time)
graph.add_one_edge_by_node_name('A','B',True, 2, 1, 5)
graph.add_one_edge_by_node_name('B','C',True, 3, 1, 2)
graph.add_one_edge_by_node_name('C','D',False, 2, 1, 2)
graph.add_one_edge_by_node_name('D','E',True, 1, 1, 2)
graph.add_one_edge_by_node_name('E','A',True, 1, 1, 2)
graph.add_one_edge_by_node_name('A','D',True, 3, 1, 2)

# test of put_agent()
graph.edge_list[1].put_agent(2, 100, True, 100, 201)
graph.edge_list[1].put_agent(3, 101, True, 100, 201)
graph.edge_list[1].put_agent(1, 102, True, 100, 201)
graph.edge_list[1].put_agent(0, 103, True, 100, 201)

print("(#node, #edge) = (%d, %d)" % (graph.num_nodes, graph.num_edges))

graph.print_adj_graph(is_showing_by_node_name=True)
graph.print_edge_list(is_showing_by_node_name=True)
