from unittest import TestCase

from scheduler_backend import LatencyAwareSchedulerBackend

ROOT_HOST_IP = "root_host_ip"


class TestLatencyAwareSchedulerBackend(TestCase):
    def __init__(self, methodName='runTest'):
        super(TestLatencyAwareSchedulerBackend, self).__init__(methodName)
        self.root_to_target_latencies = {}

    def test_given_a_request_when_no_hosts_are_available_returns_empty(self):
        self.root_to_target_latencies = {}
        self.assertEqual(self._get_host_near(ROOT_HOST_IP), [])

    def test_given_a_request_when_there_is_one_host_returns_that_host(self):
        self.root_to_target_latencies = {ROOT_HOST_IP: {"target_host_1": 0}}
        self.assertEqual("target_host_1", self._get_host_near(ROOT_HOST_IP))

    def test_given_a_request_when_the_second_target_has_lower_latency_returns_that_host(self):
        self.root_to_target_latencies = {
            ROOT_HOST_IP: {
                "target_host_1": 6,
                "target_host_2": 5
            }
        }
        self.assertEqual("target_host_2", self._get_host_near(ROOT_HOST_IP))

    def _get_host_near(self, host_ip):
        backend = LatencyAwareSchedulerBackend(root_to_target_latencies=self.root_to_target_latencies)
        placement_result = backend.get_host(host_ip)
        return placement_result

    def test_given_a_request_where_host_doesnt_exists_returns_empty(self):
        pass
