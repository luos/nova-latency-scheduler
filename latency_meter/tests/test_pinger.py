from unittest import TestCase

from latency_meter.client.api import MeasuredLatency
from latency_meter.client.ping_measurement_provider import Pinger, CommandRunner


class TestPinger(TestCase):
    def test_given_a_ping_calls_command_runner_with_host(self):
        command_runner = MockCommandRunner(
            command_output="3 packets transmitted, 3 received, 0% packet loss, time 1998ms\n"
                           "rtt min/avg/max/mdev = 0.402/0.580/0.701/0.128 ms"
        )
        pinger = Pinger(command_runner=command_runner)
        pinger.get_latency("test-host")
        self.assertEqual(
            command_runner.was_called_with_command,
            ["ping", "-Dn", "-c", Pinger.PING_COUNT, "test-host"]
        )

    def test_given_a_ping_parses_output_and_returns_measured_latency(self):
        got = self.run_pinger_with_output(
            "3 packets transmitted, 3 received, 0% packet loss, time 1998ms\n"
            "rtt min/avg/max/mdev = 0.402/0.580/0.701/0.128 ms"
        )
        expected = MeasuredLatency(3, 0.58, success=True)
        self.assertEqual(expected.packet_count, got.packet_count)
        self.assertEqual(expected.average_latency, got.average_latency)
        self.assertTrue(got.success)

    def test_given_more_ping_output_parses_correctly(self):
        ping_output = """PING index.hu (217.20.130.99) 56(84) bytes of data.
[1491753086.899682] 64 bytes from 217.20.130.99: icmp_seq=1 ttl=57 time=9.43 ms
[1491753087.900707] 64 bytes from 217.20.130.99: icmp_seq=2 ttl=57 time=8.77 ms
[1491753088.902781] 64 bytes from 217.20.130.99: icmp_seq=3 ttl=57 time=8.90 ms

--- index.hu ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2003ms
rtt min/avg/max/mdev = 8.773/9.039/9.437/0.286 ms
        """
        got = self.run_pinger_with_output(ping_output)
        expected = MeasuredLatency(3, 9.039, True)
        self.assertEqual(expected.packet_count, got.packet_count)
        self.assertEqual(expected.average_latency, got.average_latency)
        self.assertTrue(got.success)

    def test_given_100_percent_packet_loss_return_error(self):
        got = self.run_pinger_with_output("""
PING 240.0.0.1 (240.0.0.1) 56(84) bytes of data.

--- 240.0.0.1 ping statistics ---
3 packets transmitted, 0 received, 100% packet loss, time 1999ms

""")
        self.assertFalse(got.success)
        self.assertEqual(Pinger.ERROR_PACKET_LOSS, got.error_code)
        self.assertIsNone(got.average_latency)
        self.assertEqual(0, got.packet_count)

    def test_given_a_command_returns_with_nonzero_return_code_but_the_error_doesnt_match_return_unknown_error(self):
        failing_runner = MockCommandRunner("This error was very unexpected.", return_code=1)
        got = self._run_with_command_runner(failing_runner)
        self.assertFalse(got.success)
        self.assertEqual(Pinger.ERROR_UNKNOWN, got.error_code)

    def test_given_a_command_returns_unknown_host_expect_error_unknown_host(self):
        failing_runner = MockCommandRunner(
            """ping: unknown host a-host.unknown
            """
            , return_code=2)
        got = self._run_with_command_runner(failing_runner)
        self.assertFalse(got.success)
        self.assertEqual(Pinger.ERROR_UKNOWN_HOST, got.error_code)

    def run_pinger_with_output(self, ping_output):
        command_runner = MockCommandRunner(
            command_output=ping_output
        )
        got = self._run_with_command_runner(command_runner)
        return got

    def _run_with_command_runner(self, command_runner):
        pinger = Pinger(command_runner=command_runner)
        got = pinger.get_latency("test-host")
        return got


class MockCommandRunner(CommandRunner):
    def __init__(self, command_output, return_code=0):
        self.rc = return_code
        self.was_called_with_command = None
        self.command_output = command_output

    def run(self, command):
        self.was_called_with_command = command
        return (self.rc, self._process_lines(self.command_output))
