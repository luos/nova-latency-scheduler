import sys


class LatencyAwareSchedulerBackend():
    def __init__(self, root_to_target_latencies):
        self._root_to_target_latencies = root_to_target_latencies

    def get_host(self, near_to_host_ip):
        if not near_to_host_ip in self._root_to_target_latencies:
            return []

        latencies = self._root_to_target_latencies[near_to_host_ip]
        lowest_ip = None
        lowest_latency = sys.maxint
        for ip in latencies:
            latency = latencies[ip]
            if latency < lowest_latency:
                lowest_latency = latency
                lowest_ip = ip

        return lowest_ip
