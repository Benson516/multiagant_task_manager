import maTask as tk

# The class for edge and its states
#-------------------------------#
class EDGE(object):
    """
    Properties (static)
        - edge_id (int): The id of this edge
        - from_node_id (int): The id of the node that this edge begin from
        - to_node_id (int): The id of the node that this edge point to
        - is_bidirectional (bool): If this edge is bi-directional
        - capacity (int): The maximum number of agent to travel the edge at the same time
        - duration = (min_pass_time, max_pass_time)
            - min_pass_time (int): estimated minimum required time period for passing the edge
            - max_pass_time (int): estimated maximum required time period for passing the edge
                                  (should not be smaller than min_pass_time)

    States (dynamically changed)
        - task_dict: dictionary of agent that map from task_id to tk.TASK() object
    """
    #       EDGE(edge_id, from_node_id, to_node_id, is_bidirectional, capacity, duration)
    def __init__(self, edge_id, from_node_id, to_node_id, is_bidirectional=True, capacity=1, duration=(0,0)):
        """
        inputs (* denote the "must-have"(mandatory) )
        * edge_id
        * from_node_id
        * to_node_id
        - is_bidirectional  (default: True)
        - capacity          (default: 1 unit)
        - duration          (default: (0,0), type: int, None means infinity. dT)
        """
        # Properties of the edge
        #--------------------------------------#
        # The following parameters are mandatory
        self.edge_id = int(edge_id)
        self.from_node_id = int(from_node_id)
        self.to_node_id = int(to_node_id)

        # The following parameters have default values
        self.is_bidirectional = bool(is_bidirectional)
        self.capacity = int(capacity)
        #
        dT_min = int(duration[0])
        if duration[1] is None:
            # If there is no max_pass_time supplied, set it to be the same as min_pass_time
            dT_max = float('inf') # 'None' means infinity (no maximum)
        else:
            max_pass_time = int(duration[1])
            if max_pass_time < dT_min:
                # We don't allow the max_pass_time to be smaller than the min_pass_time
                dT_max = dT_min
                print('WARN: The max_pass_time is smaller than min_pass_time at edge of (%d, %d)' % (self.from_node_id, self.to_node_id))
            else:
                dT_max = max_pass_time
        #
        self.duration = (dT_min, dT_max)
        #--------------------------------------#

        # States of the edge
        #-------------------------------#
        # Tasks on this edge at specific T_zone
        self.task_dict = dict() # Elements are {task_id:tk.TASK(), ...}
        #-------------------------------#


    #                   task_id, agent_id, priority=0, T_zone=(0,0)
    def put_task(self, task_id, agent_id, priority=0, T_zone=(0,None) ):
        """
        Put a new task with task_id into the task_dict
        outputs
            - True/False
        """
        if task_id in self.task_dict:
            # Task already exist!
            print('ERROR: Task<%d> already exist in the edge<%d>. The task was not added.' % (task_id, self.edge_id)  )
            return False
        # Else, seek for space
        if self.is_available_for_T_zone(T_zone, priority):
            # There exists free sapce for this task
            self.task_dict[task_id] = tk.TASK(task_id, agent_id, priority, T_zone)
            print('INFO: A task<%d> of agent<%d> is put into the edge<%d>, total_task = %d' % (task_id, agent_id, self.edge_id, len(self.task_dict) ) )
            return True
        elif self.is_available_for_T_zone(T_zone, priority, agent_id):
            # This means that the task only inteference with the agent itself
            # Note: it's OK, since an agent will not bounce into itself, simply warning
            self.task_dict[task_id] = tk.TASK(task_id, agent_id, priority, T_zone)
            print('INFO: A task<%d> of agent<%d> is put into the edge<%d>, while T_zone may overlape with that of the same agent, total_task = %d' % (task_id, agent_id, self.edge_id, len(self.task_dict) ) )
            return True
        else:
            # No free T_zone for this task, sorry
            print('ERROR: No room left for the task<%d> in the edge<%d> within T_zone=%s. The task was not added.' % (task_id, self.edge_id, str(T_zone) ) )
            return False

    def remove_task(self, task_id):
        """
        Remove the task with task_id
        outputs
            - True/False
        """
        if task_id in self.task_dict:
            # Simply delete it
            del self.task_dict[task_id]
            print('INFO: Task<%d> of agent<%d> was removed from edge<%d>. Then, total_task becomes %d.' % (task_id, agent_id, self.edge_id, len(self.task_dict)) )
            return True
        else:
            # Task does not exist!
            print('WARN: Task <%d> does not exist in the edge<%d>.' % (task_id, self.edge_id ) )
            return False

    def remove_agent(self, agent_id):
        """
        Remove all tasks of the agent.
        outputs
            --
        """
        rm_task_list = list()
        for task_id in self.task_dict:
            if self.task_dict[task_id].agent_id == agent_id:
                rm_task_list.append(task_id)
        # Delete those tasks
        for task_id in rm_task_list:
            self.remove_task(task_id)

    def remove_low_priority(self, priority):
        """
        Remove all the task with priority <= the input priority
        outputs
            --
        """
        rm_task_list = list()
        for task_id in self.task_dict:
            if self.task_dict[task_id].priority <= priority:
                rm_task_list.append(task_id)
        # Delete those tasks
        for task_id in rm_task_list:
            self.remove_task(task_id)

    def have_task(self, task_id):
        """
        This method check if the task is in the task_dict
        outputs
            - True/False
        """
        return (task_id in self.task_dict)

    def have_agent(self, agent_id):
        """
        This method check if the agent is in the task_dict
        outputs
            - True/False
        """
        for task_id in self.task_dict:
            if self.task_dict[task_id].agent_id == agent_id:
                return True
        return False

    def update_task_priority(self, task_id, priority):
        """
        This method change the priority of the specified task.
        outputs
            --
        """
        if task_id in self.task_dict:
            self.task_dict[task_id].priority = priority
        else:
            # print('WARN: Task <%d> does not exist in the edge<%d>.' % (task_id, self.edge_id ) )
            pass

    def get_remained_capacity_for_T_zone(self, T_zone_occ, priority=0, agent_id=None):
        """
        Get the remained capacity of the edge at given time period (unix stamp)
        inputs
            - T_zone_occ: a tuple of (min_pass_stamp, max_pass_stamp)
            - priority: the priority of the query (default: 0)
            - agent_id (default: None): If agent_id is given, the task of this agent
                                        with the same or smaller priority will not be counted.
        outputs
            - The remained capacity at specific time zone
        """
        # Go through all the task
        task_count = 0
        for task_id_i in self.task_dict:
            task_count += (1 if self.task_dict[task_id_i].is_period_intersected(T_zone_occ, priority, agent_id) else 0)
        return (self.capacity - task_count)

    def is_available_for_T_zone(self, T_zone_occ, priority=0, agent_id=None):
        """
        Check if the edge is available at given time period (unix stamp)
        inputs
            - T_zone_occ: a tuple of (min_pass_stamp, max_pass_stamp)
            - priority: the priority of the query (default: 0)
            - agent_id (default: None): If agent_id is given, the task of this agent
                                        with the same or smaller priority will not be counted.
        outputs
            - True: edge is available for the time period required
              False: edge is occupied at the time period required
        """
        # Go through all the agent, no matter the current one or future one
        return (0 < self.get_remained_capacity_for_T_zone(T_zone_occ, priority, agent_id) )

    def is_possible_to_pass(self, T_zone_start, priority=0, agent_id=None):
        """
        Given the time range that the agent might possibly begin to pass the edge,
        check if it is "safe" (conservatively) to pass the edge
        with guaranteed enough remained capacity

        Note: This method is different from the self.is_available_for_T_zone()
              in that this function consider the passage motion of the agent,
              which requires time. And, also, it's not allow that the edge become
              full during passage.

        inputs
            - T_zone_start: a tuple of (min_pass_stamp, max_pass_stamp)
            - priority: the priority of the query (default: 0)
            - agent_id (default: None): If agent_id is given, the task of this agent
                                        with the same or smaller priority will not be counted.
        outputs
            - True: edge is available "starting" from the time period required
              False: edge is occupied "starting" from the time period required
        """
        # Calculate the proper time zone that this agent occupied when passing this edge
        T_zone_occ = self._get_T_zone_occ_from_start(T_zone_start)
        return self.is_available_for_T_zone(T_zone_occ, priority, agent_id)

    def is_possible_to_pass_backtrack(self, T_zone_end, priority=0, agent_id=None):
        """
        Given the time range that the agent might possibly begin to "inversely" pass the edge,
        check if it is "safe" (conservatively) to pass the edge
        with guaranteed enough remained capacity

        Note: This method is different from the self.is_available_for_T_zone()
              in that this function consider the passage motion of the agent,
              which requires time. And, also, it's not allow that the edge become
              full during passage.

        inputs
            - T_zone_end: a tuple of (min_pass_stamp, max_pass_stamp)
            - priority: the priority of the query (default: 0)
            - agent_id (default: None): If agent_id is given, the task of this agent
                                        with the same or smaller priority will not be counted.
        outputs
            - True: edge is available "ending" at the time period required
              False: edge is occupied "ending" at the time period required
        """
        # Calculate the proper time zone that this agent occupied when passing this edge
        T_zone_occ = self._get_T_zone_occ_from_end(T_zone_end)
        return self.is_available_for_T_zone(T_zone_occ, priority, agent_id)

    #------ utilities ------#
    def _get_T_zone_occ_from_start(self, T_zone_start):
        """
        Utility function for calculating the maximum time-zone stamps during the edge,
        given time zone from start
        inputs
            - T_zone_start
        outputs
            - T_zone_occ
        """
        return ( T_zone_start[0], (T_zone_start[1] + self.duration[1]) )

    def _get_T_zone_occ_from_end(self, T_zone_end):
        """
        Utility function for calculating the maximum time-zone stamps during the edge,
        given time zone from end
        inputs
            - T_zone_end
        outputs
            - T_zone_occ
        """
        return ( (T_zone_end[0] - self.duration[0]), T_zone_end[1] )

    def _get_T_zone_end_from_start(self, T_zone_start):
        """
        Utility function for calculating the time stamps after passage the edge,
        given time zone from start
        inputs
            - T_zone_start
        outputs
            - T_zone_end
        """
        return ( (T_zone_start[0] + self.duration[0]), (T_zone_start[1] + self.duration[1]) )

    def _get_T_zone_start_from_end(self, T_zone_end):
        """
        Utility function for calculating the time stamps before passage the edge,
        given time zone from end
        inputs
            - T_zone_end
        outputs
            - T_zone_start
        """
        return ( (T_zone_end[0] - self.duration[0]), (T_zone_end[1] - self.duration[1]) )
#-------------------------------#
