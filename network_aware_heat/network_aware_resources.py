from heat.engine.properties import Properties
from heat.engine.resources.openstack.nova.server import Server as NovaServer

from oslo_log import log as logging

from heat.engine import properties

LOG = logging.getLogger("heat.engine.resource")


def merge_props(a, b):
    c = a.copy()
    c.update(b)
    return c


class NetworkAwareServer(NovaServer):
    OS_EXT_HOST_KEY = 'OS-EXT-SRV-ATTR:host'
    EXPECTED_BANDWIDTH = 'expected_bandwidth'
    MAXIMUM_LATENCY = 'maximum_latency'

    properties_schema = merge_props(NovaServer.properties_schema, {
        EXPECTED_BANDWIDTH: properties.Schema(
            properties.Schema.LIST,
            "Node - Bandwidth (kbps) map",
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
        ),
        MAXIMUM_LATENCY: properties.Schema(
            properties.Schema.LIST,
            'Node - Latency (ms) map',
            schema=properties.Schema(
                properties.Schema.MAP,
                schema={
                    'to_host': properties.Schema(
                        properties.Schema.STRING,
                        'Target host'
                    ),
                    'latency': properties.Schema(
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
            LOG.info("GLLS Got bandwidth expectations" + str(bandwidth_expectations))

            self.properties.data[self.SCHEDULER_HINTS]['bandwidth_to'] = \
                self.create_hints_from_bandwidth_properties(bandwidth_expectations)
        if self.properties[self.MAXIMUM_LATENCY]:
            maximum_latencies = self.properties[self.MAXIMUM_LATENCY]
            LOG.info("GLLS Got maximum latency" + str(maximum_latencies))
            self.properties.data[self.SCHEDULER_HINTS]['latency_to'] = \
                self.create_hints_from_latency_properties(maximum_latencies)

        LOG.info("GLLS " + str(self.properties[self.SCHEDULER_HINTS]))

        return super(NetworkAwareServer, self).handle_create()

    @classmethod
    def create_hints_from_bandwidth_properties(cls, bandwidth_expectations):
        return [str(be['bandwidth']) + ',' + be['to_host'] for be in bandwidth_expectations]

    @classmethod
    def create_hints_from_latency_properties(cls, maximum_latencies):
        return [str(be['latency']) + ',' + be['to_host'] for be in maximum_latencies]

    def get_attribute(self, key, *path):
        if key == "host":
            server, data = self.get_live_resource_data()
            return data.get(self.OS_EXT_HOST_KEY)
        return super(NetworkAwareServer, self).get_attribute(key, *path)


def resource_mapping():
    return {
        'OS::NetworkAware::Server': NetworkAwareServer,
    }
