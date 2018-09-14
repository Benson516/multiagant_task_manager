"""
Graph engines
These function are graph engins apecifically for useing with
the graph data structure defined by GEOMETRY_TASK_GRAPH
and its following sub-class.
"""
import Queue as Q
# import sys


# Kernel function for finding reachability
def Explore(nid, adj, visited):
    """
    Recursive function for depth-first search.
    """
    visited[nid] = True
    for to_nid, eid in adj[nid]:
        if not visited[to_nid]:
            Explore(to_nid, adj, visited)
    # the end

# Kernel function for finding reachability
def Explore_capacity(nid, adj, edges, visited):
    """
    Recursive function for depth-first search.
    """
    visited[nid] = True
    for to_nid, eid in adj[nid]:
        if not visited[to_nid] and edges[eid].remained_capacity_now > 0:
            Explore_capacity(to_nid, adj, edges, visited)
    # the end

# Kernel function for finding connected components
def Explore_cc(nid, adj, visited, cc, CCnum):
    """
    Recursive function for depth-first search.
    """
    visited[nid] = True
    CCnum[nid] = cc
    for to_nid, eid in adj[nid]:
        if not visited[to_nid]:
            Explore_cc(to_nid, adj, visited, cc, CCnum)
    # the end

# Kernel function for finding connected components
def Explore_cc_capcity(nid, adj, edges, visited, cc, CCnum):
    """
    Recursive function for depth-first search.
    """
    visited[nid] = True
    CCnum[nid] = cc
    for to_nid, eid in adj[nid]:
        if not visited[to_nid] and edges[eid].remained_capacity_now > 0:
            Explore_cc_capcity(to_nid, adj, edges, visited, cc, CCnum)
    # the end







#------------------------------------------------#
def reachability(x, y, adj, edges=None, count_capacity=True):
    """
    Finding the reachiability from node_id:x to node_id:y

    Important: This method only consider the current
               (a specific time instant) topological state.

    """
    visited = [False for _ in range(len(adj))]
    if count_capacity:
        Explore_capacity(x, adj, edges, visited)
    else:
        # Simply traverse through the topology of graph,
        # not counting remained_capacity_now of edges
        Explore(x, adj, visited)
    return visited[y]

def number_of_connected_components(adj, edges=None, count_capacity=True):
    """
    Find the total number of connected components

    Important: This method only consider the current
               (a specific time instant) topological state.

    """
    visited = [False for _ in range(len(adj))]
    CCnum =   [0 for _ in range(len(adj))]
    cc = 1
    if count_capacity:
        for nid in range(len(adj)):
            if not visited[nid]:
                Explore_cc_capcity(nid, adj, edges, visited, cc, CCnum)
                cc += 1
    else:
        # Simply traverse through the topology of graph,
        # not counting remained_capacity_now of edges
        for nid in range(len(adj)):
            if not visited[nid]:
                Explore_cc(nid, adj, visited, cc, CCnum)
                cc += 1
    return (cc-1)




