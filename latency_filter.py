from oslo_log import log as logging
import nova.conf

from nova.scheduler.filters import BaseHostFilter

from latency_meter.server import start_server_on_other_thread

LOG = logging.getLogger(__name__)

CONF = nova.conf.CONF


class LatencyAwareFilter(BaseHostFilter):
    def __init__(self):
        super(LatencyAwareFilter, self).__init__()
        LOG.debug("GLLS Starting up")
        start_server_on_other_thread(LOG)

    def host_passes(self, host_state, spec_obj):
        """
        :type host_state: nova.scheduler.host_manager.HostState
        :type spec_obj: nova.objects.request_spec.RequestSpec
        """
        LOG.debug("GLLS")
        LOG.debug("GLLS " + str(host_state))
        LOG.debug("GLLS" + str(spec_obj))
        return True
