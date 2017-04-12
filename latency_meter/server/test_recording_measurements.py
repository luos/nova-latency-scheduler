from unittest import TestCase

from latency_meter.server import Measurement, MeasurementHandler


class TestMeasurementHandler(TestCase):
    def setUp(self):
        super(TestMeasurementHandler, self).setUp()
        self.handler = MeasurementHandler()

    def test_given_no_measurements_returns_empty_dict(self):
        self.assertEqual({},self.handler.get_measurements_from_host('blah'))

    def test_given_a_server_when_recording_measurements_stores_average_latency(self):
        measurement = Measurement(
            from_host="192.11.00.12",
            to_host="192.00.00.99",
            average_latency=5.95
        )
        self._record(measurement)

        got = self.handler.get_measurements_from_host('192.11.00.12')
        self.assertEqual(got, {
            '192.00.00.99': 5.95
        })

    def test_given_a_server_when_recording_multiple_measurements_for_same_hosts_returns_both(self):
        measurement1 = Measurement(
            from_host="192.11.00.12",
            to_host="192.00.00.99",
            average_latency=5.95
        )
        measurement2 = Measurement(
            from_host="192.11.00.12",
            to_host="192.00.00.100",
            average_latency=5.95
        )
        self._record(measurement1)
        self._record(measurement2)
        measurements = self.handler.get_measurements_from_host('192.11.00.12')
        self.assertEqual(2, len(measurements))
        self.assertEqual({
            '192.00.00.99': 5.95,
            '192.00.00.100': 5.95
        }, self.handler.get_measurements_from_host('192.11.00.12'))

    def _record(self, measurement):
        self.handler.record_measurement(measurement)