def dijkstras(adj, edges, T_zone_start, start_id, end_id, top_priority_for_activated_agent=False):
    """
    This method ues dijkstra alogorithm to find out the best path
    or find out that there is no path at all.

    Optimization problem:
        Given a graph, the state of graph, the time-zone at start_id,
        find a path with "valid edges" that minimize the
        "max_pass_stamp" at reaching the end_id
        (after passing through the last edge)

    inputs
        - T_zone_start = (T_min, T_max)
        - start_id
        - end_id
        - top_priority_for_activated_agent

    outputs
        - path/None: a sequence (list) of node_id from start_id to end_id
                     or "None" means no valid path
    """
    # Decide that if we only see the activated agent!!
    only_count_activated_agent = top_priority_for_activated_agent

    # We minimize the T_max
    id_opt_target = 1
    max_value = float('inf') # sys.maxsize


    # Get sizes
    num_nodes = len(adj)
    num_edges = len(edges)

    # Initialize the dist and prev
    dist = [max_value for _ in range(num_nodes)] # distance list, "None" stand for infinity
    prev = [None for _ in range(num_nodes)] # Parents list, "None" stands for no parent
    T_zone_nodes = [(max_value, max_value) for _ in range(num_nodes)] # (T_min, T_max) of each node / "Key" for passing edges!

    #-------------------------------#

    # dist[s] = 0 <-- acturally, minimum distance in graph, not actually need to be zero
    dist[start_id] = T_zone_start[id_opt_target] # We count for the maximum time
    T_zone_nodes[start_id] = T_zone_start

    # Make a min-heap
    heap = Q.PriorityQueue()
    for u in range(num_nodes):
        heap.put_nowait( (dist[u], u) )

    # Iteration
    while (not heap.empty()):
        # Get a node_id from heap (currently smallest distance)
        #----------------------------------#
        uh = heap.get_nowait()
        # Filter out some trash in heap
        while uh[0] != dist[uh[1]] and (not heap.empty()):
            # Pop out old one and try new one
            uh = heap.get_nowait()
        if heap.empty():
            # This means that the heap actually has no valuable things
            # in this iteration, just leave
            break
        #----------------------------------#

        # for all (u,v) in E
        # We have to find nodes through "valid" edges
        # that is, it is "possible to pass", it is activated (if we want to check)
        nid_u = uh[1]
        # print("uh[0] = " + str(uh[0]) + ", uh[1] = " + str(uh[1]))
        for nid_v, eid in adj[nid_u]:
            # Check if the edge is "valid"
            # nid_u --eid--> nid_v
            if top_priority_for_activated_agent and (edges[eid].remained_capacity_now <= 0):
                # The edge is "invalid", try another one.
                pass
            else:
                if edges[eid].is_possible_to_pass(T_zone_nodes[nid_u], only_count_activated_agent):
                    T_v_tmp = edges[eid].get_time_stamp_range_after_passage(T_zone_nodes[nid_u])
                    # Relax
                    if dist[nid_v] > T_v_tmp[id_opt_target]:
                        # print("T_v_tmp = " + str(T_v_tmp))
                        dist[nid_v] = T_v_tmp[id_opt_target]
                        T_zone_nodes[nid_v] = T_v_tmp # Update time_zone of the node
                        prev[nid_v] = nid_u
                        """
                        print("update (u, v) = (%d, %d)" % (nid_u, nid_v))
                        print("dist = " + str(dist))
                        print("prev = " + str(prev))
                        print("\n")
                        """
                        heap.put_nowait( (dist[nid_v], nid_v) )
                #
        # end for
    # end while

    # Post proccesing: replace max_value with "None"
    for i in range(len(dist)):
        if dist[i] == max_value:
            dist[i] = None

    # test
    try:
        delta_T_max = dist[end_id] - dist[start_id]
    except:
        delta_T_max = None
    #
    print("\n")
    print("INFO: Dijkstra finished")
    print("INFO: Distance from start_id <%d> to end_id <%d> = %s" % (start_id, end_id, (str(delta_T_max) if not delta_T_max is None else "None" ) ) )
    print("dist = " + str(dist))
    print("prev = " + str(prev))
    #

    # Generate the path
    if dist[end_id] is None:
        # The end_id is not reachable from start_id
        # in the sense of "valid" edge traversal
        print('INFO: The end_id is not reachable from start_id in the sense of "valid" edge traversal.')
        return None
    # If the goal is reachable
    nid_i = end_id;
    path_inv = list()
    path_inv.append(end_id)
    while True:
        nid_prev = prev[nid_i]
        if not nid_prev is None:
            nid_i = nid_prev
            path_inv.append(nid_prev)
        else:
            # No parent, not able to continue
            break
    # Reverse the path, make it from start_id to end_id
    path = path_inv[::-1]
    if path[0] != start_id:
        print("ERROR: path[0] != start_id, something wrong in dijkstra.")
    else:
        # print("INFO: The path generated correctly in dijkstra.")
        pass

    # test
    print("path = " + str(path) )
    print("\n")
    #
    return path
