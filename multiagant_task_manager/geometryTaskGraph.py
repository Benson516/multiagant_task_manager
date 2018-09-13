
import maAgent as ag
import maEdge as ed


# The class for geometry task graph
class GEOMETRY_TASK_GRAPH(object):
    """
    """
    def __init__(self, num_nodes, num_edges):
        """
        """
        self.num_nodes = num_nodes
        self.num_edges = num_edges
        # Adjacent graph, store a list of (to_node_id, edge_id) pair of a from_node_id
        self.adj_graph = [[] for _ in range(self.num_nodes)]
        # Nodes
        # For searching and inverse searching between node id and the node "names"
        # Note that id and "name" are not one to one
        # One id may have several "name"
        self.node_id_name_list = [] # Layout: [['name1','name2'], ['name3'], ...]
        self.node_name_id_dict = dict() # Layout: {'name1':0, 'name2':0, 'name3':1, ...}
        # Edges, indexed by the edge_id recorded in adj_graph
        self.edge_list = [] # Dynamically changed, elements are ed.EDGE()

    def _is_edge_in_adj_graph(self, from_node_id, to_node_id):
        """
        This function help check if the specified edge (by vertex) is existed in adj_graph
        """
        if len(self.adj_graph) <= from_node_id:
            return False
        else:
            for node in self.adj_graph[from_node_id]:
                if to_node_id == node:
                    return True
            return False

    def add_one_node(self, node_name, node_id=None):
        """

        """
        pass

    def add_one_edge_by_node_id(self, param_dict):
        """
        inputs
            param_dict includes: (* denote the "must-have"(mandatory) )
            * edge_id
            * from_node_id
            * to_node_id
            - is_bidirectional  (default: True)
            - capacity          (default: 1 unit)
            - min_pass_time     (default: 0 sec.)
            - max_pass_time     (default: None, the same as min_pass_time)
        outputs
            - True/False
        """
        edge_id = len(self.edge_list) # Append to the end of the edge_state
        if self._is_edge_in_adj_graph(from_node_id, to_node_id)
            print('WARN: The edge (%d, %d) already exist, no new edge created.' % (from_node_id, to_node_id))
            return False
        # else, create a new one
        if is_bidirectional:
            adj[from_node_id].append((to_node_id, edge_id))
            adj[to_node_id].append((from_node_id, edge_id))
        else:
            adj[from_node_id].append((to_node_id, edge_id))
        # Edges
        self.edge_list.append( ed.EDGE(param_dict) )
        return True

    def add_one_edge_by_node_name(self, param_dict):
        """
        inputs
            param_dict includes: (* denote the "must-have"(mandatory) )
            * edge_id
            * from_node_id
            * to_node_id
            - is_bidirectional  (default: True)
            - capacity          (default: 1 unit)
            - min_pass_time     (default: 0 sec.)
            - max_pass_time     (default: None, the same as min_pass_time)
        outputs
            - True/False
        """
        try:
            from_node_id = self.node_name_id_dict[from_node_name]
            to_node_id = self.node_name_id_dict[to_node_name]
        except:
            print('WARN: At least one of the node name (%s, %s) does not exist, no new edge created.' % (from_node_name, to_node_name))
            return False
        #
        return self.add_one_edge_by_node_id(from_node_id, to_node_id, is_bidirectional, capacity, min_pass_time, max_pass_time)
