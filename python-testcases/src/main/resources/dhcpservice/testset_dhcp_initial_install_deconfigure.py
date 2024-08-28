'''
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     April 2015
@author:    Philip Daly
@summary:   Integration
            Agile: STORY-dhcp
'''

from litp_generic_test import GenericTest, attr
import test_constants


class Storydhcp(GenericTest):
    """
    As a LITP Architect I want a filesystem to be tagged as snap_externally so
    that Database Specific Plugins can explicitly generate DB specific snapshot
    tasks for their filesystems.
    """

    def setUp(self):
        """
        Description:
            Runs before every single test.
        Actions:

            1. Call the super class setup method.
            2. Set up variables used in the tests.
        Results:
            The super class prints out diagnostics and variables
            common to all tests are available.
        """
        # 1. Call super class setup
        super(Storydhcp, self).setUp()

        # 2. Set up variables used in the test
        self.ms_node = self.get_management_node_filename()

        self.node_urls = self.find(self.ms_node, "/deployments", "node")
        self.node_urls.sort()
        # Current assumption is that only 1 VCS cluster will exist
        self.vcs_cluster_url = self.find(self.ms_node,
                                         "/deployments", "vcs-cluster")[-1]

    def tearDown(self):
        """
        Description:
            Run after each test and performs the following:
        Actions:
            1. Cleanup after test if global results value has been used
            2. Call the superclass teardown method
        Results:
            Items used in the test are cleaned up and the
            super class prints out end test diagnostics
        """
        super(Storydhcp, self).tearDown()

    def get_deployment_dhcp_services(self, ipv6=False):
        """
        Description:
            Function to retrieve all of the dhcp service references in the
            model below the deployment.
        Args:
            ipv6 (bool): Boolean value indicating whether for ipv4 or ipv6 dhcp
                         services the search is to be issued.
        Returns:
            list. A list of all the dhcp services found
                  below each node.
        """
        dhcp_services = []
        for node_url in self.node_urls:
            if not ipv6:
                dhcp_services.extend(self.find(self.ms_node,
                                               node_url,
                                               "reference-to-dhcp-service"))
            else:
                dhcp_services.extend(self.find(self.ms_node,
                                               node_url,
                                               "reference-to-dhcp6-service"))

        return dhcp_services

    def get_software_dhcp_services(self, ipv6=False):
        """
        Description:
            Function to retrieve all of the dhcp service references in the
            model below the software section.
        Args:
            ipv6 (bool): Boolean value indicating whether for ipv4 or ipv6 dhcp
                         services the search is to be issued.
        Returns:
            list. A list containing a list of all the dhcp services found
                  below the software section.
        """
        dhcp_services = []
        if not ipv6:
            dhcp_services.extend(self.find(self.ms_node,
                                           '/software',
                                           "dhcp-service"))
        else:
            dhcp_services.extend(self.find(self.ms_node,
                                           '/software',
                                           "dhcp6-service"))

        return dhcp_services

    def get_dhcp_network_hosts(self):
        """
        Description:
            Function to retrieve all of the network hosts of the dhcp_network.
        Returns:
            list. A list of all the network hosts on the dhcp_network.
        """
        network_hosts = (self.find(self.ms_node,
                                   self.vcs_cluster_url + '/network_hosts/',
                                   "vcs-network-host"))
        dhcp_hosts = []
        for host_url in network_hosts:
            network_name = \
            self.get_props_from_url(self.ms_node, host_url,
                                    filter_prop="network_name")
            if network_name == "dhcp_network":
                dhcp_hosts.append(host_url)

        return dhcp_hosts

    def get_dhcp_bridges(self):
        """
        Description:
            Function to retrieve a list of all the bridges on the dhcp network.
        Returns:
            list. A list of all the bridges on the dhcp_network.
        """
        dhcp_bridges = []
        for node_url in self.node_urls:
            node_bridges = (self.find(self.ms_node,
                                      node_url,
                                      "bridge"))

            for bridge_url in node_bridges:
                network_name = \
                self.get_props_from_url(self.ms_node, bridge_url,
                                        filter_prop="network_name")
                if network_name == "dhcp_network":
                    dhcp_bridges.append(bridge_url)

        return dhcp_bridges

    def get_dhcp_bridge_eths(self, bridges):
        """
        Description:
            Function to retrieve all of the eths using the bridges on the
            dhcp_network.
        Args:
            bridges (list): A list of all the bridges on the dhcp network.
        Returns:
            list. A list of all the eths using the bridges on the dhcp_network.
        """
        dhcp_eths = []
        for bridge_url in bridges:
            device_name = \
            self.get_props_from_url(self.ms_node, bridge_url,
                                    filter_prop="device_name")

            split_url = bridge_url.split('/')
            split_url.pop(-1)
            parent_url = "".join(["/" + x for x in split_url if x != ''])
            node_eths = (self.find(self.ms_node,
                                   parent_url,
                                   "eth"))
            for eth_url in node_eths:
                bridge_name = \
                self.get_props_from_url(self.ms_node, eth_url,
                                        filter_prop="bridge")
                if device_name == bridge_name:
                    dhcp_eths.append(eth_url)
                    break

        return dhcp_eths

    @attr('all', 'non-revert', 'story8716', 'story8716_tc01')
    def test_01_deconfigure_initial_install_dhcp(self):
        """
        @tms_id: litpcds_8716_tc01
        @tms_requirements_id: LITPCDS-8716
        @tms_title: Deconfigure existing dhcp config
        @tms_description: Remove dhcp related items and config
        @tms_test_steps:
            @step: Find all dhcp services under the nodes.
            @result: All dhcp-service items returned from /node
            @step: Find all dhcp services in software
            @result: All dhcp-service items returned from /software
            @step: Find all network hosts on the dhcp network
            @result: All network hosts returned from dhcp network
            @step: Find all bridges on the dhcp network
            @result: All bridges from dhcp network returned
            @step: Find all eths using the bridges.
            @result: All eth interfaces from dhcp network returned
            @step: Deconfigure all of the above.
            @result: All found items removed successfully
        @tms_test_precondition:  N/A
        @tms_execution_type: Automated
        """
        dhcp_deployment_srvcs = self.get_deployment_dhcp_services()
        dhcp_soft_srvcs = self.get_software_dhcp_services()
        dhcp_network_hosts = self.get_dhcp_network_hosts()
        dhcp_bridges = self.get_dhcp_bridges()
        dhcp_eths = self.get_dhcp_bridge_eths(dhcp_bridges)
        # REMOVE DHCP FROM THE NODES
        for node_url in dhcp_deployment_srvcs:
            self.execute_cli_remove_cmd(self.ms_node, node_url,
                                        add_to_cleanup=False)
        # REMOVE DHCP FROM SOFTWARE
        for definition_url in dhcp_soft_srvcs:
            self.execute_cli_remove_cmd(self.ms_node, definition_url,
                                        add_to_cleanup=False)
        # REMOVE DHCP NETWORK HOSTS
        for network_host in dhcp_network_hosts:
            self.execute_cli_remove_cmd(self.ms_node, network_host,
                                        add_to_cleanup=False)

        # REMOVE BRIDGES
        for bridge in dhcp_bridges:
            self.execute_cli_remove_cmd(self.ms_node, bridge,
                                        add_to_cleanup=False)

        # REMOVE ETHS
        for eth in dhcp_eths:
            self.execute_cli_remove_cmd(self.ms_node, eth,
                                        add_to_cleanup=False)

        self.execute_cli_createplan_cmd(self.ms_node)
        self.execute_cli_runplan_cmd(self.ms_node)
        self.assertTrue(self.wait_for_plan_state(self.ms_node,
                                                 test_constants.PLAN_COMPLETE))
