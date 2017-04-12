from unittest import TestCase

from nova.objects.request_spec import RequestSpec
from nova.scheduler.host_manager import HostState

from latency_filter import LatencyAwareFilter, HostLatencyService, LatencyHostFilter, StaticHostLatencyService


class MockLatencyFilter(LatencyHostFilter):
    returns = False

    def __init__(self):
        self.was_called_with_host = None
        self.was_called_with_hints = None

    def host_passes(self, hostname, hints):
        self.was_called_with_host = hostname
        self.was_called_with_hints = hints
        return self.returns


class TestLatencyAwareFilter(TestCase):
    def test_given_a_request_calls_backend_filter_with_hints_and_host(self):
        mock_latency_filter = MockLatencyFilter()
        latency_filter = LatencyAwareFilter(
            filter_backend=mock_latency_filter
        )
        request_spec = RequestSpec()
        request_spec._from_hints({'to_latency': ['10, compute1', '20,gateway3']})
        latency_filter.host_passes(HostState('test-host', 'node-name'), request_spec)
        self.assertEqual('test-host', mock_latency_filter.was_called_with_host)
        self.assertEqual(
            {'to_latency': [
                '10, compute1',
                '20,gateway3'
            ]
            }, mock_latency_filter.was_called_with_hints)

    def test_given_no_filter_backend_the_filter_is_static(self):
        filter = LatencyAwareFilter()
        self.assertIsInstance(filter.filter_backend, LatencyHostFilter)
        self.assertIsInstance(filter.filter_backend.latencies, StaticHostLatencyService)
