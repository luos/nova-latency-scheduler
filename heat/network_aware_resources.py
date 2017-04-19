from heat.engine.resources.openstack.nova.server import Server as NovaServer

from oslo_log import log as logging
import traceback

LOG = logging.getLogger(__name__)


class NetworkAwareServer(NovaServer):
    OS_EXT_HOST_KEY = 'OS-EXT-SRV-ATTR:host'

    def get_attribute(self, key, *path):
        if key == "host":
            server, data = self.get_live_resource_data()
            return data.get(self.OS_EXT_HOST_KEY)
        return super(NetworkAwareServer, self).get_attribute(key, *path)


def resource_mapping():
    return {
        'OS::NetworkAware::Server': NetworkAwareServer,
    }
