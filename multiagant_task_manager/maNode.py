import maTask as tk


# The class for node and its states
#-------------------------------#
class NODE(object):
    """
    Properties (static)
        - node_id (int): The id of the node
        - name (string): The name of the node
        - is_stayable (bool): If the node is able to be safely stay (eternally) by an agent without blocking other agent's path
        - capacity (int): The maximum number of agent to stay/pass the node at the same time

    States (dynamically changed)
        - task_dict: dictionary of task that map from task_id to tk.TASK() object
        - idle_task_list: a list of task with task_id are all (-1) <-- idle,
                          while priorities are the higest (2) <-- occupying,
                          and the T_zone are infinite for the last one
    """
    def __init__(self, node_id, name, is_stayable=False, capacity=1):
        """
        inputs (* denote the "must-have"(mandatory) )
        * node_id
        * name
        - is_stayable       (default: False)
        - capacity          (default: 1 unit)
        """
        # Properties of the node
        #--------------------------------------#
        # The following parameters are mandatory
        self.node_id    = int(node_id)
        self.name       = name

        # The following parameters have default values
        self.is_stayable = bool(is_stayable)
        self.capacity = int(capacity)
        #--------------------------------------#

        # States of the node
        #-------------------------------#
        # Tasks on this node at specific T_zone (or stay forever)
        self.task_dict = dict() # Elements are {task_id:tk.TASK(), ...}
        #-------------------------------#

    #                   task_id, agent_id, priority=0, T_zone=(0,None)
    def put_task(self, task_id, agent_id, priority=0, T_zone=(0,None) ):
        """
        Put a new task with task_id into the task_dict
        outputs
            - True/False
        """
        if task_id in self.task_dict:
            # Task already exist!
            print('ERROR: Task<%d> already exist in the node<%s>. The task was not added.' % (task_id, self.name)  )
            return False
        # Else, seek for space
        if self.is_available_for_T_zone(T_zone, priority):
            # There exists free sapce for this task
            self.task_dict[task_id] = tk.TASK(task_id, agent_id, priority, T_zone)
            print('INFO: A task<%d> of agent<%d> is put into the node<%s>, total_task = %d' % (task_id, agent_id, self.name, len(self.task_dict) ) )
            return True
        elif self.is_available_for_T_zone(T_zone, priority, agent_id):
            # This means that the task only inteference with the agent itself
            # Note: it's OK, since an agent will not bounce into itself, simply warning
            self.task_dict[task_id] = tk.TASK(task_id, agent_id, priority, T_zone)
            print('INFO: A task<%d> of agent<%d> is put into the node<%s>, while T_zone may overlape with that of the same agent, total_task = %d' % (task_id, agent_id, self.name, len(self.task_dict) ) )
            return True
        else:
            # No free T_zone for this task, sorry
            print('ERROR: No room left for the task<%d> in the node<%s> within T_zone=%s. The task was not added.' % (task_id, self.name, str(T_zone) ) )
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
            print('INFO: Task<%d> of agent<%d> was removed from node<%s>. Then, total_task becomes %d.' % (task_id, agent_id, self.name, len(self.task_dict)) )
            return True
        else:
            # Task does not exist!
            print('WARN: Task <%d> does not exist in the node<%s>.' % (task_id, self.name ) )
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

    def has_task(self, task_id):
        """
        This method check if the task is in the task_dict
        outputs
            - True/False
        """
        return (task_id in self.task_dict)

    def has_agent(self, agent_id):
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
            # print('WARN: Task <%d> does not exist in the node<%s>.' % (task_id, self.name ) )
            pass

    def get_remained_capacity_for_T_zone(self, T_zone_occ, priority=0, agent_id=None):
        """
        Get the remained capacity of the node at given time period (unix stamp)
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
        Check if the node is available at given time period (unix stamp)
        inputs
            - T_zone_occ: a tuple of (min_pass_stamp, max_pass_stamp)
            - priority: the priority of the query (default: 0)
            - agent_id (default: None): If agent_id is given, the task of this agent
                                        with the same or smaller priority will not be counted.
        outputs
            - True: node is available for the time period required
              False: node is occupied at the time period required
        """
        # Go through all the agent, no matter the current one or future one
        return (0 < self.get_remained_capacity_for_T_zone(T_zone_occ, priority, agent_id) )


#-------------------------------#
