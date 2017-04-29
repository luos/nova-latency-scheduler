from unittest import TestCase

from heat.engine.rsrc_defn import ResourceDefinition
from heat.engine.stack import Stack

from network_aware_heat.network_aware_resources import NetworkAwareServer


class TestNetworkAwareServer(TestCase):
    def test_given_bandwidth_expecations_can_convert_into_hints(self):
        self.assertEqual(['99,node1'],
                         self.bandwidth_expectation_to_hints([{'bandwidth': 99, 'to_host': 'node1'}]))
        self.assertEqual([],
                         self.bandwidth_expectation_to_hints([]))

    def test_given_latency_expectations_can_convert_into_hints(self):
        self.assertEqual(['150,node1'], NetworkAwareServer.create_hints_from_latency_properties([{
            'to_host': 'node1',
            'latency': 150
        }]))

    def bandwidth_expectation_to_hints(self, bandwidth_expectations):
        return NetworkAwareServer.create_hints_from_bandwidth_properties(
            bandwidth_expectations
        )
