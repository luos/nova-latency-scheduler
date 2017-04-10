from latency_meter.client.api import MeasurementProvider


class Client:
    def __init__(self, measurement_provider):
        """

        :type measurement_provider: MeasurementProvider
        """
        self.measurement_provider = measurement_provider


