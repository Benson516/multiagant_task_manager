
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

    def _get_edge_list_from_path(self, path):
        """
        This utility method help finding the edge list from a given path.
        inputs
            - path: a sequence of node_id

        outputs
            - path_edges/None: a sequence of edges that the path pass through,
                               "None" means that the path has some non-exist edges.
        """
        path_edges = []
        for i in range(len(path)-1):
            from_node_id = path[i]
            to_node_id = path[i+1]
            if not self._is_edge_in_adj_graph(from_node_id, to_node_id, check_dual_direction=True):
                print("ERROR: The edge (%d --> %d) is not in the given path" % (from_node_id, to_node_id) )
                return None
            edge_id = None
            for nid, eid in self.adj_graph[from_node_id]:
                if nid == to_node_id:
                    edge_id = eid
                    break
            if edge_id is None:
                # Something wrong
                print("ERROR: The edge (%d --> %d) is not in the given path" % (from_node_id, to_node_id) )
                return None
            # Found edge_id
            path_edges.append(edge_id)
        return path_edges


    def print_adj_graph(self, is_printing=True, is_showing_by_node_name=True):
        """
        This function print or return a beautiful layout of self.adj_graph by string.
        """
        Str_out = "\nadj_graph with <%d> nodes and <%d> edges\n" % (self.num_nodes, self.num_edges)
        Str_out += "-------------------------------------------------\n"
        for i in range(self.num_nodes):
            Str_out += ( (self.node_id_name_list[i] + "(%d)" % i) if is_showing_by_node_name else ("#%d" % i) )
            Str_out += ":\t"
            for node_id, edge_id in self.adj_graph[i]:
                Str_out += ( (self.node_id_name_list[node_id]) if is_showing_by_node_name else str(node_id) )
                Str_out += "(%s:%d)\t" % ("<-->" if self.edge_list[edge_id].is_bidirectional else " -->",edge_id)
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
        Str_out = "\nedge_list with <%d> edges\n" % self.num_edges
        Str_out += "---------------------------------------------------------------------------------------\n"
        for i in range(self.num_edges):
            _E = self.edge_list[i]
            Str_out += "#%d:\t" % i
            from_node_id = _E.from_node_id
            to_node_id = _E.to_node_id
            from_node_str = (self.node_id_name_list[from_node_id]) if is_showing_by_node_name else str(from_node_id)
            to_node_str = (self.node_id_name_list[to_node_id]) if is_showing_by_node_name else str(to_node_id)
            Str_out += from_node_str + (" <--> " if _E.is_bidirectional else "  --> ")
            Str_out += to_node_str + ",\t"
            Str_out += "cap=%d, " % _E.capacity
            Str_out += "pTime=(%d, %d), " % (_E.min_pass_time, _E.max_pass_time)
            Str_out += "#ag=%d, " % _E.num_activated_agent
            Str_out += "reCap=%d, " % _E.remained_capacity_now
            Str_out += "agents={"
            for agent_id in _E.agent_dict:
                Str_out += str(_E.agent_dict[agent_id]) + ", "
            Str_out += "}"
            Str_out += "\n"
        Str_out += "---------------------------------------------------------------------------------------\n"
        # Print out
        if is_printing:
            print(Str_out)
        return Str_out

    def print_path(self, path, is_printing=True, is_showing_by_node_name=True):
        """
        This function print or return a the path by string.
        """
        if not is_showing_by_node_name:
            Str_out = "path = %s" % str(path)
        else:
            Str_out = "path = ["
            for i in range(len(path)):
                Str_out += self.node_id_name_list[path[i]]
                Str_out += (", " if i < (len(path)-1) else "")
            Str_out += "]"
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
            print('ERROR: The node name <%s> is already exist, the node is not added.' % node_name)
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

    # Agent operations
    #---------------------------------------#
    def _remove_agent_from_all_edges(self, agent_id, task_id=None):
        """
        Remove an agent from all edges with specified/non-specified task_id.
        """
        for edge in self.edge_list:
            if edge.is_agent_in_edge(agent_id):
                if (task_id is None) or (self.edge_list[edge_id].agent_dict[agent_id].task_id == task_id):
                    # print('INFO: Remove the agent <%d> with task <%d> from edge <%d>.' % (agent_id, edge.agent_dict[agent_id].task_id, edge.edge_id))
                    edge.remove_agent(agent_id)
        #
        return True

    def _remove_agent_by_path(self, path, agent_id, task_id=None):
        """
        Remove an agent according to a list of node "path"
        with specified/non-specified task_id.
        """
        path_edge = self._get_edge_list_from_path(path)
        if path_edge is None:
            return False
        # Else
        for edge_id in path_edge:
            # Remove agent
            if self.edge_list[edge_id].is_agent_in_edge(agent_id):
                if (task_id is None) or (self.edge_list[edge_id].agent_dict[agent_id].task_id == task_id):
                    # print('INFO: Remove agent <%d> with task <%s> from edge <%d>.' % (agent_id, str(self.edge_list[edge_id].agent_dict[agent_id].task_id), self.edge_list[edge_id].edge_id))
                    self.edge_list[edge_id].remove_agent(agent_id)
        #
        return True

    def _add_agent_by_path(self, path, T_zone_start, agent_id, task_id=None, is_activated=True):
        """
        Add an agent according to a list of node "path"
        with specified/non-specified task_id.
        inputs
            - T_zone_start = (T_min, T_max)
        outputs
            - True/False
        """
        path_edge = self._get_edge_list_from_path(path)
        if path_edge is None:
            return False
        # Else
        T_zone_tmp = T_zone_start
        T_zone_occ = T_zone_start
        for edge_id in path_edge:
            # Add agent
            T_zone_occ = self.edge_list[edge_id].get_time_stamp_range_occupying_edge(T_zone_tmp)
            T_zone_tmp = self.edge_list[edge_id].get_time_stamp_range_after_passage(T_zone_tmp)
            self.edge_list[edge_id].put_agent(agent_id, task_id, is_activated, T_zone_occ[0], T_zone_occ[1])
            # print('INFO: Add agent <%d> with task <%s> from edge <%d>.' % (agent_id, str(self.edge_list[edge_id].agent_dict[agent_id].task_id), self.edge_list[edge_id].edge_id))
            # Note that we have to print this after adding agent
        return True
    #---------------------------------------#

    # Traversal methods
    #---------------------------------------#
    def qrarry_path_exist(self, T_zone_start, start_id, end_id, top_priority_for_activated_agent=False):
        """
        This method ues dijkstra alogorithm to find out the best path
        or find out that there is no path at all.

        inputs
            - T_zone_start = (T_min, T_max)
            - start_id
            - end_id
            - top_priority_for_activated_agent

        outputs
            - True/False
        """
        return ( not (ge.dijkstras(self.adj_graph, self.edge_list, T_zone_start, start_id, end_id, top_priority_for_activated_agent) is None) )

    def book_a_path(self, T_zone_start, start_id, end_id, agent_id, task_id=None):
        """
        This method ues dijkstra alogorithm to find out the best path
        or find out that there is no path at all.

        inputs
            - T_zone_start = (T_min, T_max)
            - start_id
            - end_id
            - top_priority_for_activated_agent

        outputs
            - path/None: a sequence (list) of node_id from start_id to end_id
                         or "None" means no valid path
        """
        # Note that top_priority_for_activated_agent is set to False
        path = ge.dijkstras(self.adj_graph, self.edge_list, T_zone_start, start_id, end_id, False)
        if path is None:
            # Non-reachable
            return None
        # Else
        # Note that the activation of the agent is set to False
        self._add_agent_by_path(path, T_zone_start, agent_id, task_id, False)
        return path
    #---------------------------------------#
