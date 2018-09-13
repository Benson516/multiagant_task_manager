

# The structure for edge
#-------------------------------#
class EDGE(object):
    """
    - edge_id
    - from which node
    - to which node
    - Bidirectional?
    - capacity
    - min_pass_time: estimated minimum required time period for passing the edge
    - max_pass_time: estimated maximum required time period for passing the edge
    """
    def __init__(self, edge_id, from_node, to_node, is_bidirectional=True, capacity=1, min_pass_time=1.0, max_pass_time=None):
        """
        """
        self.edge_id = edge_id
        #
        self.from = from_node
        self.to = to_node
        self.is_bidirectional = is_bidirectional
        self.capacity = capacity
        self.min_pass_time = min_pass_time
        #
        if max_pass_time is None:
            # If there is no max_pass_time supplied, set it to be the same as min_pass_time
            self.max_pass_time = min_pass_time
        elif max_pass_time < min_pass_time:
            # We don't allow the max_pass_time to be smaller than the min_pass_time
            self.max_pass_time = min_pass_time
            print('WARN: The max_pass_time is smaller than min_pass_time at edge of (%d, %d)' % (self.from, self.to))
        else:
            self.max_pass_time = max_pass_time
#-------------------------------#
