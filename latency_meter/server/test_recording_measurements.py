from unittest import TestCase

from latency_meter.server import Measurement, MeasurementHandler


class TestMeasurementHandler(TestCase):
    def test_given_no_measurements_returns_none(self):
        handler = MeasurementHandler()
        self.assertIsNone(handler.get_measurements_from_host('blah'))

    def test_given_a_server_when_recording_measurements_stores_average_latency(self):
        measurement = Measurement(
            from_host="192.11.00.12",
            to_host="192.00.00.99",
            average_latency=5.95
        )
        handler = MeasurementHandler()
        handler.record_measurement(measurement)
        got = handler.get_measurements_from_host('192.11.00.12')
        self.assertEqual(got, {
            '192.00.00.99': 5.95
        })
