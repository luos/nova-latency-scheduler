from unittest import TestCase

from nova.objects.request_spec import RequestSpec
from nova.scheduler.host_manager import HostState

from network_filters import NetworkAwareFilter, HostLatencyService, LatencyFilter, StaticHostLatencyService, \
    BandwidthFilter, BandwidthHint


class MockLatencyFilter(LatencyFilter):
    returns = False

    def __init__(self):
        self.was_called_with_host = None
        self.was_called_with_hints = None

    def host_passes(self, hostname, hints):
        self.was_called_with_host = hostname
        self.was_called_with_hints = hints
        return self.returns


class MockBandwidthFilter(BandwidthFilter):
    returns = False

    def __init__(self):
        self.was_called_with_hints = None

    def host_passes(self, hostname, hints):
        self.was_called_with_hints = hints
        return self.returns


class TestNetworkAwareFilter(TestCase):
    def setUp(self):
        self.mock_latency_filter = MockLatencyFilter()
        self.bandwidth_filter = MockBandwidthFilter()
        self.latency_filter = NetworkAwareFilter(
            latency_filter=self.mock_latency_filter,
            bandwidth_filter=self.bandwidth_filter
        )

    def test_given_a_request_calls_backend_filter_with_hints_and_host(self):
        self.process_request(
            self.from_hints({'to_latency': ['10, compute1', '20,gateway3']})
        )
        self.assertEqual('test-host', self.mock_latency_filter.was_called_with_host)
        self.assertEqual(
            {'to_latency': [
                '10, compute1',
                '20,gateway3'
            ]
            }, self.mock_latency_filter.was_called_with_hints)

    def from_hints(self, hints):
        request_spec = RequestSpec()
        request_spec._from_hints(hints)
        return request_spec

    def test_given_a_request_with_bandwidth_hints_calls_filter(self):
        self.process_request(
            self.from_hints({'bandwidth_to': ['10, compute1', '20,gateway3']})
        )
        self.assertEqual([
            BandwidthHint(10, 'compute1'),
            BandwidthHint(20, 'gateway3'),
        ], self.bandwidth_filter.was_called_with_hints)

    def process_request(self, request_spec):
        self.latency_filter.host_passes(HostState('test-host', 'node-name', ''), request_spec)

    def test_given_no_filter_backend_the_filter_is_static(self):
        filter = NetworkAwareFilter()
        self.assertIsInstance(filter.latency_filter, LatencyFilter)
        self.assertIsInstance(filter.latency_filter.measurements, StaticHostLatencyService)
        self.assertIsInstance(filter.bandwidth_filter, BandwidthFilter)
        self.assertIsInstance(filter.bandwidth_filter.measurements, StaticHostLatencyService)
