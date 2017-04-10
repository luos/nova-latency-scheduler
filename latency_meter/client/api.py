class MeasurementProvider():
    pass


class MeasuredLatency():
    def __init__(self, received_packet_count, average_latency, success, error_code=None):
        self.error_code = error_code
        self.success = success
        self.average_latency = average_latency
        self.packet_count = received_packet_count
