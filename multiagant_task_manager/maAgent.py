

# The structure for agent
#-------------------------------#
class AGENT(object):
    """
    - agent_id
    - task_id
    - is_activated
    - min_pass_stamp: estimated earliest time (unix stamp) for passing the edge
    - max_pass_stamp: estimated latest time (unix stamp) for passing the edge
    """
    def __init__(self, agent_id, task_id, is_activated=True, min_pass_stamp=0, max_pass_stamp=0):
        """
        """
        self.agent_id   = agent_id
        self.task_id    = task_id

        # The states
        self.is_activated = is_activated
        #
        self.min_pass_stamp = min_pass_stamp
        # If the max_pass_stamp is smaller than the min_pass_stamp
        # give warning and set the max_pass_stamp equals to min_pass_stamp
        if max_pass_stamp < min_pass_stamp:
            self.max_pass_stamp = min_pass_stamp
            print('ERROR: The max_pass_stamp is smaller than min_pass_stamp at (agent_id, task_id) = (%d, %d)' % (self.agent_id, self.task_id))
        else:
            self.max_pass_stamp = max_pass_stamp
        # self.max_pass_stamp = (max_pass_stamp if max_pass_stamp >= min_pass_stamp else min_pass_stamp)

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
