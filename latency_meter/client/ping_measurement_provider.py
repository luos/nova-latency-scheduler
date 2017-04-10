from subprocess import call, check_output, CalledProcessError, STDOUT

from latency_meter.client.api import MeasuredLatency
import re


class Pinger():
    PING_COUNT = 3
    ERROR_UKNOWN_HOST = "unknown-host"
    ERROR_PACKET_LOSS = "100pc-packet-loss"
    ERROR_UNKNOWN = "unknown-error"

    def __init__(self, command_runner):
        """

        :type command_runner: CommandRunner
        """
        self.command_runner = command_runner
        self._first_line_regexp = re.compile(".* packets transmitted, (?P<received_count>[\d]*) received, .*")
        self._second_line_regexp = re.compile("rtt min\/avg\/max\/mdev \= (.*)/(?P<avg>.*)/(.*)/(.*) ms")
        self._uknown_host_regexp = re.compile("(.*)ping: unknown host(.*)")

    def get_latency(self, target_host):
        # type: (str) -> MeasuredLatency


        ping_result = self._ping_host(target_host)

        result = self._check_for_errors(ping_result)
        if result:
            return result

        output = ping_result[1]

        first_line_match = self._first_line_regexp.match(output[-2])
        packet_count = int(first_line_match.groups('received_count')[0])

        second_line_match = self._second_line_regexp.match(output[-1])
        avg = second_line_match.group('avg')

        return MeasuredLatency(
            received_packet_count=packet_count,
            average_latency=float(avg),
            success=True
        )

    def _ping_host(self, target_host):
        return self.command_runner.run(["ping", "-Dn", "-c", self.PING_COUNT, target_host])

    def _check_for_errors(self, run_result):
        return_code = run_result[0]
        output = run_result[1]

        first_line_match = self._first_line_regexp.match(output[-1])

        if first_line_match:
            packet_count = int(first_line_match.groups('received_count')[0])

            if (packet_count == 0):
                return MeasuredLatency(
                    received_packet_count=0,
                    average_latency=None,
                    success=False,
                    error_code=self.ERROR_PACKET_LOSS
                )

        if self._uknown_host_regexp.match(output[-1]):
            return MeasuredLatency(
                received_packet_count=0,
                average_latency=None,
                success=False,
                error_code=self.ERROR_UKNOWN_HOST
            )

        if (return_code != 0):
            return MeasuredLatency(
                received_packet_count=None,
                average_latency=None,
                success=False,
                error_code=self.ERROR_UNKNOWN
            )
        return None


class CommandRunner():
    def run(self, command):
        """

        :type command: list
        :returns (int, str) (rc,output)
        """
        try:
            rc = 0
            result = check_output([str(c) for c in command], stderr=STDOUT)
        except CalledProcessError as e:
            rc = e.returncode
            result = e.output

        return (rc, self._process_lines(result))

    def _process_lines(self, result):
        return result.strip().splitlines()
