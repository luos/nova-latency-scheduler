from unittest import TestCase

from network_filters import BandwidthFilter, BandwidthHint, HostBandwidthService


class MockBandwidthService(HostBandwidthService):
    bandwidths = []
    was_called_with_host = None

    def get_bandwidth_from_host(self, host):
        self.was_called_with_host = host
        return self.bandwidths


class TestBandwidthFilter(TestCase):
    def setUp(self):
        super(TestBandwidthFilter, self).setUp()
        self.measurements = MockBandwidthService()
        self.filter = BandwidthFilter(self.measurements)

    def test_given_no_bandwidth_hints_passes(self):
        self.assert_passes([])

    def test_given_a_bandwidth_hint_which_is_higher_than_bandwidth_fails(self):
        self.measurements.bandwidths = {
            'remote': 999
        }
        self.assert_doesnt_pass([BandwidthHint(1000, 'remote')])
        assert self.measurements.was_called_with_host == 'blah'

    def test_given_bandwidth_lower_than_threshold_passes(self):
        self.measurements.bandwidths = {
            'remote': 1001
        }
        self.assert_passes([BandwidthHint(1000, 'remote')])

    def test_given_multiple_hints_one_of_them_doesnt_pass_fails(self):
        self.measurements.bandwidths = {
            'remote': 1000,
            'remote2': 2000
        }
        self.assert_doesnt_pass([
            BandwidthHint(1000, 'remote'),
            BandwidthHint(3000, 'remote2'),
        ])

    def test_given_hint_when_no_data_found_returns_false(self):
        self.measurements.bandwidths = {}
        self.assert_doesnt_pass([
            BandwidthHint(1000, 'remote')
        ])

    def assert_doesnt_pass(self, hints):
        assert not self.filter.host_passes('blah', hints)

    def assert_passes(self, hints):
        assert self.filter.host_passes('blah', hints)
