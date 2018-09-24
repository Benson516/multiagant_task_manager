import maAgent as ag

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
        - agent_dict: dictionary of agent that map from agent_id to ag.AGENT() object
        - num_activated_agent: The agent that marked is_activated=True
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
        min_pass_time, max_pass_time = duration
        dT_min = int(min_pass_time)
        if max_pass_time is None:
            # If there is no max_pass_time supplied, set it to be the same as min_pass_time
            dT_max = float('inf') # 'None' means infinity (no maximum)
        else:
            max_pass_time = int(max_pass_time)
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
        # Agents that own this edge at current time or future time
        self.agent_dict = dict() # Elements are {agent_id:ag.AGENT(), ...}

        # ** Important!! **
        # The fllowing numbers should be syncing with self.agent_dict
        #-------------------------------------#
        # The total number of activated agent
        self.num_activated_agent = 0 # current running agent
        #-------------------------------------#
        #-------------------------------#

    def _sync_agent_dict(self):
        """
        In case there might be counting error, re-sync the states of this object with agent_dict().
        outputs
            - True/False
        """
        num_activated_agent = 0
        for agent_id in self.agent_dict:
            num_activated_agent += (1 if self.agent_dict[agent_id].is_activated else 0)
        self.num_activated_agent = num_activated_agent
        return True

    #             (agent_id, task_id, is_activated, min_pass_stamp, max_pass_stamp)
    def put_agent(self, agent_id, task_id, is_activated=False, T_zone=(0,None)):
        """
        Put a 'new' agent into the agent_dict
        outputs
            - True/False
        """
        if not agent_id in self.agent_dict:
            self.agent_dict[agent_id] = ag.AGENT(agent_id)
        # else
        if self.is_available_for_T_zone(T_zone, only_count_activated_agent=False):
            if self.agent_dict[agent_id].put_task(task_id, is_activated, T_zone):
                if is_activated:
                    self.num_activated_agent += 1
                    print('INFO: An activated agent <%d> with task <%s> is put into the edge<%d>, activated/total = %d/%d' % (agent_id, str(task_id), self.edge_id, self.num_activated_agent, len(self.agent_dict)) )
                else:
                    print('INFO: A non-activated agent <%d> with task <%s> is put into the edge<%d>, activated/total = %d/%d' % (agent_id, str(task_id), self.edge_id, self.num_activated_agent, len(self.agent_dict)) )
                return True
            else:
                # Somthing wrong
                print('ERROR: Somthing wrong in put_task() for agent <%d> with task <%s> in the edge<%d> within T_zone=%s. The agent was not added.' % (agent_id, str(task_id), self.edge_id , str(T_zone) ) )
                return False
        else:
            # Something wrong, no room left for this activated agent!!
            print('ERROR: No room left for an agent in the edge<%d> within T_zone=%s. The agent <%d> was not added.' % (self.edge_id, agent_id, str(T_zone) ) )
            return False


    def remove_agent(self, agent_id, task_id=None):
        """
        Remove the exist agent
        outputs
            - True/False
        """
        if agent_id in self.agent_dict:
            was_activated = self.agent_dict[agent_id].is_activated
            if self.agent_dict[agent_id].remove_task(task_id):
                if was_activated and (not self.agent_dict[agent_id].is_activated):
                    # No more being activated
                    self.num_activated_agent -= 1
                    if self.num_activated_agent < 0:
                        self.num_activated_agent = 0
                        print('ERROR: The num_activated_agent < 0 after removal of an agent at edge <%d>.' % self.edge_id)
                #
                if self.agent_dict[agent_id].number_task(only_count_activated_task=False) == 0:
                    # Remove this agent
                    del self.agent_dict[agent_id]
                    print('INFO: Agent <%d> was totally removed from edge <%d>. Then, activated/total becomes %d/%d.' % (agent_id, self.edge_id, self.num_activated_agent, len(self.agent_dict) ))
                else:
                    print('INFO: Agent <%d> with task <%s> was removed from edge <%d>. Then, activated/total becomes %d/%d.' % (agent_id, str(task_id), self.edge_id, self.num_activated_agent, len(self.agent_dict)) )
                return True
            else:
                # Something wrong, task was not in the task_dict
                print('ERROR: The task <%s> is not in the task_dict of agent <%d> at edge <%d>.' % (str(task_id), agent_id, self.edge_id))
                return False
        else:
            # Something wrong, agent was not in the agent_dict
            print('ERROR: The agent <%d> is not in the agent_dict at edge <%d>.' % (agent_id, self.edge_id))
            return False

    def is_agent_in_edge(self, agent_id):
        """
        This method check if the agent is in the agent_dict
        """
        return (agent_id in self.agent_dict)

    def activate_agent(self, agent_id, task_id):
        """
        This method activates the specified agent
        """
        if agent_id in self.agent_dict:
            if self.agent_dict[agent_id].activate_task(task_id):
                self._sync_agent_dict()
                return True
            else:
                print('ERROR: The agent <%d> with task <%s> is not activated at edge <%d>.' % (agent_id, str(task_id), self.edge_id))
                return False
        else:
            # Something wrong
            # Something wrong, agent was not in the dict
            print('ERROR: The agent <%d> is not in the agent_dict at edge <%d>.' % (agent_id, self.edge_id))
            return False

    def deactivate_agent(self, agent_id, task_id=None):
        """
        This method deactivates the specified agent
        """
        if agent_id in self.agent_dict:
            if self.agent_dict[agent_id].deactivate_task(task_id):
                self._sync_agent_dict()
                return True
            else:
                print('ERROR: The agent <%d> with task <%s> is not de-activated at edge <%d>.' % (agent_id, str(task_id), self.edge_id))
                return False
        else:
            # Something wrong
            # Something wrong, agent was not in the dict
            print('ERROR: The agent <%d> is not in the agent_dict at edge <%d>.' % (agent_id, self.edge_id))
            return False

    def get_remained_capacity_for_T_zone(self, T_zone_occ, only_count_activated_agent=False, agent_id=None):
        """
        Get the remained capacity of the edge at given time period (unix stamp)
        inputs
            - T_zone_occ: a tuple of (min_pass_stamp, max_pass_stamp)
            - only_count_activated_agent: required to only count the currently activated (running) agents
            - agent_id (default: None): If agent_id is given, ignore this agent in this edge.
        outputs
            - The remained capacity at specific time zone
        """
        # Go through all the agent, no matter the current one or future one
        agent_count = 0
        for agent_id_i in self.agent_dict:
            if agent_id_i == agent_id:
                continue
            if only_count_activated_agent and (not self.agent_dict[agent_id_i].is_activated):
                continue # Pass this non-activated agent
            agent_count += (1 if self.agent_dict[agent_id_i].is_period_intersected(T_zone_occ) else 0)
        return (self.capacity - agent_count)

    def is_available_for_T_zone(self, T_zone_occ, only_count_activated_agent=False, agent_id=None):
        """
        Check if the edge is available at given time period (unix stamp)
        inputs
            - T_zone_occ: a tuple of (min_pass_stamp, max_pass_stamp)
            - only_count_activated_agent: required to only count the currently activated (running) agents
            - agent_id (default: None): If agent_id is given, ignore this agent in this edge.
        outputs
            - True: edge is available for the time period required
              False: edge is occupied at the time period required
        """
        # Go through all the agent, no matter the current one or future one
        return (0 < self.get_remained_capacity_for_T_zone(T_zone_occ, only_count_activated_agent, agent_id) )

    def is_possible_to_pass(self, T_zone_start, only_count_activated_agent=False, agent_id=None):
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
            - only_count_activated_agent: required to only count the currently activated (running) agents
            - agent_id (default: None): If agent_id is given, ignore this agent in this edge.
        outputs
            - True: edge is available "starting" from the time period required
              False: edge is occupied "starting" from the time period required
        """
        # Calculate the proper time zone that this agent occupied when passing this edge
        T_zone_occ = self.get_T_zone_occ_from_start(T_zone_start)
        return self.is_available_for_T_zone(T_zone_occ, only_count_activated_agent)

    def is_possible_to_pass_backtrack(self, T_zone_end, only_count_activated_agent=False, agent_id=None):
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
            - only_count_activated_agent: required to only count the currently activated (running) agents
            - agent_id (default: None): If agent_id is given, ignore this agent in this edge.
        outputs
            - True: edge is available "ending" at the time period required
              False: edge is occupied "ending" at the time period required
        """
        # Calculate the proper time zone that this agent occupied when passing this edge
        T_zone_occ = self.get_T_zone_occ_from_end(T_zone_end)
        return self.is_available_for_T_zone(T_zone_occ, only_count_activated_agent)

    def get_T_zone_occ_from_start(self, T_zone_start):
        """
        Utility function for calculating the maximum time-zone stamps during the edge,
        given time zone from start
        inputs
            - T_zone_start
        outputs
            - T_zone_occ
        """
        return ( T_zone_start[0], (T_zone_start[1] + self.duration[1]) )

    def get_T_zone_occ_from_end(self, T_zone_end):
        """
        Utility function for calculating the maximum time-zone stamps during the edge,
        given time zone from end
        inputs
            - T_zone_end
        outputs
            - T_zone_occ
        """
        return ( (T_zone_end[0] - self.duration[0]), T_zone_end[1] )

    def get_T_zone_end_from_start(self, T_zone_start):
        """
        Utility function for calculating the time stamps after passage the edge,
        given time zone from start
        inputs
            - T_zone_start
        outputs
            - T_zone_end
        """
        return ( (T_zone_start[0] + self.duration[0]), (T_zone_start[1] + self.duration[1]) )

    def get_T_zone_start_from_end(self, T_zone_end):
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
