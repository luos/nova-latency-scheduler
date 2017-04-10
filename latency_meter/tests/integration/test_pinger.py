import unittest

from latency_meter.client.ping_measurement_provider import Pinger, CommandRunner


class TestPingerIntegration(unittest.TestCase):
    def test_given_a_real_command_runner_can_ping_localhost(self):
        pinger = Pinger(CommandRunner())
        result = pinger.get_latency("localhost")
        self.assertTrue(result.success)
        self.assertEqual(Pinger.PING_COUNT, result.packet_count)

    def test_given_a_made_up_ip_100_pc_packet_loss(self):
        pinger = Pinger(CommandRunner())
        result = pinger.get_latency("240.0.0.1") #unallocated block
        self.assertFalse(result.success)
        self.assertEqual(Pinger.ERROR_PACKET_LOSS, result.error_code)
        self.assertEqual(0, result.packet_count)

    def test_given_an_unknown_host_returns_unknown_host_error(self):
        pinger = Pinger(CommandRunner())
        result = pinger.get_latency("thisisanunknown.host")
        self.assertFalse(result.success)
        self.assertEqual(Pinger.ERROR_UKNOWN_HOST, result.error_code)
        self.assertEqual(0, result.packet_count)
