# TODO: Add a data structure for tasks
# TODO: Add data structure (dictionary - container_name:task_id) and operation method for agent

# The structure for task (in AGENT)
class TASK(object):
    """
    - task_id (int): The id of the task.
    - is_activated (bool): If this agent is "currently" working
                    (there is no connection about this parameter and estimated pass time)
    - T_zone = (min_pass_stamp, max_pass_stamp)
        - min_pass_stamp (int): estimated earliest time (unix stamp) for passing the edge
        - max_pass_stamp (int): estimated latest time (unix stamp) for passing the edge
    """
    def __init__(self, task_id, is_activated=False, T_zone=(0,None)):
        """
        * task_id
        - is_activated      (default: False)
        - T_zone = (min_pass_stamp, max_pass_stamp)
            - min_pass_stamp    (default: 0 sec., type: int)
            - max_pass_stamp    (default: None, infinity or eternal)
        """
        # The following parameters have default values
        self.task_id      = task_id # (int(task_id) if (not task_id is None) else None)
        # The states
        self.is_activated = bool(is_activated)
        #
        min_pass_stamp, max_pass_stamp = T_zone
        T_min = int(min_pass_stamp)
        if max_pass_stamp is None:
            T_max = float('inf') # 'None' means infinity (no maximum)
        else:
            max_pass_stamp = int(max_pass_stamp)
            # If the max_pass_stamp is smaller than the min_pass_stamp
            # give warning and set the max_pass_stamp equals to min_pass_stamp
            if max_pass_stamp < T_min:
                T_max = T_min
                print('WARN: The max_pass_stamp is smaller than min_pass_stamp at agent <%d>' % self.agent_id)
            else:
                T_max = max_pass_stamp
            # T_max = (max_pass_stamp if max_pass_stamp >= min_pass_stamp else min_pass_stamp)
        self.T_zone = (T_min, T_max)

    def __str__(self):
        ret = "<{ACTI}T#{TID}, Tz({TMIN},{TMAX})>".format(TID=(self.task_id if not self.task_id is None else "--"), ACTI=("+" if self.is_activated else "-" ), TMIN=self.T_zone[0], TMAX=self.T_zone[1] )
        return ret

    def is_period_intersected(self, T_zone):
        """
        This method help check if the T_zone is intersected with
        the occupied time period of this task.

        Because the time period is defined to be a closed set,
        the coiincident boundary points are considered to be interseted.

        input
            - T_zone: a tuple of (min_pass_stamp, max_pass_stamp)
        output
            - True/False
        """
        if T_zone[1] is None:
            # 'None' means infinity
            return (T_zone[0] <= self.T_zone[1])
        if T_zone[1] < T_zone[0]:
            print('WARN: the max_pass_stamp is smaller than min_pass_stamp in T_zone.')
        return (T_zone[1] >= self.T_zone[0]) and (T_zone[0] <= self.T_zone[1])


