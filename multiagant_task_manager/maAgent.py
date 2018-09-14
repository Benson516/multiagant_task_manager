

# The structure for agent
#-------------------------------#
class AGENT(object):
    """
    - agent_id (int): The id of this agent
    - task_id (int or None): The id of the task. If there is no task, keep it as "None".
    - is_activated (bool): If this agent is "currently" working
                    (there is no connection about this parameter and estimated pass time)
    - min_pass_stamp (int): estimated earliest time (unix stamp) for passing the edge
    - max_pass_stamp (int): estimated latest time (unix stamp) for passing the edge
    """
    def __init__(self, agent_id, task_id=None, is_activated=True, min_pass_stamp=0, max_pass_stamp=None):
        """
        inputs (* denote the "must-have"(mandatory) )
        * agent_id
        - task_id           (default: None)
        - is_activated      (default: True)
        - min_pass_stamp    (default: 0 sec., type: int)
        - max_pass_stamp    (default: None, the same as min_pass_time)
        """
        # Properties of the agent
        #--------------------------------------#
        # The following parameters are mandatory
        self.agent_id   = int(agent_id)

        # The following parameters have default values
        self.task_id    = (int(task_id) if (not task_id is None) else None)
        # The states
        self.is_activated = bool(is_activated)
        self.min_pass_stamp = int(min_pass_stamp)
        if max_pass_stamp is None:
            self.max_pass_stamp = self.min_pass_stamp
        else:
            max_pass_stamp = int(max_pass_stamp)
            # If the max_pass_stamp is smaller than the min_pass_stamp
            # give warning and set the max_pass_stamp equals to min_pass_stamp
            if max_pass_stamp < self.min_pass_stamp:
                self.max_pass_stamp = self.min_pass_stamp
                print('WARN: The max_pass_stamp is smaller than min_pass_stamp at agent <%d>' % self.agent_id)
            else:
                self.max_pass_stamp = max_pass_stamp
            # self.max_pass_stamp = (max_pass_stamp if max_pass_stamp >= min_pass_stamp else min_pass_stamp)

    def __str__(self):
        ret = "({ACTI}A#{AID}, T#{TID})".format(AID=self.agent_id, TID=(self.task_id if not self.task_id is None else "--"), ACTI=("o" if self.is_activated else "x" ) )
        return ret

    def is_period_intersected(self, time_stamp_range):
        """
        This method help check if the time_stamp_range is intersected with
        the occupied time period of this agent in this task.

        Because the time period is defined to be a closed set,
        the coiincident boundary points are considered to be interseted.

        input
            - time_stamp_range: a tuple of (min_pass_stamp, max_pass_stamp)
        output
            - True/False
        """
        if time_stamp_range[1] < time_stamp_range[0]:
            print('WARN: the max_pass_stamp is smaller than min_pass_stamp in time_stamp_range.')
        return (time_stamp_range[1] >= self.min_pass_stamp) and (time_stamp_range[0] <= self.max_pass_stamp)
#-------------------------------#
