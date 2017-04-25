from heat.engine.properties import Properties
from heat.engine.resources.openstack.nova.server import Server as NovaServer

from oslo_log import log as logging
import traceback
from heat.engine import properties
from pprint import pprint

LOG = logging.getLogger("heat.engine.resource")


def merge_props(a, b):
    c = a.copy()
    c.update(b)
    return c


class NetworkAwareServer(NovaServer):
    OS_EXT_HOST_KEY = 'OS-EXT-SRV-ATTR:host'
    EXPECTED_BANDWIDTH = 'expected_bandwidth'

    properties_schema = merge_props(NovaServer.properties_schema, {
        EXPECTED_BANDWIDTH: properties.Schema(
            properties.Schema.LIST,
            "Node - Bandwidth (kbps) key value pairs",
            schema=properties.Schema(
                properties.Schema.MAP,
                schema={
                    'to_host': properties.Schema(
                        properties.Schema.STRING,
                        'Target host'
                    ),
                    'bandwidth': properties.Schema(
                        properties.Schema.NUMBER,
                        'Expected bandwidth'
                    ),
                }
            )

        )
    })

    def handle_create(self):
        assert isinstance(self.properties, Properties)
        if self.properties[self.SCHEDULER_HINTS] is None:
            self.properties.data[self.SCHEDULER_HINTS] = {}

        if self.properties[self.EXPECTED_BANDWIDTH]:
            bandwidth_expectations = self.properties[self.EXPECTED_BANDWIDTH]
            LOG.info("GLLS Was in properties" + str(bandwidth_expectations))

            self.properties.data[self.SCHEDULER_HINTS]['bandwidth_to'] = \
                self.create_hints_from_bandwidth_properties(bandwidth_expectations)

        LOG.info("GLLS" + str(self.properties[self.SCHEDULER_HINTS]))

        return super(NetworkAwareServer, self).handle_create()

    @classmethod
    def create_hints_from_bandwidth_properties(cls, bandwidth_expectations):
        return [str(be['bandwidth']) + ',' + be['to_host'] for be in bandwidth_expectations]

    def get_attribute(self, key, *path):
        if key == "host":
            server, data = self.get_live_resource_data()
            return data.get(self.OS_EXT_HOST_KEY)
        return super(NetworkAwareServer, self).get_attribute(key, *path)


def resource_mapping():
    return {
        'OS::NetworkAware::Server': NetworkAwareServer,
    }
