"""
Graph engines
These function are graph engins apecifically for useing with
the graph data structure defined by GEOMETRY_TASK_GRAPH
and its following sub-class.
"""

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
