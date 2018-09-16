import geometryTaskGraph as gtg
import maGraphEngines as ge

graph = gtg.GEOMETRY_TASK_GRAPH()

graph.add_one_node_by_name('A')
graph.add_one_node_by_name('B')
graph.add_one_node_by_name('C')
graph.add_one_node_by_name('D')
graph.add_one_node_by_name('E')
graph.add_one_node_by_name('F')
graph.add_one_node_by_name('G')

# (from_node_name, to_node_name, is_bidirectional, capacity, min_pass_time, max_pass_time)
graph.add_one_edge_by_node_name('A','B',True, 2, (1, 5))
graph.add_one_edge_by_node_name('B','C',False, 2, (1, 2))
graph.add_one_edge_by_node_name('C','D',False, 3, (1, 3))
graph.add_one_edge_by_node_name('D','E',True, 1, (1, 2))
# graph.add_one_edge_by_node_name('E','A',True, 1, (1, 2))
graph.add_one_edge_by_node_name('A','D',True, 2, (1, 2))

graph.add_one_edge_by_node_name('E','G',True, 1, (1, 2))
graph.add_one_edge_by_node_name('A','F',True, 1, (1, 2))

# test of put_agent()
graph.edge_list[1].put_agent(2, 100, True, (100, 201))
graph.edge_list[2].put_agent(3, 101, True, (100, 201))
graph.edge_list[3].put_agent(1, 102, True, (100, 201))
graph.edge_list[2].put_agent(1, 103, False, (100, 201))
graph.edge_list[1].put_agent(1, 104, True, (100, 201))
graph.edge_list[0].put_agent(0, 103, True, (100, 201))

# Test of time zone calculations
print("\n")
time_zone = (0, 5)
print("time_zone = " + str(time_zone) )
time_zone = graph.edge_list[0].get_time_stamp_range_after_passage(time_zone)
print("time_zone = " + str(time_zone) )
time_zone = graph.edge_list[1].get_time_stamp_range_after_passage(time_zone)
print("time_zone = " + str(time_zone) )
print("\n")

print("(#node, #edge) = (%d, %d)" % (graph.num_nodes, graph.num_edges))

graph.print_adj_graph(is_showing_by_node_name=True)
graph.print_edge_list(is_showing_by_node_name=True)

# test the kernel functions
res = ge.reachability(0, 3, graph.adj_graph, graph.edge_list, True)
print("reachability = " + str(res))
res = ge.number_of_connected_components(graph.adj_graph, graph.edge_list, True)
print("# of connected component = %d" % res)

# Dijkstra
path = ge.dijkstras(graph.adj_graph, graph.edge_list, (0,0), 5, 6, False)
print("Dijkstra's path = " + str(path))

# test removing agents
# path.append(7)
# print("new path = " + str(path))
graph._remove_agent_by_path(path, 1)
graph.print_edge_list(is_showing_by_node_name=True)
graph._add_agent_by_path(path, (0,0), 1, 10, False)
graph.print_edge_list(is_showing_by_node_name=True)
graph._remove_agent_by_path(path[:3], (0,0), 1)
graph.print_edge_list(is_showing_by_node_name=True)
#
graph._remove_agent_from_all_edges(1)
graph.print_edge_list(is_showing_by_node_name=True)

graph.book_a_path((50,100), 0, 6, 7)
graph.print_edge_list(is_showing_by_node_name=True)


graph.print_path(path, is_showing_by_node_name=False)
graph.print_path(path)