# The structure for agent
#-------------------------------#
class AGENT(object):
    """
    - agent_id (int): The id of this agent
    - task_dict: contains all the tasks this agent got
    - is_activated (bool): If this agent is "currently" working
                    (there is no connection about this parameter and estimated pass time)
    """
    def __init__(self, agent_id):
        """
        inputs (* denote the "must-have"(mandatory) )
        * agent_id
        """
        # Properties of the agent
        #--------------------------------------#
        # The following parameters are mandatory
        self.agent_id   = int(agent_id)

        # The states
        self.task_dict = dict() # Elements are {task_id:TASK(), ...}

        # Activation
        self.num_activated_task = 0
        self.is_activated = False # If there is a task being activated, this is set to True

    def __str__(self):
        task_dict_str = ""
        for task_id in self.task_dict:
            task_dict_str += (str(self.task_dict[task_id]) + " ")
        ret = "({ACTI}A#{AID}:{TASK_DICT})".format(AID=self.agent_id, ACTI=("+" if self.is_activated else "-" ), TASK_DICT=task_dict_str )
        return ret

    def _update_activation_state(self):
        """
        This function update the activation status of this agent.
        """
        activation_count = 0
        for task_id in self.task_dict:
            activation_count += (1 if self.task_dict[task_id].is_activated else 0)
        # Result
        self.num_activated_task = activation_count
        self.is_activated = (activation_count > 0)

    def put_task(self, task_id, is_activated=False, T_zone=(0,None)):
        """
        Give a task to this agent.
        """
        if task_id is None:
            print('ERROR: task_id cannot be "None".')
            return False

        if task_id in self.task_dict:
            # The task already exist, overwrite it
            print("WARN: The task <%s> already exists in this agent <%d>. Skip this requirement on put_task()." % (str(task_id), self.agent_id))
            return False
        else:
            """
            if self.is_period_intersected(T_zone):
                # That's OK, the agent interseted with itself will not hurt anything!
                pass
            """
            self.task_dict[task_id] = TASK(task_id, is_activated, T_zone)
            # print("INFO: A task <%s> is put into the agent <%d>" % (str(task_id), self.agent_id))
            # Update the activation state
            self._update_activation_state()
            return True


    def remove_task(self, task_id=None):
        """
        Remove a task from the agent
        If task_id is "None", delete all the tasks.
        """
        if task_id is None:
            # Delete all the tasks
            self.task_dict = dict() # Elements are {task_id:TASK(), ...}
            # Update the activation state
            self._update_activation_state()
            return True

        # Else, the task was specified
        if task_id in self.task_dict:
            # Delete the task from the task_dict
            del self.task_dict[task_id]
            # print('INFO: Task <%s> was removed from agent <%d>.' % (str(task_id), self.agent_id) )
            # Update the activation state
            self._update_activation_state()
            return True
        else:
            # Something wrong, agent was not in the dict
            print('ERROR: The task <%s> is not in the task_dict at agent <%d>.' % (str(task_id), self.agent_id))
            return False

    def activate_task(self, task_id):
        """
        This method activates the specified task
        """
        if task_id is None:
            print('ERROR: task_id cannot be "None".')
            return False
        # Else, the task was specified
        if task_id in self.task_dict:
            self.task_dict[task_id].is_activated = True
            # Update the activation state
            self._update_activation_state()
            return True
        else:
            # Something wrong, agent was not in the dict
            print('ERROR: The task <%s> is not in the task_dict at agent <%d>.' % (str(task_id), self.agent_id))
            return False

    def deactivate_task(self, task_id=None):
        """
        This method deactivates the specified task
        """
        if task_id is None:
            for task_id in self.task_dict:
                self.task_dict[task_id].is_activated = False
            # All tasks are deactivated
            self._update_activation_state()
            return True
        # Else, the task was specified
        if task_id in self.task_dict:
            self.task_dict[task_id].is_activated = False
            # Update the activation state
            self._update_activation_state()
            return True
        else:
            # Something wrong, agent was not in the dict
            print('ERROR: The task <%s> is not in the task_dict at agent <%d>.' % (str(task_id), self.agent_id))
            return False

    def number_task(self, only_count_activated_task=False):
        """
        This function return the total number of task this agent got.
        """
        if only_count_activated_task:
            return self.num_activated_task
        else:
            return len(self.task_dict)

    def is_period_intersected(self, T_zone, only_count_activated_task=False):
        """
        This method help check if the T_zone is intersected with
        the occupied time period of this agent in its tasks.

        Because the time period is defined to be a closed set,
        the coiincident boundary points are considered to be interseted.

        input
            - T_zone: a tuple of (min_pass_stamp, max_pass_stamp)
        output
            - True/False
        """
        is_intersected = False
        for task_id in self.task_dict:
            if only_count_activated_task and (not self.task_dict[task_id].is_activated):
                continue # Pass this non-activated task
            is_intersected |= self.task_dict[task_id].is_period_intersected(T_zone)
        return is_intersected
#-------------------------------#
