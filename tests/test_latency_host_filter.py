from unittest import TestCase

from network_filters import LatencyFilter, HostLatencyService


class TestLatencyHostFilter(TestCase):
    def setUp(self):
        super(TestLatencyHostFilter, self).setUp()
        self.latencies = MockHostLatencyService()
        self.filter = LatencyFilter(self.latencies)

    def test_given_a_host_with_no_hints_passes(self):
        self.assertPasses("test-host", {})

    def test_given_a_host_with_a_latency_hint_but_no_latency_info_fails(self):
        self.latencies.returns({})
        self.assertFails('test-host', {'latency_to': ['50,target1']})

    def test_given_a_host_with_a_latency_hint_and_latency_info_passes(self):
        self.latencies.returns({'target1': 30})
        self.assertPasses('test-host', {'latency_to': ['50,target1']})

    def test_given_a_host_with_higher_latency_than_the_hint_fails(self):
        self.latencies.returns({'target1': 1000})
        self.assertFails('test-host', {'latency_to': ['50,target1']})

    def test_given_a_host_with_multiple_latencies_if_no_less_than_expected_fails(self):
        self.latencies.returns({
            'target2': 10000,
            'target1': 1000,
            'target24': 3333
        })
        self.assertFails('test-host', {'latency_to': ['50,target1']})

    def test_given_a_host_with_multiple_latencies_with_less_than_the_hint_passes(self):
        self.latencies.returns({
            'target2': 10000,
            'target1': 1000,
            'target24': 3333
        })
        self.assertPasses('test-host', {'latency_to': ['1001,target1']})

    def test_given_multiple_expectations_when_meets_expectations_passes(self):
        self.latencies.returns({
            'target2': 50,
            'target1': 60,
        })
        self.assertPasses('test-host', {'latency_to': ['1001,target1', '500,target2']})

    def test_given_multiple_expectations_when_doesnt_meet_expectations_fails(self):
        self.latencies.returns({
            'target2': 5000,
            'target1': 6000,
        })
        self.assertFails('test-host', {'latency_to': ['1001,target1', '500,target2']})

    def test_given_multiple_expectations_when_one_host_doesnt_exist_fails(self):
        self.latencies.returns({
            'target1': 5000,
        })
        self.assertFails('test-host', {'latency_to': ['1001,target1', '500,target2']})


    def test_given_multiple_expectations_when_successful_passes(self):
        self.latencies.returns({
            'target3': 24234,
            'target2': 2000,
            'target1': 1000,
        })
        self.assertPasses('test-host', {'latency_to': ['1001,target1', '2001,target2']})

    def test_given_multiple_expectations_one_of_them_fails_then_fails(self):
        self.latencies.returns({
            'target3': 24234,
            'target2': 2002,
            'target1': 1000,
        })
        self.assertFails('test-host', {'latency_to': ['1001,target1', '2001,target2']})


    def assertFails(self, host, hints):
        assert self.filter.host_passes(host, hints) == False

    def assertPasses(self, host, hints):
        assert self.filter.host_passes(host, hints) == True


class MockHostLatencyService(HostLatencyService):
    latencies = {}

    def get_latencies_from_host(self, host):
        return self.latencies

    def returns(self, latencies):
        self.latencies = latencies
