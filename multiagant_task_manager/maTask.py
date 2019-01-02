
# The structure for task
class TASK(object):
    """
    - task_id (int): The id of the task.
    - agent_id (int): The id of the agent.
    - priority (int): The priority of task (simply a container, the value is defined at higer level)
    - T_zone = (min_pass_stamp, max_pass_stamp)
        - min_pass_stamp (int): estimated earliest time (unix stamp) for passing the edge
        - max_pass_stamp (int): estimated latest time (unix stamp) for passing the edge
    """
    def __init__(self, task_id, agent_id, priority=0, T_zone=(0,None)):
        """
        * task_id (-1: only valid for NODEs, idle task, the agent stay there)
        * agent_id
        - priority      (default: 0, negative means that it can be deleted by system)
        - T_zone = (min_pass_stamp, max_pass_stamp)
            - min_pass_stamp    (default: 0 sec., type: int)
            - max_pass_stamp    (default: None, infinity or eternal)
        """
        # The following parameters have default values
        self.task_id    = int(task_id) # (int(task_id) if (not task_id is None) else None)
        self.agent_id   = int(agent_id)
        # The priority
        self.priority = int(priority)
        #
        T_min = int(T_zone[0])
        if T_zone[1] is None:
            T_max = float('inf') # 'None' means infinity (no maximum)
        else:
            max_pass_stamp = int(T_zone[1])
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
        ret = "<T#{TID}, A#{AID}, P{PRIO}, Tz{TZONE}>".format(TID=self.task_id, AID=self.agent_id, PRIO=self.priority, TZONE=self.T_zone )
        return ret

    def is_period_intersected(self, T_zone_in, priority_in=0, agent_id_in=None):
        """
        This method help check if the T_zone_in is intersected with
        the occupied time period of this task.

        Because the time period is defined to be a closed set,
        the coiincident boundary points are considered to be interseted.

        input
            - T_zone_in: a tuple of (min_pass_stamp, max_pass_stamp)
            - priority_in: a integer value indicates the priority level of the T_zone_in,
                           if priority_in > self.priority, then viewed as no intersection.
            - agent_id_in: the agent_id of the provided T_zone_in,
                           if agent_id_in is provided (not None) and the agent_id is the same as this task,
                           then the same priority one can also be treated as invisible.
        output
            - True/False
        """
        # Compare the priority
        if priority_in > self.priority:
            return False
        # If the agent_id_in is the same as this one
        if agent_id_in == self.agent_id:
            if priority_in >= self.priority:
                return False
        #
        if T_zone_in[1] is None:
            # 'None' means infinity
            return (T_zone_in[0] <= self.T_zone[1])
        if T_zone_in[1] < T_zone_in[0]:
            print('WARN: the max_pass_stamp is smaller than min_pass_stamp in T_zone_in.')
        return (T_zone_in[1] >= self.T_zone[0]) and (T_zone_in[0] <= self.T_zone[1])
