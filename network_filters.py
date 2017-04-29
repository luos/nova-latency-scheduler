from abc import ABCMeta, abstractmethod
from collections import namedtuple

from nova.objects.request_spec import RequestSpec
from nova.scheduler.host_manager import HostState
from oslo_log import log as logging
import nova.conf

from nova.scheduler.filters import BaseHostFilter

from latency_meter.server import start_server_on_other_thread

LOG = logging.getLogger(__name__)

CONF = nova.conf.CONF

LOG_TAG = "GLLS"


class NetworkAwareFilter(BaseHostFilter):
    def __init__(self,
                 latency_filter=None,
                 bandwidth_filter=None
                 ):
        """

        :type bandwidth_filter: BandwidthFilter
        :type latency_filter: LatencyFilter
        """
        super(NetworkAwareFilter, self).__init__()

        if latency_filter is not None:
            self.latency_filter = latency_filter
        else:
            self.latency_filter = create_default_filter_backend()

        if latency_filter is not None:
            self.bandwidth_filter = bandwidth_filter
        else:
            self.bandwidth_filter = create_default_bandwidth_filter()

        start_server_on_other_thread(LOG)

    def host_passes(self, host_state, spec_obj):
        """
        :type host_state: HostState
        :type spec_obj: RequestSpec
        """
        latency_passes = self.latency_filter.host_passes(host_state.host, hints=spec_obj.scheduler_hints)

        bandwidth_passes = self.bandwidth_filter.host_passes(host_state.host, self.get_bandwidth_hints(spec_obj))

        LOG.info(
            "GLLS " + host_state.host + " Latency passes: " + str(
                latency_passes) + ", Bandwidth passes: " + str(bandwidth_passes) + " with hints: " +
            str(spec_obj.scheduler_hints))

        return latency_passes and bandwidth_passes

    def get_bandwidth_hints(self, spec_obj):
        hints = []
        if 'bandwidth_to' in spec_obj.scheduler_hints:
            bandwidth_pairs = [hint.split(',') for hint in spec_obj.scheduler_hints['bandwidth_to']]
            hints = [BandwidthHint(float(hint[0]), hint[1].strip()) for hint in bandwidth_pairs]
        return hints


class HostLatencyService():
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latencies_from_host(self, host):
        pass


class HostBandwidthService():
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_bandwidth_from_host(self, host):
        pass


class StaticHostLatencyService(HostLatencyService, HostBandwidthService):
    latencies = {
        'node-2': {
            'node-3': 15,
            'node-2': 10
        },
        'node-3': {
            'node-3': 500,
            'node-2': 10
        }
    }

    bandwidth = {
        'node-2': {
            'node-3': 1000,
            'node-2': 500,
        },
        'node-3': {
            'node-3': 250,
            'node-2': 350,
        }

    }

    def get_latencies_from_host(self, host):
        return self.latencies[host]

    def get_bandwidth_from_host(self, host):
        return self.bandwidth[host]


class LatencyFilter():
    def __init__(self, measurements):
        """

        :type measurements: HostLatencyService
        """
        self.measurements = measurements

    def host_passes(self, hostname, hints):
        if 'latency_to' in hints:
            latency_expectations = [hint.split(',') for hint in hints['latency_to']]
            self._log("Scheduling with expectations: " + str(latency_expectations))
            if len(latency_expectations) > 0:
                latencies_to_host = self.measurements.get_latencies_from_host(host=hostname)
                self._log("Got latency list: " + str(latencies_to_host))
                for expected_latency, remote_host in latency_expectations:
                    if remote_host not in latencies_to_host:
                        self._log("Node " + str(remote_host) + " was not in nodes for " + hostname)
                        return False

                    latency_to_target = latencies_to_host[remote_host]
                    self._log("Checking node " + remote_host + " expected latency: " + str(
                        expected_latency) + " got latency " + str(latency_to_target))
                    if latency_to_target < float(expected_latency):
                        continue
                    else:
                        return False
                return True
            return True
        return True

    def _log(self, log):
        LOG.info(LOG_TAG + " " + str(log))


class BandwidthHint():
    def __init__(self, bandwidth_kbps, to_host):
        self.bandwidth_kbps = bandwidth_kbps
        self.to_host = to_host

    def __eq__(self, other):
        if isinstance(other, BandwidthHint):
            return other.bandwidth_kbps == self.bandwidth_kbps and other.to_host == self.to_host
        else:
            return False


class BandwidthFilter():
    def __init__(self, measurements):
        """

        :type measurements: HostBandwidthService
        """
        self.measurements = measurements

    def host_passes(self, hostname, hints):
        """

        :type hostname: str
        :type hints: list[BandwidthHint]
        """
        if len(hints) > 0:
            bandwidths = self.measurements.get_bandwidth_from_host(hostname)
            LOG.info(LOG_TAG + " BANDWIDTH to host " + hostname + " -" + str(bandwidths))
            for hint in hints:
                if hint.to_host not in bandwidths:
                    return False

                bandwidth_to_host = bandwidths[hint.to_host]
                if bandwidth_to_host >= hint.bandwidth_kbps:
                    continue
                else:
                    return False
            return True
        return True


def create_default_filter_backend():
    return LatencyFilter(StaticHostLatencyService())


def create_default_bandwidth_filter():
    return BandwidthFilter(StaticHostLatencyService())
