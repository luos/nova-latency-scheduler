from abc import ABCMeta, abstractmethod

from nova.objects.request_spec import RequestSpec
from nova.scheduler.host_manager import HostState
from oslo_log import log as logging
import nova.conf

from nova.scheduler.filters import BaseHostFilter

from latency_meter.server import start_server_on_other_thread

LOG = logging.getLogger(__name__)

CONF = nova.conf.CONF


class LatencyAwareFilter(BaseHostFilter):
    def __init__(self, filter_backend=None):
        """

        :type filter_backend: LatencyHostFilter
        """
        super(LatencyAwareFilter, self).__init__()
        if filter_backend is not None:
            self.filter_backend = filter_backend
        else:
            self.filter_backend = create_default_filter_backend()
        start_server_on_other_thread(LOG)

    def host_passes(self, host_state, spec_obj):
        """
        :type host_state: HostState
        :type spec_obj: RequestSpec
        """
        passes = self.filter_backend.host_passes(host_state.host, hints=spec_obj.scheduler_hints)
        LOG.debug(
            "GLLS " + host_state.host + " passes: " + str(passes) + " with hints: " + str(spec_obj.scheduler_hints))
        return passes


class HostLatencyService():
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_measurements_from_host(self, host):
        pass


class StaticHostLatencyService(HostLatencyService):
    data = {
        'node-2': {
            'node-3': 15
        },
        'node-3': {
            'node-3': 500
        }
    }

    def get_measurements_from_host(self, host):
        return self.data[host]


class LatencyHostFilter():
    def __init__(self, latencies):
        """

        :type latencies: HostLatencyService
        """
        self.latencies = latencies

    def host_passes(self, hostname, hints):
        if 'latency_to' in hints:
            latency_expectations = [hint.split(',') for hint in hints['latency_to']]
            print(latency_expectations)
            if len(latency_expectations) > 0:
                latencies_to_host = self.latencies.get_measurements_from_host(host=hostname)
                LOG.debug("GLLS Got latency list: " + str(latencies_to_host))
                for expected_latency, remote_host in latency_expectations:
                    if remote_host not in latencies_to_host:
                        LOG.debug("Node " + str(remote_host) + " was not in nodes for " + hostname)
                        return False

                    latency_to_target = latencies_to_host[remote_host]
                    LOG.debug(
                        "GLLS Checking node " + remote_host + " expected latency: " + str(
                            expected_latency) + " got latency " + str(latency_to_target))
                    if latency_to_target < float(expected_latency):
                        return True
                    else:
                        continue
                return False
            return True
        return True


def create_default_filter_backend():
    return LatencyHostFilter(StaticHostLatencyService())
