
import maTask as tk
import maEdge as ed
import maNode as nd
import maGraphEngines as ge


# The class for geometry task graph
class GEOMETRY_TASK_GRAPH(object):
    """
    This is the container fo the geometry graph which contains nodes, edges, agents, and task.
    Properties (static)
        - num_nodes
        - num_edges
        - node_list: The list of node containers
        - node_name_id_dict: the dictionary that maps from name to node_id
        - edge_list: The list of edge containers
        - adj_graph: The relationship from node to node, connected by edges

    States (dynamically changed)
        - task_dict: dictionary of task that map from task_id to tk.TASK() object
        - idle_task_list: a list of task with task_id are all (-1) <-- idle,
                          while priorities are the higest (2) <-- occupying,
                          and the T_zone are infinite for the last one
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
        self.node_list = [] # Dynamically changed, elements are nd.NODE()
        self.node_name_id_dict = dict() # Layout: {'name1':0, 'name2':1, 'name3':2, ...}
        # Edges, indexed by the edge_id recorded in adj_graph
        self.edge_list = [] # Dynamically changed, elements are ed.EDGE()


    # Insertion
    #-----------------------------------------#
    def add_one_node_by_name(self, node_name, is_stayable=False, capacity=1):
        """
        The node_id should be unique.

        inputs (* denote the "must-have"(mandatory) )
        * name
        - is_stayable       (default: False)
        - capacity          (default: 1 unit)

        outputs
            - True/False
        """
        if node_name in self.node_name_id_dict:
            # The node name already exist
            print('ERROR: The node_name <%s> is already exist, the node is not added.' % node_name)
            return False
        else:
            node_id = len(self.node_list)
            # Node mapping
            self.node_list.append( nd.NODE(node_id, node_name, is_stayable, capacity) )
            self.node_name_id_dict[node_name] = node_id
            # Expend the size of adj_graph (for additional node)
            self.adj_graph.append([])
            # Increase the counter
            self.num_nodes += 1
            return True

    #                                 (from_node_id, to_node_id, is_bidirectional, capacity, duration)
    def add_one_edge_by_node_id(self, from_node_id, to_node_id, is_bidirectional=True, capacity=1, duration=(0, 0)):
        """
        inputs (* denote the "must-have"(mandatory) )
            * from_node_id
            * to_node_id
            - is_bidirectional      (default: True)
            - capacity              (default: 1 unit)
            - duration = (min_pass_time, max_pass_time)
                - min_pass_time     (default: 0 sec.)
                - max_pass_time     (default: None, stands for infinity)
        outputs
            - True/False
        """
        if from_node_id >= self.num_nodes or to_node_id >= self.num_nodes:
            # At least one of the nodes not created!
            print('WARN: At least one of the node id (%d, %d) does not exist, no new edge created.' % (from_node_id, to_node_id))
            return False

        # Else, nodes exist
        edge_id = len(self.edge_list) # Append to the end of the edge_list
        if self._is_edge_in_adj_graph(from_node_id, to_node_id, check_dual_direction=True):
            print('WARN: The edge (%d, %d) already exist, no new edge created.' % (from_node_id, to_node_id))
            return False
        # else, no existence edge, create a new one
        if is_bidirectional:
            self.adj_graph[from_node_id].append((to_node_id, edge_id))
            self.adj_graph[to_node_id].append((from_node_id, edge_id))
        else:
            self.adj_graph[from_node_id].append((to_node_id, edge_id))
        # Edge
        self.edge_list.append( ed.EDGE(edge_id, from_node_id, to_node_id, is_bidirectional, capacity, duration) )
        # Increase the counter
        self.num_edges += 1
        return True

    #                                 (from_node_name, to_node_name, is_bidirectional, capacity, duration)
    def add_one_edge_by_node_name(self, from_node_name, to_node_name, is_bidirectional=True, capacity=1, duration=(0, 0)):
        """
        inputs (* denote the "must-have"(mandatory) )
            * from_node_name
            * to_node_name
            - is_bidirectional      (default: True)
            - capacity              (default: 1 unit)
            - duration = (min_pass_time, max_pass_time)
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
        return self.add_one_edge_by_node_id(from_node_id, to_node_id, is_bidirectional, capacity, duration)
    #-----------------------------------------#


    def _is_edge_in_adj_graph(self, from_node_id, to_node_id, check_dual_direction=True):
        """
        This function help check if the specified edge (by vertex) is existed in adj_graph
        """
        if from_node_id >= len(self.adj_graph) or to_node_id >= len(self.adj_graph):
            return False
        # else
        # Normal direction
        for node_id, edge_id in self.adj_graph[from_node_id]:
            if node_id == to_node_id:
                return True
        if check_dual_direction:
            # Reverse direction
            for node_id, edge_id in self.adj_graph[to_node_id]:
                if node_id == from_node_id:
                    return True
        # not Found
        return False

    def _get_edge_list_from_path(self, path):
        """
        This utility method help finding the edge list from a given path.
        inputs
            - path: a sequence of node_id

        outputs
            - path_edges/None: a sequence of edge_id that the path pass through,
                               "None" means that the path does not exist in the graph.
        """
        if path is None:
            return None
        # Else, non-empty path
        path_edges = []
        for i in range(len(path)-1):
            from_node_id = path[i]
            to_node_id = path[i+1]
            if not self._is_edge_in_adj_graph(from_node_id, to_node_id, check_dual_direction=True):
                print("ERROR: The edge (%d --> %d) does not exist in the graph." % (from_node_id, to_node_id) )
                return None
            edge_id = None
            for nid, eid in self.adj_graph[from_node_id]:
                if nid == to_node_id:
                    edge_id = eid
                    break
            if edge_id is None:
                # Something wrong
                print("ERROR: The edge (%d --> %d) on the specified direction does not exist in the graph." % (from_node_id, to_node_id) )
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
            Str_out += ( (self.node_list[i].name + "(%d)" % i) if is_showing_by_node_name else ("#%d" % i) )
            Str_out += ":\t"
            for node_id, edge_id in self.adj_graph[i]:
                Str_out += ( (self.node_list[node_id].name) if is_showing_by_node_name else str(node_id) )
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
            from_node_str = (self.node_list[from_node_id].name) if is_showing_by_node_name else str(from_node_id)
            to_node_str = (self.node_list[to_node_id].name) if is_showing_by_node_name else str(to_node_id)
            Str_out += from_node_str + (" <--> " if _E.is_bidirectional else "  --> ")
            Str_out += to_node_str + ",\t"
            Str_out += "cap=%d, " % _E.capacity
            Str_out += "dT=" + str(_E.duration) + ", "
            Str_out += "#task=%d, " % len(_E.task_dict)
            Str_out += "tasks={"
            for task_id in _E.task_dict:
                Str_out += str(_E.task_dict[task_id]) + ", "
            Str_out += "}"
            Str_out += "\n"
        Str_out += "---------------------------------------------------------------------------------------\n"
        # Print out
        if is_printing:
            print(Str_out)
        return Str_out

    def print_node_list(self, is_printing=True, is_showing_by_node_name=True):
        """
        This function print or return a beautiful layout of self.node_list by string.
        """
        # TODO: Implement this function.
        pass

    def print_path(self, path, is_printing=True, is_showing_by_node_name=True):
        """
        This function print or return a the path by string.
        """
        if not is_showing_by_node_name:
            Str_out = "path = %s" % str(path)
        else:
            Str_out = "path = ["
            for i in range(len(path)):
                Str_out += self.node_list[path[i]].name
                Str_out += (", " if i < (len(path)-1) else "")
            Str_out += "]"
        # Print out
        if is_printing:
            print(Str_out)
        return Str_out





    # Agent operations
    #---------------------------------------#
    def _remove_agent_from_all_edges(self, agent_id):
        """
        Remove an agent from all edges with specified/non-specified task_id.
        """
        for edge in self.edge_list:
            if edge.has_agent(agent_id):
                # print('INFO: Remove the agent <%d> with task <%d> from edge <%d>.' % (agent_id, edge.agent_dict[agent_id].task_id, edge.edge_id))
                edge.remove_agent(agent_id)
        #
        return True

    def _remove_agent_from_all_nodes(self, agent_id):
        """
        Remove an agent from all nodes with specified/non-specified task_id.
        """
        for node in self.node_list:
            if node.has_agent(agent_id):
                # print('INFO: Remove the agent <%d> with task <%d> from edge <%d>.' % (agent_id, edge.agent_dict[agent_id].task_id, edge.edge_id))
                node.remove_agent(agent_id)
        #
        return True


    def _remove_task_by_path(self, path, task_id, is_keeping_agent_on_last_node=False):
        """
        Remove a task according to a list of node "path"
        with specified task_id.

        inputs
            - is_keeping_agent_on_last_node (default:True):
                Decide if the last node on path (end) is going to be removed.
                (o--o--o--o--o--x <-- Does the agent on last node need to be removed?)
                Note: This is defaultly set to False for whole path cleanning.
                "False" for use in the following scenarios
                - Task finished -->
                    We should re-assign an "idle (no task, infinity time-zone)" agent
                    to the end_node.
                "True" for use in the following scenarios
                - Robot running, eatting finished path -->
                    The path in the argument is a portion of the whole path
                    , from start_id to some current node_id;
                    hence, we should keep the last node (current node_id)
        """
        # Check if this is a valid path (it's indeed a path for that edges exist between each node-pair)
        path_edge = self._get_edge_list_from_path(path)
        if path_edge is None:
            # Invalid path
            return False

        # Remove from edges
        for edge_id in path_edge:
            # Remove task
            if self.edge_list[edge_id].has_task(task_id):
                # print('INFO: Remove task <%s> from edge <%d>.' % (task_id, edge_id))
                self.edge_list[edge_id].remove_task(task_id)
        #
        # Remove from nodes
        if is_keeping_agent_on_last_node:
            path_ = path[0:-1]
        else:
            path_ = path
        #
        for node_id in path_:
            # Remove task
            if self.node_list[node_id].has_task(task_id):
                # print('INFO: Remove task <%s> from node <%d>.' % (task_id, node_id))
                self.node_list[node_id].remove_task(task_id)
        return True

    def _remove_agent_by_path(self, path, agent_id, task_id=None, is_keeping_agent_on_last_node=False):
        """
        Remove an agent according to a list of node "path" with specified/non-specified task.

        inputs
            - is_keeping_agent_on_last_node (default:True):
                Decide if the last node on path (end) is going to be removed.
                (o--o--o--o--o--x <-- Does the agent on last node need to be removed?)
                Note: This is defaultly set to False for whole path cleanning.
                "False" for use in the following scenarios
                - Task finished -->
                    We should re-assign an "idle (no task, infinity time-zone)" agent
                    to the end_node.
                "True" for use in the following scenarios
                - Robot running, eatting finished path -->
                    The path in the argument is a portion of the whole path
                    , from start_id to some current node_id;
                    hence, we should keep the last node (current node_id)
        """
        if not task_id is None:
            self._remove_task_by_path(path, task_id, is_keeping_agent_on_last_node)
            return
        # Else, any task
        # Check if this is a valid path (it's indeed a path for that edges exist between each node-pair)
        path_edge = self._get_edge_list_from_path(path)
        if path_edge is None:
            # Invalid path
            return False

        # Remove from edges
        for edge_id in path_edge:
            # Remove task
            if self.edge_list[edge_id].has_agent(task_id):
                # print('INFO: Remove task <%s> from edge <%d>.' % (task_id, edge_id))
                self.edge_list[edge_id].remove_agent(task_id)
        #
        # Remove from nodes
        if is_keeping_agent_on_last_node:
            path_ = path[0:-1]
        else:
            path_ = path
        #
        for node_id in path_:
            # Remove task
            if self.node_list[node_id].has_agent(task_id):
                # print('INFO: Remove task <%s> from node <%d>.' % (task_id, node_id))
                self.node_list[node_id].remove_agent(task_id)
        return True




    def _add_agent_by_path(self, path, T_zone_start, agent_id, task_id, is_activated=True):
        """
        Add an agent according to a list of node "path"
        with specified/non-specified task_id.
        inputs
            - path
            - T_zone_start = (T_min, T_max)
            - agent_id
            - task_id
            - is_activated
        outputs
            - True/False
        """
        # Check if this is a valid path (it's indeed a path for that edges exist between each node-pair)
        path_edge = self._get_edge_list_from_path(path)
        if path_edge is None:
            # Invalid path
            return False

        # Add to edges
        T_zone_tmp = T_zone_start
        T_zone_occ = T_zone_start
        for edge_id in path_edge:
            # Add agent
            T_zone_occ = self.edge_list[edge_id].get_T_zone_occ_from_start(T_zone_tmp)
            T_zone_tmp = self.edge_list[edge_id].get_T_zone_end_from_start(T_zone_tmp)
            self.edge_list[edge_id].put_agent(agent_id, task_id, is_activated, T_zone_occ)
            # print('INFO: Add agent <%d> with task <%s> from edge <%d>.' % (agent_id, str(self.edge_list[edge_id].agent_dict[agent_id].task_id), self.edge_list[edge_id].edge_id))
            # Note that we have to print this after adding agent

        # Add to nodes
        # TODO: Add to nodes on path, too!

        return True
    #---------------------------------------#

    # Traversal methods
    #---------------------------------------#
    def query_path_exist(self, T_zone_start, start_id, end_id, top_priority_for_activated_agent=False):
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
        # TODO: Decide if also need to check the nodes on path??
        return ( not (ge.dijkstras(self.adj_graph, self.edge_list, T_zone_start, start_id, end_id, top_priority_for_activated_agent) is None) )

    def book_a_path(self, T_zone_start, start_id, end_id, agent_id, task_id):
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
            - list of (node_id, agent_list) that obstruct the path (may be some agents idle/stop/waiting at those places)
            - T_zone_total: Total occupation time (stamp) for this path, from start to end
        """
        # Note that top_priority_for_activated_agent is set to False
        path = ge.dijkstras(self.adj_graph, self.edge_list, T_zone_start, start_id, end_id, False)
        if path is None:
            # Non-reachable
            return None
        # TODO: Check if any node on the path is occupied by "other" agents!! (maybe it's no need to check the start node?)
        # TODO: return the path, list of (node_id, agent_list) pairs for post process, T_zone_total with "None"
        # TODO: If there were any node occupied, don't book the path!

        # Else
        # Note that the activation of the agent is set to False
        self._add_agent_by_path(path, T_zone_start, agent_id, task_id, False)
        # TODO: retrun a variable indicating that there is no node being occupied by agent.
        # TODO: return T_zone_total
        return path
    #---------------------------------------#
