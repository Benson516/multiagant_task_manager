import maAgent as ag

# The class for dege states
#-------------------------------#
class EDGE_STATE(object):
    """
    - edge_id: inherited from EDGE()
    - capacity: inherited from EDGE()

    - agent_dict: dictionary of agent that map from agent_id to ag.AGENT() object
    - num_activated_agent: The agent that marked is_activated=True
    - remained_capacity_now: This equals to (capacity - num_activated_agent)
    """
    def __init__(self, edge_id, capacity_of_edge):
        """
        """
        # The edge (id) of this edge_state belongs to
        self.edge_id = edge_id
        # Capacity of the edge, fixed value
        self.capacity = capacity_of_edge

        # Agents that own this edge at current time or future time
        self.agent_dict = dict() # Elements are {agent_id:ag.AGENT(), ...}

        # Important!!
        # The fllowing two number should be syncing with self.agent_dict
        #------------------------------------------#
        # The total number of activated agent
        self.num_activated_agent = 0 # current running agent
        # The current/activated remained capacity of this edge
        self.remained_capacity_now = self.capacity - self.num_activated_agent # self.num_agent_now + self.remained_capacity_now = self.capacity
        #------------------------------------------#

    def put_agent(self, agent_id, task_id, is_activated=True, min_pass_stamp=0, max_pass_stamp=0):
        """
        Put a 'new' agent into the agent_dict
        outputs
            - True/False
        """
        if agent_id in self.agent_dict:
            print('WARN: The agent with agent_id:<%d> already exist, skip this requirement on put_agent()' % agent_id)
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
        if not agent_id in self.agent_dict:
            # Something wrong
            # Something wrong, agent was not in the dict
            print('ERROR: The agent <%d> is not in the agent_dict at edge <%d>.' % (agent_id, self.edge_id))
            return False
        # else
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

    def deactivate_agent(self, agent_id):
        """
        This method deactivates the specified agent
        """
        if not agent_id in self.agent_dict:
            # Something wrong
            # Something wrong, agent was not in the dict
            print('ERROR: The agent <%d> is not in the agent_dict at edge <%d>.' % (agent_id, self.edge_id))
            return False
        # else
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

    def sync_agent_dict(self):
        """
        In case there might be counting error, re-sync the states of this object with agent_dict().
        outputs
            - True/False
        """
        num_activated_agent = 0
        for agent in self.agent_dict:
            num_activated_agent += (1 if agent.is_activated else 0)
        self.num_activated_agent = num_activated_agent
        self.remained_capacity_now = self.capacity - self.num_activated_agent # self.num_agent_now + self.remained_capacity_now = self.capacity
        if self.remained_capacity_now < 0:
            print('ERROR: The remained_capacity_now < 0 after removal of an agent at edge <%d>' % self.edge_id)
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
        for agent in self.agent_dict:
            if only_count_activated_agent and (not agent.is_activated):
                continue # Pass this non-activated agent
            agent_count += (1 if agent.is_period_intersected(time_stamp_range) else 0)
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
#-------------------------------#
