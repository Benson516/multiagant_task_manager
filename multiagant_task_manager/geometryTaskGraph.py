
import maAgent as ag
import maEdge as ed
import maGraphEngines as ge


# The class for geometry task graph
class GEOMETRY_TASK_GRAPH(object):
    """
    """
    def __init__(self):
        """
        """
        self.num_nodes = 0
        self.num_edges = 0
        # Adjacent graph, store a list of (to_node_id, edge_id) pair of a from_node_id
        # self.adj_graph = [[] for _ in range(self.num_nodes)]
        self.adj_graph = [] # Empty
        # Nodes
        # For searching and inverse searching between node id and the node "name"
        # Note that id and "name" are one to one
        # One node_id have only one "name"
        self.node_id_name_list = [] # Layout: ['name1','name2','name3', ...]
        self.node_name_id_dict = dict() # Layout: {'name1':0, 'name2':1, 'name3':2, ...}
        # Edges, indexed by the edge_id recorded in adj_graph
        self.edge_list = [] # Dynamically changed, elements are ed.EDGE()

    def _is_edge_in_adj_graph(self, from_node_id, to_node_id, check_dual_direction=True):
        """
        This function help check if the specified edge (by vertex) is existed in adj_graph
        """
        if from_node_id >= len(self.adj_graph) or to_node_id >= len(self.adj_graph):
            return False
        else:
            # Normal direction
            for node_id, edge_id in self.adj_graph[from_node_id]:
                if node_id == to_node_id:
                    return True
            if check_dual_direction:
                # Reverse direction
                for node_id, edge_id in self.adj_graph[to_node_id]:
                    if node_id == from_node_id:
                        return True
        #
        return False

    def print_adj_graph(self, is_printing=True, is_showing_by_node_name=True):
        """
        This function print or return a beautiful layout of self.adj_graph by string.
        """
        Str_out = "adj_graph with <%d> nodes and <%d> edges\n" % (self.num_nodes, self.num_edges)
        Str_out += "-------------------------------------------------\n"
        for i in range(self.num_nodes):
            Str_out += ( (self.node_id_name_list[i] + "(%d)" % i) if is_showing_by_node_name else ("#%d" % i) )
            Str_out += ":\t"
            for node_id, edge_id in self.adj_graph[i]:
                Str_out += ( (self.node_id_name_list[node_id]) if is_showing_by_node_name else str(node_id) )
                Str_out += "(%s:%d)\t" % ("biE" if self.edge_list[edge_id].is_bidirectional else "siE",edge_id)
            Str_out += "\n"
        Str_out += "-------------------------------------------------\n"
        # Print out
        if is_printing:
            print(Str_out)
        return Str_out

    def print_edge_list(self, is_printing=True, is_showing_by_node_name=True):
        """
        This function print or return a beautiful layout of self.edge_list by string.
        """
        Str_out = "edge_list with <%d> edges\n" % self.num_edges
        Str_out += "----------------------------------------------------------------------------------\n"
        for i in range(self.num_edges):
            _E = self.edge_list[i]
            Str_out += "#%d:\t" % i
            from_node_id = _E.from_node_id
            to_node_id = _E.to_node_id
            from_node_str = (self.node_id_name_list[from_node_id]) if is_showing_by_node_name else str(from_node_id)
            to_node_str = (self.node_id_name_list[to_node_id]) if is_showing_by_node_name else str(to_node_id)
            Str_out += from_node_str + " --> " + to_node_str + ", "
            Str_out += "biE, " if _E.is_bidirectional else "siE, "
            Str_out += "cap=%d, " % _E.capacity
            Str_out += "pTime=(%d, %d), " % (_E.min_pass_time, _E.max_pass_time)
            Str_out += "#ag=%d, " % _E.num_activated_agent
            Str_out += "reCap=%d, " % _E.remained_capacity_now
            Str_out += "agents={"
            for agent_id in _E.agent_dict:
                Str_out += str(_E.agent_dict[agent_id]) + ", "
            Str_out += "}"
            Str_out += "\n"
        Str_out += "----------------------------------------------------------------------------------\n"
        # Print out
        if is_printing:
            print(Str_out)
        return Str_out

    def add_one_node_by_name(self, node_name):
        """
        The node_id should be unique.
        outputs
            - True/False
        """
        if node_name in self.node_name_id_dict:
            # The node name already exist
            print('The node name <%s>' % node_name)
            return False
        else:
            node_id = len(self.node_id_name_list)
            # Node mapping
            self.node_name_id_dict[node_name] = node_id
            self.node_id_name_list.append(node_name)
            # Update adj_graph
            self.adj_graph.append([])
            # Increase the counter
            self.num_nodes += 1
    #                                 (from_node_id, to_node_id, is_bidirectional, capacity, min_pass_time, max_pass_time)
    def add_one_edge_by_node_id(self, from_node_id, to_node_id, is_bidirectional=True, capacity=1, min_pass_time=0, max_pass_time=None):
        """
        inputs (* denote the "must-have"(mandatory) )
            * from_node_id
            * to_node_id
            - is_bidirectional  (default: True)
            - capacity          (default: 1 unit)
            - min_pass_time     (default: 0 sec.)
            - max_pass_time     (default: None, the same as min_pass_time)
        outputs
            - True/False
        """
        if from_node_id >= self.num_nodes or to_node_id >= self.num_nodes:
            # At least one of the nodes not created!
            print('WARN: At least one of the node id (%d, %d) does not exist, no new edge created.' % (from_node_id, to_node_id))
            return False

        # Nodes exist
        edge_id = len(self.edge_list) # Append to the end of the edge_state
        if self._is_edge_in_adj_graph(from_node_id, to_node_id):
            print('WARN: The edge (%d, %d) already exist, no new edge created.' % (from_node_id, to_node_id))
            return False
        # else, create a new one
        if is_bidirectional:
            self.adj_graph[from_node_id].append((to_node_id, edge_id))
            self.adj_graph[to_node_id].append((from_node_id, edge_id))
        else:
            self.adj_graph[from_node_id].append((to_node_id, edge_id))
        # Edges
        self.edge_list.append( ed.EDGE(edge_id, from_node_id, to_node_id, is_bidirectional, capacity, min_pass_time, max_pass_time) )
        # Increase the counter
        self.num_edges += 1
        return True

    #                                 (from_node_name, to_node_name, is_bidirectional, capacity, min_pass_time, max_pass_time)
    def add_one_edge_by_node_name(self, from_node_name, to_node_name, is_bidirectional=True, capacity=1, min_pass_time=0, max_pass_time=None):
        """
        inputs (* denote the "must-have"(mandatory) )
            * from_node_name
            * to_node_name
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
