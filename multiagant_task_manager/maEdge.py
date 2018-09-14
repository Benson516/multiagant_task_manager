import maAgent as ag

# The class for dege and its states
#-------------------------------#
class EDGE(object):
    """
    Properties (static)
        - edge_id (int): The id of this edge
        - from_node_id (int): The id of the node that this edge begin from
        - to_node_id (int): The id of the node that this edge point to
        - is_bidirectional (bool): If this edge is bi-directional
        - capacity (int): The maximum number of agent to travel the edge at the same time
        - min_pass_time (int): estimated minimum required time period for passing the edge
        - max_pass_time (int): estimated maximum required time period for passing the edge
                         (should not be smaller than min_pass_time)

    States (dynamically changed)
        - agent_dict: dictionary of agent that map from agent_id to ag.AGENT() object
        - num_activated_agent: The agent that marked is_activated=True
        - remained_capacity_now: This equals to (capacity - num_activated_agent)
    """
    #       EDGE(edge_id, from_node_id, to_node_id, is_bidirectional, capacity, min_pass_time, max_pass_time)
    def __init__(self, edge_id, from_node_id, to_node_id, is_bidirectional=True, capacity=1, min_pass_time=0, max_pass_time=None):
        """
        inputs (* denote the "must-have"(mandatory) )
        * edge_id
        * from_node_id
        * to_node_id
        - is_bidirectional  (default: True)
        - capacity          (default: 1 unit)
        - min_pass_time     (default: 0 sec., type: int)
        - max_pass_time     (default: None, the same as min_pass_time)
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
        self.min_pass_time = int(min_pass_time)
        if max_pass_time is None:
            # If there is no max_pass_time supplied, set it to be the same as min_pass_time
            self.max_pass_time = self.min_pass_time
        else:
            max_pass_time = int(max_pass_time)
            if max_pass_time < self.min_pass_time:
                # We don't allow the max_pass_time to be smaller than the min_pass_time
                self.max_pass_time = self.min_pass_time
                print('WARN: The max_pass_time is smaller than min_pass_time at edge of (%d, %d)' % (self.from_node_id, self.to_node_id))
            else:
                self.max_pass_time = max_pass_time
        #--------------------------------------#

        # States of the edge
        #-------------------------------#
        # Agents that own this edge at current time or future time
        self.agent_dict = dict() # Elements are {agent_id:ag.AGENT(), ...}

        # ** Important!! **
        # The fllowing two number should be syncing with self.agent_dict
        #-------------------------------------#
        # The total number of activated agent
        self.num_activated_agent = 0 # current running agent
        # The current/activated remained capacity of this edge
        self.remained_capacity_now = self.capacity - self.num_activated_agent # self.num_agent_now + self.remained_capacity_now = self.capacity
        #-------------------------------------#
        #-------------------------------#

    #             (agent_id, task_id, is_activated, min_pass_stamp, max_pass_stamp)
    def put_agent(self, agent_id, task_id, is_activated=True, min_pass_stamp=0, max_pass_stamp=0):
        """
        Put a 'new' agent into the agent_dict
        outputs
            - True/False
        """
        if agent_id in self.agent_dict:
            print('WARN: The agent with agent_id:<%d> already exist, skip this requirement on put_agent() at edge<%d>' % (agent_id, self.edge_id))
            return False
        else:
            if is_activated:
                if self.remained_capacity_now > 0:
                    self.num_activated_agent += 1
                    self.remained_capacity_now -= 1
                    self.agent_dict[agent_id] = ag.AGENT(agent_id, task_id, is_activated, min_pass_stamp, max_pass_stamp)
                    print('INFO: An activated agent is put into the edge<%d>, activated/total = %d/%d' % (self.edge_id, self.num_activated_agent, len(self.agent_dict)) )
                    return True
                else:
                    # Something wrong, no room left for this activated agent!!
                    print('ERROR: No room left for an activated agent in the edge<%d>. The agent <%d> was not added.' % (self.edge_id,agent_id) )
                    return False
            else:
                # Nothing, just put this non-activated agent in
                self.agent_dict[agent_id] = ag.AGENT(agent_id, task_id, is_activated, min_pass_stamp, max_pass_stamp)
                print('INFO: A non-activated agent is put into the edge<%d>, activated/total = %d/%d' % (self.edge_id, self.num_activated_agent, len(self.agent_dict)) )
                return True

    def remove_agent(self, agent_id):
        """
        Remove the exist agent
        outputs
            - True/False
        """
        if agent_id in self.agent_dict:
            #
            if self.agent_dict[agent_id].is_activated:
                self.num_activated_agent -= 1
                if self.num_activated_agent < 0:
                    self.num_activated_agent = 0
                    print('ERROR: The num_activated_agent < 0 after removal of an agent at edge <%d>.' % self.edge_id)
                #
                self.remained_capacity_now += 1
                if self.remained_capacity_now > self.capacity:
                    self.remained_capacity_now = self.capacity
                    print('ERROR: The remained_capacity_now is greater than the capacity after removal of an agent at edge <%d>.' % self.edge_id)
            #
            # Delet the agent from dict
            del self.agent_dict[agent_id]
            #
            return True # No matter what, the agent has been removed.
        else:
            # Something wrong, agent was not in the dict
            print('ERROR: The agent <%d> is not in the agent_dict at edge <%d>.' % (agent_id, self.edge_id))
            return False

    def is_agent_in_edge(self, agent_id):
        """
        This method check if the agent is in the agent_dict
        """
        return (agent_id in self.agent_dict)

    def activate_agent(self, agent_id):
        """
        This method activates the specified agent
        """
        if agent_id in self.agent_dict:
            if self.agent_dict[agent_id].is_activated:
                # The agent is already activated, do nothing
                print('WARN: The agent <%d> is already activated at edge <%d>.' % (agent_id, self.edge_id))
                return True
            else:
                if self.remained_capacity_now <= 0:
                    # Something wrong, no room left for this agent to be activated!!
                    print('WARN: No room left for the agent in the edge<%d>. The agent <%d> was not activated.' % self.edge_id)
                    return False
                else:
                    self.agent_dict[agent_id].is_activated = True
                    self.num_activated_agent += 1
                    self.remained_capacity_now -= 1
                    return True
        else:
            # Something wrong
            # Something wrong, agent was not in the dict
            print('ERROR: The agent <%d> is not in the agent_dict at edge <%d>.' % (agent_id, self.edge_id))
            return False

    def deactivate_agent(self, agent_id):
        """
        This method deactivates the specified agent
        """
        if agent_id in self.agent_dict:
            if not self.agent_dict[agent_id].is_activated:
                # The agent is already non-activated, do nothing
                print('WARN: The agent <%d> is already non-activated at edge <%d>.' % (agent_id, self.edge_id))
                return True
            else:
                self.agent_dict[agent_id].is_activated = False
                self.num_activated_agent -= 1
                self.remained_capacity_now += 1
                # Check for numbers
                if self.num_activated_agent < 0:
                    # Something wrong, remained_capacity_now is too high!!
                    print('ERROR: num_activated_agent < 0 in the edge<%d>.' % self.edge_id)
                    self.num_activated_agent = 0
                if self.remained_capacity_now > self.capacity:
                    # Something wrong, remained_capacity_now is too high!!
                    print('ERROR: remained_capacity_now > capacity in the edge<%d>.' % self.edge_id)
                    self.remained_capacity_now = self.capacity
                return True
        else:
            # Something wrong
            # Something wrong, agent was not in the dict
            print('ERROR: The agent <%d> is not in the agent_dict at edge <%d>.' % (agent_id, self.edge_id))
            return False

    def sync_agent_dict(self):
        """
        In case there might be counting error, re-sync the states of this object with agent_dict().
        outputs
            - True/False
        """
        num_activated_agent = 0
        for agent_id in self.agent_dict:
            num_activated_agent += (1 if self.agent_dict[agent_id].is_activated else 0)
        self.num_activated_agent = num_activated_agent
        self.remained_capacity_now = self.capacity - self.num_activated_agent # self.num_agent_now + self.remained_capacity_now = self.capacity
        if self.remained_capacity_now < 0:
            print('ERROR: The remained_capacity_now < 0 after removal of an agent at edge <%d>' % self.edge_id)
            self.remained_capacity_now = 0
            return False
        else:
            return True

    def get_remained_capacity_at_specific_time_period(self, time_stamp_range, only_count_activated_agent=False):
        """
        Get the remained capacity of the edge at given time period (unix stamp)
        inputs
            - time_stamp_range: a tuple of (min_pass_stamp, max_pass_stamp)
            - only_count_activated_agent: required to only count the currently activated (running) agents
        outputs
            - The remained capacity at specific time zone
        """
        # Go through all the agent, no matter the current one or future one
        agent_count = 0
        for agent_id in self.agent_dict:
            if only_count_activated_agent and (not self.agent_dict[agent_id].is_activated):
                continue # Pass this non-activated agent
            agent_count += (1 if self.agent_dict[agent_id].is_period_intersected(time_stamp_range) else 0)
        return (self.capacity - agent_count)

    def is_time_period_available(self, time_stamp_range, only_count_activated_agent=False):
        """
        Check if the edge is available at given time period (unix stamp)
        inputs
            - time_stamp_range: a tuple of (min_pass_stamp, max_pass_stamp)
            - only_count_activated_agent: required to only count the currently activated (running) agents
        outputs
            - True: edge is available for the time period required
              False: edge is occupied at the time period required
        """
        # Go through all the agent, no matter the current one or future one
        return (0 < self.get_remained_capacity_at_specific_time_period(time_stamp_range, only_count_activated_agent) )

    def is_possible_to_pass(self, time_stamp_range_start, only_count_activated_agent=False):
        """
        Given the time range that the agent might possibly begin to pass the edge,
        check if it is "safe" (conservatively) to pass the edge
        with guaranteed enough remained capacity

        Note: This method is different from the self.is_time_period_available()
              in that this function consider the passage motion of the agent,
              which require time. And, also, it's not allow that the edge become
              full during passage.

        inputs
            - time_stamp_range_start: a tuple of (min_pass_stamp, max_pass_stamp)
            - only_count_activated_agent: required to only count the currently activated (running) agents
        outputs
            - True: edge is available "starting" for the time period required
              False: edge is occupied "starting" at the time period required
        """
        # Calculate the proper time zone that this agent occupied when passing this edge
        time_stamp_range = (time_stamp_range_start[0], (time_stamp_range_start[1] + self.max_pass_time) )
        return self.is_time_period_available(time_stamp_range, only_count_activated_agent)

    def get_time_stamp_range_after_passage(self, time_stamp_range_start):
        """
        Utility function for calculating the time stamps after passage the edge,
        given time zone from start
        """
        return ( (time_stamp_range_start[0] + self.min_pass_time), (time_stamp_range_start[1] + self.max_pass_time) )
#-------------------------------#
