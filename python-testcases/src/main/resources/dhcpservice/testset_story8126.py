'''
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     Febuary 2015
@author:    Boyan Mihovski, Kieran Duggan, Remy Horton, Carlos Novo
@summary:   Integration
            Agile: STORY-8126
'''

from litp_generic_test import GenericTest, attr
import test_constants
from test_constants import PLAN_TASKS_INITIAL


class Story8126(GenericTest):
    """
    As a LITP user I want to specify a DHCP service to run on a
    pair of peer nodes so that there is a DHCP service available
    for virtual machines running in the LITP complex (ipv6 only).
    """

    test_node_if1 = None
    test_node_if2 = None
    test_node2_if1 = None
    test_node2_if2 = None
    nics_node1 = None
    nics_node2 = None
    test_ms_if1 = None

    ipv4_subnet_prefix = None
    ipv4_subnets = None
    ipv6_prefixes = None
    ipv6_masks = None
    ipv6_networks = None

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
        super(Story8126, self).setUp()

        # 2. Set up variables used in the test
        self.ms_node = self.get_management_node_filenames()[0]

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
        super(Story8126, self).tearDown()

    def create_two_networks_two_interfaces(self, provoke_fail=False):
        """
        Description:
            Litp create two test interfaces and networks per node:
        Actions:
            1. Litp create two test interfaces and networks
                for two dhcp subnets (IPv6 only).
        Results:
            litp create command for direct plan task execution
        """
        node_urls = self.find(self.ms_node, "/deployments", "node")
        node_urls.sort()

        self.ipv6_prefixes = [
            '2001:2200:82a1:103',
            '2001:5500:82a1:103:4355:3267'
            ]
        self.ipv6_masks = ['/64', '/96']
        self.ipv6_networks = ['test1', 'test2']

        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]
        # CREATE TEST NETWORK 1
        network_url = networks_path + "/test_network8126"
        props = "name='{0}'".format(self.ipv6_networks[0])
        self.execute_cli_create_cmd(self.ms_node, network_url,
                                    "network", props)

        # CREATE TEST NETWORK 2
        network_url = networks_path + "/test_network8127"
        props = "name='{0}'".format(self.ipv6_networks[1])
        self.execute_cli_create_cmd(self.ms_node, network_url,
                                    "network", props)

        free_nics = \
            self.verify_backup_free_nics(self.ms_node, node_urls[0],
                                         required_free_nics=2)
        self.test_node_if1 = free_nics[0]
        self.test_node_if2 = free_nics[1]

        if provoke_fail:
            # We want run_plan to fail: force invalid MAC
            self.test_node_if1["MAC"] = "FF:FF:FF:FF:FF:FF"

        free_nics = \
            self.verify_backup_free_nics(self.ms_node, node_urls[1],
                                         required_free_nics=2)
        self.test_node2_if1 = free_nics[0]
        self.test_node2_if2 = free_nics[1]

        # node1 eth1
        if_url = node_urls[0] + "/network_interfaces/if_8126"
        ipv6 = "{0}::2{1}".format(self.ipv6_prefixes[0], \
                                        self.ipv6_masks[0])
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='{2}' \
                    ipv6address='{3}'".\
                    format(self.test_node_if1["MAC"],
                           self.test_node_if1["NAME"],
                           self.ipv6_networks[0],
                           ipv6)

        self.execute_cli_create_cmd(self.ms_node, if_url, "eth", eth_props)

        # node1 eth2
        if_url = node_urls[0] + "/network_interfaces/if_8127"
        ipv6 = "{0}::2{1}".format(self.ipv6_prefixes[1], \
                                        self.ipv6_masks[1])
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='{2}' \
                    ipv6address='{3}'".\
                    format(self.test_node_if2["MAC"],
                           self.test_node_if2["NAME"],
                           self.ipv6_networks[1],
                           ipv6)

        self.execute_cli_create_cmd(self.ms_node, if_url, "eth", eth_props)

        # node2 eth1
        if_url = node_urls[1] + "/network_interfaces/if_8126"
        ipv6 = "{0}::3{1}".format(self.ipv6_prefixes[0], \
                                        self.ipv6_masks[0])
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='{2}' \
                    ipv6address='{3}'".\
                    format(self.test_node2_if1["MAC"],
                           self.test_node2_if1["NAME"],
                           self.ipv6_networks[0],
                           ipv6)

        self.execute_cli_create_cmd(self.ms_node, if_url, "eth", eth_props)

        # node2 eth2
        if_url = node_urls[1] + "/network_interfaces/if_8127"
        ipv6 = "{0}::3{1}".format(self.ipv6_prefixes[1], \
                                self.ipv6_masks[1])
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='{2}' \
                    ipv6address='{3}'".\
                    format(self.test_node2_if2["MAC"],
                           self.test_node2_if2["NAME"],
                           self.ipv6_networks[1],
                           ipv6)

        self.execute_cli_create_cmd(self.ms_node, if_url, "eth", eth_props)

        self.nics_node1 = [self.test_node_if1["NAME"],
                           self.test_node_if2["NAME"]]
        self.nics_node2 = [self.test_node2_if1["NAME"],
                           self.test_node2_if2["NAME"]]

    def create_network_and_interfaces(self):
        """
        Description:
            Litp create one test interface and network per node:
        Actions:
            1. Litp create one test interface and network
                for one dhcp subnets (IPv4 and IPv6).
        Results:
            litp create command for direct plan task execution
        """
        self.ipv4_subnet_prefix = '40.40.40.'
        self.ipv4_subnets = [self.ipv4_subnet_prefix + '0/24']
        self.ipv6_prefixes = ['2001:2200:82a1:103']
        self.ipv6_masks = ['/64']
        self.ipv6_networks = ['test1']

        node_urls = self.find(self.ms_node, "/deployments", "node")
        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]
        # CREATE TEST NETWORK 1
        network_url = networks_path + "/test_network8126"
        props = "name='{0}' subnet='{1}'".format(self.ipv6_networks[0],
                                                 self.ipv4_subnets[0])
        self.execute_cli_create_cmd(self.ms_node, network_url,
                                    "network", props)

        # Add an eth to the nodes with an ipaddress on the associated network
        free_nics = \
            self.verify_backup_free_nics(self.ms_node, node_urls[0])
        self.test_node_if1 = free_nics[0]

        free_nics = \
            self.verify_backup_free_nics(self.ms_node, node_urls[1])
        self.test_node2_if1 = free_nics[0]

        # node1 eth
        if_url = node_urls[0] + "/network_interfaces/if_8126"
        ipv4 = "{0}1".format(self.ipv4_subnet_prefix)
        ipv6 = "{0}::2{1}".format(self.ipv6_prefixes[0],
                                  self.ipv6_masks[0])
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='{2}' ipaddress='{3}' \
                    ipv6address='{4}'".\
                    format(self.test_node_if1["MAC"],
                           self.test_node_if1["NAME"],
                           self.ipv6_networks[0],
                           ipv4,
                           ipv6)

        self.execute_cli_create_cmd(self.ms_node, if_url, "eth", eth_props)

        # node2 eth
        if_url = node_urls[1] + "/network_interfaces/if_8126"
        ipv4 = "{0}2".format(self.ipv4_subnet_prefix)
        ipv6 = "{0}::3{1}".format(self.ipv6_prefixes[0],
                                  self.ipv6_masks[0])
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='{2}' ipaddress='{3}' \
                    ipv6address='{4}'".\
                    format(self.test_node2_if1["MAC"],
                           self.test_node2_if1["NAME"],
                           self.ipv6_networks[0],
                           ipv4,
                           ipv6)

        self.execute_cli_create_cmd(self.ms_node, if_url, "eth", eth_props)

        self.nics_node1 = [self.test_node_if1["NAME"]]
        self.nics_node2 = [self.test_node2_if1["NAME"]]

    def interfaces_cleanup(self, nodes, node1_ifs, node2_ifs):
        """
        Description:
            Clean up the used ip addresses (testing framework - work around)
        Args:
            nodes (list): all nodes to be de configured.
            node1_ifs (list): used interfaces  - node1.
            node2_ifs (list): used interfaces - node2.
        Results:
            The IP settings are restored.
        """

        self.assertEqual(len(node1_ifs), len(node2_ifs))

        # len(node1_ifs) is always == len(mode2_ifs)
        # and always there is one subnet per used nic

        number_of_subnets = len(node1_ifs)

        if number_of_subnets == 2:

            # NODE1 DECONFIGURE test interface 1
            self.add_nic_to_cleanup(nodes[0],
                                    node1_ifs[0],
                                    flush_ip=True)
            # NODE1 DECONFIGURE test interface 2
            self.add_nic_to_cleanup(nodes[0],
                                    node1_ifs[1],
                                    flush_ip=True)
            # NODE2 DECONFIGURE test interface 1
            self.add_nic_to_cleanup(nodes[1],
                                    node2_ifs[0],
                                    flush_ip=True)
            # NODE2 DECONFIGURE test interface 2
            self.add_nic_to_cleanup(nodes[1],
                                    node2_ifs[1],
                                    flush_ip=True)
        else:
            # NODE1 DECONFIGURE test interface 1
            self.add_nic_to_cleanup(nodes[0],
                                    node1_ifs[0],
                                    flush_ip=True)
            # NODE2 DECONFIGURE test interface 2
            self.add_nic_to_cleanup(nodes[1],
                                    node2_ifs[0],
                                    flush_ip=True)

    def check_existents_of_the_confs(self, node_fname, dhcpd_conf,
                                     dhcpd_pools, dhcpd_sysconf):
        """
        Description:
            Check that /etc/dhcp/dhcpd6.conf, /etc/sysconfig/dhcpd6 and
            /etc/dhcp/dhcpd.pools are populated after
            the dhcp service installation.
        Args:
            node_fname (str): all nodes to be de configured.
            dhcpd_conf (str): path to dhcpd6.conf.
            dhcpd.pools (list): path to dhcpd6.pools.
            dhcpd_sysconf (str): path to dhcpd6 sysconf file.
        Results:
            The errors generated after the validation.
        """
        errors = []
        # check the existence of dhcpd.conf into the node
        if not self.remote_path_exists(node_fname,
                                       dhcpd_conf):
            errors.append("dhcpd6.conf doesn't exist into the node")
        # check the existence of /etc/sysconfig/dhcpd6
        if not self.remote_path_exists(node_fname,
                                       dhcpd_sysconf):
            errors.append("/etc/sysconfig/dhcpd6" +
                          "doesn't exist into the node")

        # check the existence of dhcpd.pools into the nodes
        if not self.remote_path_exists(node_fname,
                                       dhcpd_pools):
            errors.append("dhcpd6.pools" +
                          "doesn't exist into the node")
        # check the existence of /etc/sysconfig/dhcpd6
        if not self.remote_path_exists(node_fname,
                                       dhcpd_sysconf):
            errors.append("/etc/sysconfig/dhcpd6" +
                          "doesn't exist into the node")

        # check the existence of dhcpd.pools into the nodes
        if not self.remote_path_exists(node_fname,
                                       dhcpd_pools):
            errors.append("dhcpd6.pools" +
                          "doesn't exist into the node")

        return errors

    def check_dhcpd_conf_content(self, node_path, dhcpd_conf, role):
        """
        Description:
            Checking /etc/sysconfig/dhcpd6 values after successfull plan.
        Args:
            node_path (list): all nodes to be configured.
            dhcpd_conf (str): path to conf file configured.
            role (str): Role of the server.
        Results:
            The errors generated after the validation.
        """
        # check one node
        errors = []
        # CHECK dhcpd.conf FILE CONTENT NODES
        std_out = self.get_file_contents(node_path, dhcpd_conf,
                                         su_root=True)

        server_role = "option dhcp6.preference {0};".format(role)

        if not self.is_text_in_list(server_role, std_out):
            errors.append('The node dhcp v6 role '
                          'is not correct')

        return errors

    def check_sysconf_dhcpd_content(self, node_fname, node_ifs, dhcpd_sysconf):
        """
        Description:
            Checking /etc/sysconfig/dhcpd6 values after successfull plan.
        Args:
            node_fname (list): all nodes to be configured.
            node_ifs (list): Used networking adapters.
            dhcpd_sysconf (str): path to dhcpd6 sysconf file.
        Results:
            The errors generated after the validation.
        """
        errors = []

        std_out = self.get_file_contents(node_fname,
                                         dhcpd_sysconf)
        expected = 'DHCPDARGS=" ' + ' '.join(iface for iface in node_ifs) + '"'
        if not self.is_text_in_list(expected, std_out):
            errors.append("The dhcp v6 server" +
                          " not listening the correct adapter, expected: {0}".
                          format(expected))

        return errors

    def check_pools_conf_subnet(self, std_out, dhcp_subnet):
        """
        Description:
            Checking /etc/dhcp/dhcpd.pool values for subnets
            after successfull plan, when single subnet is configured.
        Args:
            std_out (list): The content of the file after successfull plan.
            dhcp_subnet (list): used dhcp subnets and subnet masks.
        Results:
            The errors generated after the validation.
        """

        errors = []

        for item in dhcp_subnet:
            expected_subnet = "subnet6 {0}".format(item[0])
            if not self.is_text_in_list(expected_subnet, std_out):
                errors.append(
                    'Incorrect subnet config for {0}'.format(item[0])
                    )
            self.assertEqual(len(dhcp_subnet),
                             self.count_text_in_list("subnet6 ", std_out))
        return errors

    def check_pools_conf_ranges(self, std_out, ranges):
        """
        Description:
            Checking /etc/dhcp/dhcpd6.pool values for IP ranges
            after successfull plan.
        Args:
            std_out (list): The content of the file after successfull plan.
            ranges (list): Used dhcp v6 ranges.
        Results:
            The errors generated after the validation.
        """

        errors = []

        for item in ranges:
            if isinstance(item, tuple):
                range_start, range_end = item
                expected = "range6 {0} {1};".format(range_start, range_end)
            else:
                expected = "range6 {0} {1};".format(item[0], item[1])
            if not self.is_text_in_list(expected, std_out):
                errors.append(
                    'The dhcp v6 {0} configuration is not correct'.format(
                        expected
                        )
                    )

            self.assertEqual(len(ranges),
                             self.count_text_in_list("range6", std_out))
        return errors

    def data_driven_verification(self, node_urls,
                                 node1_ifs, node2_ifs,
                                 dhcp_subnet, ranges):
        """
        Description:
            Check system configuration, output of the executed plan.
        Args:
            node_urls (list): all nodes to be configured.
            node1_ifs (list): used interfaces  - node1.
            node2_ifs (list): used interfaces - node2.
            dhcp_subnet (list): network addresses for used subnets.
            ranges (list): Used dhcp v6 ranges.
        Results:
            stderr of checking configuration
        """
        errors = []
        # dhcpd.conf path
        dhcpd_conf = "{0}/dhcpd6.conf".format(test_constants.
                                              DHCPD_CONF_DIR)
        # dhcpd.pools path
        dhcpd_pools = "{0}/dhcpd6.pools".format(test_constants.
                                                DHCPD_CONF_DIR)
        # dhcpd6 path
        dhcpd_sysconf = "{0}/dhcpd6".format(test_constants.
                                            DHCPD_DHCPDARGS_FILE)

        for pos, node_url in enumerate(node_urls):

            self.log("info", "VERIFYING NODE {0}".format(node_url))
            node_fname = self.get_node_filename_from_url(self.ms_node,
                                                         node_url)
            check_files_existence = \
                self.check_existents_of_the_confs(node_fname, dhcpd_conf,
                                                  dhcpd_pools, dhcpd_sysconf)
            errors.extend(check_files_existence)
            # CHECK dhcpd.conf FILE CONTENT NODES
            if pos == 0:
                role = '255'  # primary
                node_ifs = node1_ifs
            else:
                role = '0'  # secondary
                node_ifs = node2_ifs

            check_dhcpd_conf = self.check_dhcpd_conf_content(node_fname,
                                                             dhcpd_conf,
                                                             role)
            errors.extend(check_dhcpd_conf)
            # CHECK /etc/sysconfig/dhcpd6 FILE CONTENT NODES

            check_sysconf_dhcpd = self. \
                check_sysconf_dhcpd_content(node_fname,
                                            node_ifs, dhcpd_sysconf)
            errors.extend(check_sysconf_dhcpd)
            # CHECK dhcpd.pools FILE CONTENT NODES
            std_out = self.get_file_contents(node_fname, dhcpd_pools,
                                             su_root=True)
            check_subnet_conf = \
                self.check_pools_conf_subnet(std_out, dhcp_subnet)
            errors.extend(check_subnet_conf)

            check_ranges_conf = \
                self.check_pools_conf_ranges(std_out, ranges)
            errors.extend(check_ranges_conf)

        return errors

    def _add_service(self, dhcp_infra_path, srv_name):
        '''
        Description:
            Add DHCP service to deployment
        Args:
            dhcp_infra_path (string): Path to DHCP service under software
            srv_name (string): Name to give DHCP service
        Results:
            None
        '''
        self.execute_cli_create_cmd(
            self.ms_node,
            dhcp_infra_path,
            'dhcp6-service',
            'service_name=' + srv_name
            )

    def _add_subnet(self, dhcp_infra_path, subnet_id, network_name):
        '''
        Description:
            Add subnet to DHCP service
        Args:
            dhcp_infra_path (string): Path to DHCP service under software
            subnet_id (string): Subnet name to use in vpath
            network_name (string): Name of network to associate with subnet
        Results:
            None
        '''
        self.execute_cli_create_cmd(
            self.ms_node,
            dhcp_infra_path + '/subnets/' + subnet_id,
            'dhcp6-subnet',
            'network_name=' + network_name
            )

    def _add_ranges(self, dhcp_infra_path, subnet, list_ranges, offset):
        '''
        Description:
            Add range6 to DHCP subnet
        Args:
            dhcp_infra_path (string):  Path to DHCP service under software
            subnet (string): Name of subnet to attach range to
            list_ranges (list): List of tuples, each giving start & end ip
            offset (integer): Start number to use when naming ranges
        Results:
            None
        '''
        for idx, item in enumerate(list_ranges):
            range_start, range_end = item
            self.execute_cli_create_cmd(
                self.ms_node,
                '{0}/subnets/{1}/ranges/r{2}'.format(
                    dhcp_infra_path, subnet, offset + idx
                    ),
                'dhcp6-range',
                'start={0} end={1}'.format(range_start, range_end)
                )

    def _add_inherit(self, dhcp_infra_path, node_url, srv_name, params):
        '''
        Description:
            Make node inherit DHCP service
        Args:
            dhcp_infra_path (string): Path to DHCP service to inherit
            node_url (string): URL of node that will inherit service
            srv_name (string): Name (in vpath) of DHCP service to inherit
            params (string): Extra parameters (i.e. primary=true/false)
        Results:
            None
        '''
        self.execute_cli_inherit_cmd(
            self.ms_node,
            node_url + '/services/' + srv_name,
            dhcp_infra_path,
            params
            )

    def _remove_inherit(self, node_url, srv_name):
        '''
        Description:
            Remove DHCP service from node
        Args:
            node_url (string): URL of node that will disinherit service
            srv_name (string): Name (in vpath) of DHCPO service to disinherit
        Results:
            None
        '''
        self.execute_cli_remove_cmd(
            self.ms_node,
            node_url + '/services/' + srv_name
            )

    def _create_and_run_plan(self, timeout_delay=12):
        '''
        Description:
            Create and run plan
        Args:
            timeout_delay (integer): Runplan timeout, in minutes
        Results:
            None
        '''
        self.execute_cli_createplan_cmd(self.ms_node, expect_positive=True)
        self.execute_cli_runplan_cmd(self.ms_node, expect_positive=True)
        self.assertTrue(
            self.wait_for_plan_state(
                self.ms_node, test_constants.PLAN_TASKS_SUCCESS,
                timeout_mins=timeout_delay
            )
        )

    @attr('all', 'revert', 'story8126', 'story8126_tc03')
    def test_03_p_configure_extend_remove_full_dhcp_v6_service(self):
        """
        @tms_id: story8126_tc03
        @tms_requirements_id: LITPCDS-8126
        @tms_title: Create dhcpv6 service, subnet, and range then remove
        service.
        @tms_description:  This test creates a model with a dhcp v6 service,
        a single dhcp-subnet and a single dhcp-range. It then adds a new
        subnet with three ranges to the service. Finally it removes the dhcp
        v6 service completely_
        @tms_test_steps:
            @step: Create a dhcp v6 service
            @result: dhcp v6 service created
            @step: Create a dhcp-subnet item that doesnt belong a
            mgmt-interface
            @result: dhcp-subnet item created
            @step:  Assign a single dhcp-range item to the dhcp-subnet item
            @result: dhcp-range item successfully assigned to previously
            created dhcp-service item
            @step: Deploy the dhcp v6 service on the peer nodes, as primary
            on node1 and as non-primary node2.
            @result: dhcp v6 service deployed successfully on node1 as
            primary, and node 2 and non-primary
            @step: Create and run plan.
            @result: Plan created and run successfully
            @step: Check config of applied plan
            @result: Config of applied plan confirmed to match expected values
            @step: Add a new subnet with three ranges to the applied dhcp
            v6 service.
            @result: New subnet with 3 specified ranges applied to existing
            dhcp v6 service
            @step: Run plan and check that the new ranges and subnet are
            configured.
            @result: Plan run successfully and verified to be configured as
            expected
            @step: Remove the full dhcp v6 service
            @result: dhcp v6 service removed
            @step: Run plan and check that it has been de-configured correctly
            @result: Plan run successfully and verified to have been
            de-configured
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """

        # Setup some nodes
        node_urls = self.find(self.ms_node, "/deployments", "node")
        node_urls.sort()
        self.create_two_networks_two_interfaces()

        dhcp_infra_path = '/software/services/dhcp'
        ipv6_ranges = [
            (self.ipv6_prefixes[0] + '::10', self.ipv6_prefixes[0] + '::20')
            ]
        more_ipv6_ranges = [
            (self.ipv6_prefixes[1] + '::10', self.ipv6_prefixes[1] + '::20'),
            (self.ipv6_prefixes[1] + '::21', self.ipv6_prefixes[1] + '::24'),
            (self.ipv6_prefixes[1] + '::26', self.ipv6_prefixes[1] + '::30')
            ]

        # 1. Create a dhcp v6 service, a dhcp-subnet(not belonging to a
        #    mgmt-interface) and specify a single dhcp-range.
        # 2. Deploy the dhcp v6 service on two peer nodes, as the primary
        #    on nodeX and as the secondary nodeY.

        dhcp_service_name = 'dhcp_srv'
        subnet1_name = 'sub1'
        subnet2_name = 'sub2'
        inherit_name = 'dhcp_srv'

        self._add_service(dhcp_infra_path, dhcp_service_name)
        self._add_subnet(dhcp_infra_path, subnet1_name, self.ipv6_networks[0])
        self._add_ranges(dhcp_infra_path, subnet1_name, ipv6_ranges, 1)
        self._add_inherit(
            dhcp_infra_path, node_urls[0], inherit_name, 'primary=true')
        self._add_inherit(
            dhcp_infra_path, node_urls[1], inherit_name, 'primary=false')

        # 3. Run a plan and check config.

        self._create_and_run_plan()

        # Check configs
        std_err = self.data_driven_verification(
            node_urls,
            [self.nics_node1[0]],
            [self.nics_node2[0]],
            [[self.ipv6_prefixes[0] + '::' + self.ipv6_masks[0]]],
            ipv6_ranges
            )
        self.assertEqual([], std_err)

        # 4. Add a new subnet and with three ranges to the applied dhcp
        #    v6 service.

        self._add_subnet(dhcp_infra_path, subnet2_name, self.ipv6_networks[1])
        self._add_ranges(dhcp_infra_path, subnet2_name, more_ipv6_ranges, 1)

        # 5. Run plan and check that the new ranges and subnet are
        #   configured.

        self._create_and_run_plan()

        # Check configs
        std_err = self.data_driven_verification(
            node_urls,
            self.nics_node1,
            self.nics_node2,
            [[self.ipv6_prefixes[0] + '::' + self.ipv6_masks[0]],
             [self.ipv6_prefixes[1] + '::' + self.ipv6_masks[1]]],
            ipv6_ranges + more_ipv6_ranges
            )
        self.assertEqual([], std_err)

        # 6. Remove the full dhcp v6 service

        self._remove_inherit(node_urls[0], inherit_name)
        self._remove_inherit(node_urls[1], inherit_name)
        self.execute_cli_remove_cmd(self.ms_node, dhcp_infra_path)

        # 7. Run plan and check that it has been deconfigured correctly

        self._create_and_run_plan()

        node1_fname = self.get_node_filename_from_url(
            self.ms_node, node_urls[0]
            )
        node2_fname = self.get_node_filename_from_url(
            self.ms_node, node_urls[1]
            )

        # Check dhcpd process per NODE to be not active
        cmd = "/bin/ps aux | /bin/grep 'd[h]cpd -6'"
        _, _, rc = self.run_command(node1_fname, cmd, su_root=True)
        self.assertEqual(1, rc)
        _, _, rc = self.run_command(node2_fname, cmd, su_root=True)
        self.assertEqual(1, rc)

        # Check dhcpd process auto-start per NODE to be not active
        cmd = "/sbin/chkconfig | /bin/grep dhcpd6"
        stdout, _, _ = self.run_command(node1_fname, cmd, su_root=True)
        self.assertFalse(self.count_text_in_list("on", stdout))
        stdout, _, _ = self.run_command(node2_fname, cmd, su_root=True)
        self.assertFalse(self.count_text_in_list("on", stdout))

    @attr('all', 'revert', 'story8126', 'story8126_tc05')
    def test_05_p_create_update_full_dhcp_v6_service(self):
        """
        @tms_id: story8126_tc05
        @tms_requirements_id: LITPCDS-8126
        @tms_title: Create dhcpv6 service with multiple subnets and ranges
        then update the subnets and ranges
        @tms_description: This test creates a model with a dhcp v6 service,
        multiple subnets, and multiple ranges. It then updates all the
        properties of a service, range and subnet.(including primary/secondary
        values)
        @tms_test_steps:
            @step: Create a dhcp v6 service
            @result: shcp v6 sewrvice created
            @step: Create a dhcp-subnet item that doesn not belong a
            mgmt-interface
            @result: dhcp-subnet item created
            @step:  Assign multiple dhcp-range items to the dhcp-subnet item
            @result: multiple dhcp-range item successfully assigned to
            previously created dhcp-service item
            @step: Deploy the dhcp v6 service on the peer nodes, as primary
            on node1 and as non-primary node2.
            @result: dhcp v6 service deployed successfully on node1 as
            primary, and node 2 and non-primary
            @step: Create and run plan.
            @result: Plan created and run successfully
            @step: Check config of applied plan
            @result: Config of applied plan confirmed to match expected values
            @step: Update the service_name property of the dhcp v6 service
            @result: service_name property of the dhcp v6 service updated to
            new value
            @step: Update the network_name property of the dhcp-subnet
            (using a valid network)
            @result:network_name property of the dhcp-subnet updated
            successfully
            @step: Update the start and end properties of a dhcp-range
            (extending the range)
            @result: start and end properties are successfully updated to
            the new values
            @step: Update the start and end properties of a dhcp-range
            (Decreasing the range)
            @result: start and end properties are successfully updated to
            the new values
            @step: Add a new range in the same plan as an existing range is
            updated(Test for LITPCDS-9041)
            @result: New range is successfully added to plan
            @step: Update the primary service on node1 to become the
            secondary service.
            @result: Property primary on node1 dhcp-service successfully
            updated to false
            @step: Update the secondary service on node2 to become the
            primary service.
            @result: Property primary on node2 dhcp-service successfully
            updated to true
            @step: Create and run plan, then check all of the configuration
            updates are successful.
            @result: Plan confirmed to have run successfully
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """

        self.create_two_networks_two_interfaces()

        nodes = []

        base_url = "/software/services"
        service_props = "service_name=dhcp_8126"
        service_url = base_url + "/s8126"
        subnet_props = "network_name=test1"
        subnet2_props = "network_name=test2"
        subnet_url = service_url + "/subnets/s8126"
        subnet2_url = service_url + "/subnets/s8127"
        # intial ranges
        ranges = [['2001:2200:82a1:0103:3456:1234:aaaa:aaa2',
                   '2001:2200:82a1:0103:3456:1234:aabb:aaa2'],
                  ['2001:2200:82a1:0103:3456:1234:abaa:aaa2',
                   '2001:2200:82a1:0103:3456:1234:acbb:aaa2'],
                  ['2001:2200:82a1:0103:3456:1234:acbb:aaa3',
                   '2001:2200:82a1:0103:3456:1234:bcbb:aaa2'],
                  ['2001:5500:82a1:0103:4355:3267:4355:3466',
                   '2001:5500:82a1:0103:4355:3267:5555:3466']]

        range1_start = ranges[0][0]
        range1_end = ranges[0][1]
        range1_props = "start={0} end={1}".format(range1_start, range1_end)
        range1_url = subnet_url + "/ranges/r1"

        range2_start = ranges[1][0]
        range2_end = ranges[1][1]
        range2_props = "start={0} end={1}".format(range2_start, range2_end)
        range2_url = subnet_url + "/ranges/r2"

        range3_start = ranges[2][0]
        range3_end = ranges[2][1]
        range3_props = "start={0} end={1}".format(range3_start, range3_end)
        range3_url = subnet_url + "/ranges/r3"

        range4_start = ranges[3][0]
        range4_end = ranges[3][1]
        range4_props = "start={0} end={1}".format(range4_start, range4_end)
        range4_url = subnet2_url + "/ranges/r4"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp6-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp6-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, subnet2_url,
                                    "dhcp6-subnet", subnet2_props)

        self.execute_cli_create_cmd(self.ms_node, range1_url,
                                    "dhcp6-range", range1_props)

        self.execute_cli_create_cmd(self.ms_node, range2_url,
                                    "dhcp6-range", range2_props)

        self.execute_cli_create_cmd(self.ms_node, range3_url,
                                    "dhcp6-range", range3_props)

        self.execute_cli_create_cmd(self.ms_node, range4_url,
                                    "dhcp6-range", range4_props)

        node_urls = self.find(self.ms_node, "/deployments", "node")

        for node in node_urls:
            nodes.append(self.get_node_filename_from_url(self.ms_node,
                                                         node))
        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s8126"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url)

        node2_dhcp_url = node_urls[1] + "/services/s8126"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node2_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        # create plan
        self.execute_cli_createplan_cmd(self.ms_node)
        # run plan
        self.execute_cli_runplan_cmd(self.ms_node)
        self.assertTrue(self.wait_for_plan_state(self.ms_node,
                                                 test_constants.PLAN_COMPLETE))

        # used dhcp subnet
        dhcp_subnet = [['2001:2200:82a1:103::/64'],
                       ['2001:5500:82a1:103:4355:3267::/96']]

        std_err = self.data_driven_verification(node_urls,
                                                self.nics_node1,
                                                self.nics_node2,
                                                dhcp_subnet,
                                                ranges)

        self.assertEqual([], std_err)

        # Update the network_name property of the dhcp-subnet
        # Create a new network
        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]
        # CREATE TEST NETWORK 3
        network_url = networks_path + "/test_network6550"
        props = "name='test3'"
        self.execute_cli_create_cmd(self.ms_node, network_url,
                                    "network", props)

        # Update the network_name
        subnet2_props = "network_name=test3"
        self.execute_cli_update_cmd(self.ms_node, subnet2_url, subnet2_props)

        # only third range remain inchanged
        ranges[0] = ['2001:2200:82a1:0103:3456:1234:aaaa:aaa0',
                     '2001:2200:82a1:0103:3456:1234:aaab:aaa2']
        ranges[1] = ['2001:2200:82a1:0103:3456:1234:abaa:aaa2',
                     '2001:2200:82a1:0103:3456:1234:abbb:aaa2']
        ranges[3] = ['2002:5500:82a1:0103:4355:3267:5555:3499',
                     '2002:5500:82a1:0103:4355:3267:5555:3599']

        # Update the range ips
        range4_start = ranges[3][0]
        range4_end = ranges[3][1]
        range4_props = "start={0} end={1}".format(range4_start, range4_end)
        self.execute_cli_update_cmd(self.ms_node, range4_url, range4_props)

        # update any interfaces using that network
        # node1 eth
        if1_url = node_urls[0] + "/network_interfaces/if_8127"
        if1_props = "ipv6address=2002:5500:82a1:0103:4355:3267:5555:3466/99" \
                    " network_name=test3"
        self.execute_cli_update_cmd(self.ms_node, if1_url, if1_props)
        # node2 eth
        if2_url = node_urls[1] + "/network_interfaces/if_8127"
        if2_props = "ipv6address=2002:5500:82a1:0103:4355:3267:5555:3467/99" \
                    " network_name=test3"
        self.execute_cli_update_cmd(self.ms_node, if2_url, if2_props)

        # update the service_name of the service
        update_props = "service_name=dhcp_update"
        self.execute_cli_update_cmd(self.ms_node, service_url, update_props)

        # decrease range1 and increase range2
        range1_start = ranges[0][0]
        range1_end = ranges[0][1]
        range1_props = "start={0} end={1}".format(range1_start, range1_end)
        self.execute_cli_update_cmd(self.ms_node, range1_url, range1_props)

        range2_start = ranges[1][0]
        range2_end = ranges[1][1]
        range2_props = "start={0} end={1}".format(range2_start, range2_end)
        self.execute_cli_update_cmd(self.ms_node, range2_url, range2_props)

        #Add a new range in the same plan as an existing range is updated
        range5_start = "2001:2200:82a1:0103:3456:1234:aabb:aaa7"
        range5_end = "2001:2200:82a1:0103:3456:1234:aabb:aaa9"
        range5_props = "start={0} end={1}".format(range5_start, range5_end)
        range5_url = subnet_url + "/ranges/r5"

        self.execute_cli_create_cmd(self.ms_node, range5_url,
                                    "dhcp6-range", range5_props)

        # update the primary service to no-primary and vice-versa
        props = "primary=false"
        self.execute_cli_update_cmd(self.ms_node, node1_dhcp_url, props)

        props = "primary=true"
        self.execute_cli_update_cmd(self.ms_node, node2_dhcp_url, props)

        # Setup further nics cleaning in teardown.
        self.interfaces_cleanup(nodes, self.nics_node1, self.nics_node2)

        # create plan
        self.execute_cli_createplan_cmd(self.ms_node)
        # run plan
        self.execute_cli_runplan_cmd(self.ms_node)
        self.assertTrue(self.wait_for_plan_state(self.ms_node,
                                                 test_constants.PLAN_COMPLETE))

        new_range = [range5_start, range5_end]
        ranges.append(new_range)

        # Check that dhcp service is configured correctly
        dhcp_subnet[1] = ['2002:5500:82a1:103:4355:3267:4000:0/99']

        # The roles are reversed and checked urls are updated.
        new_roles_nodes_urls = [node_urls[1], node_urls[0]]

        std_err = self.data_driven_verification(new_roles_nodes_urls,
                                                self.nics_node1,
                                                self.nics_node2,
                                                dhcp_subnet,
                                                ranges)

        self.assertEqual([], std_err)

    @attr('all', 'revert', 'story8126', 'story8126_tc33')
    def test_33_p_update_network_and_range_dhcp_v6_service(self):
        """
        @tms_id: litpcds_8126_tc33
        @tms_requirements_id: LITPCDS-8126
        @tms_title: Create dhcp v6 service, subnet, and range, then update
        networks adapter settings and properties
        @tms_description: This test creates a model with a dhcp v6 service,
        one subnet, and range. It then updates network adapters settings and
        properties of a service, network name and range.
        This test verifies LITPCDS-8866
        @tms_test_steps:
            @step: Create a dhcp v6 service
            @result: dhcp v6 service created successfully
            @step: Specify an IP range for dhcp v6 service
            @result: IP range item successfully added to dhcp v6 service
            @step:  Deploy the dhcp v6 service on two peer nodes, as the
            primary on node1 and as the secondary on node2.
            @result: dhcp v6 service successfully deployed on node1 as primary,
            and as secondary on node2
            @step: Update the network_name property
            @result: network_name property successfully updated
            @step: Update the IPv6 addresses on the involved network adapters.
            @result: Addresses successfully updated
            @step: Update the network_name property of the dhcp-subnet
            according to the new network settings.
            @result: network_name property successfully updated
            @step: Update the start and end properties of a dhcp-range
            according to the new network settings.
            @result: start and end properties are successfully updated to
            the new values
            @step: Run plan and check that all of the updates are successful.
            @result: Plan run successfully and all properties conlfirmed to
            have been updated
        @tms_test_precondition: NA
        @tms_execution_type: Automated

        """

        self.create_network_and_interfaces()

        nodes = []

        base_url = "/software/services"
        service_props = "service_name=dhcp_8126"
        service_url = base_url + "/s8126"
        subnet_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s8126"
        ipv6_1 = "2002:5500:82a1:0103:4355:3267:5555:3466/99"
        ipv6_2 = "2002:5500:82a1:0103:4355:3267:5555:3467/99"
        network3_name = "test3"

        # intial ranges
        ranges = [['2001:2200:82a1:0103:3456:1234:aaaa:aaa2',
                   '2001:2200:82a1:0103:3456:1234:aabb:aaa2']]

        range_start = ranges[0][0]
        range_end = ranges[0][1]
        range_props = "start={0} end={1}".format(range_start, range_end)
        range_url = subnet_url + "/ranges/r1"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp6-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp6-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range_url,
                                    "dhcp6-range", range_props)

        node_urls = self.find(self.ms_node, "/deployments", "node")

        for node in node_urls:
            nodes.append(self.get_node_filename_from_url(self.ms_node,
                                                         node))
        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s8126"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url)

        node2_dhcp_url = node_urls[1] + "/services/s8126"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node2_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        # Update the network_name property of the dhcp-subnet
        # Create a new network
        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]
        # CREATE TEST NETWORK 3
        network_url = networks_path + "/test_network8126"
        props = "name='{0}'".format(network3_name)
        self.execute_cli_update_cmd(self.ms_node, network_url, props)

        # Update the network_name
        subnet_props = "network_name={0}".format(network3_name)
        self.execute_cli_update_cmd(self.ms_node, subnet_url, subnet_props)

        # only third range remain unchanged
        ranges = [['2002:5500:82a1:0103:4355:3267:5555:3499',
                   '2002:5500:82a1:0103:4355:3267:5555:3599']]

        # Update the range ips
        range_start = ranges[0][0]
        range_end = ranges[0][1]
        range_props = "start={0} end={1}".format(range_start, range_end)
        self.execute_cli_update_cmd(self.ms_node, range_url, range_props)

        # update any interfaces using that network
        # node1 eth
        if1_url = node_urls[0] + "/network_interfaces/if_8126"
        if1_props = "ipv6address={0}" \
                    " network_name={1}".format(ipv6_1, network3_name)
        self.execute_cli_update_cmd(self.ms_node, if1_url, if1_props)
        # node2 eth
        if2_url = node_urls[1] + "/network_interfaces/if_8126"
        if2_props = "ipv6address={0}" \
                    " network_name={1}".format(ipv6_2, network3_name)
        self.execute_cli_update_cmd(self.ms_node, if2_url, if2_props)

        # Setup further nics cleaning in teardown.
        self.interfaces_cleanup(nodes, self.nics_node1, self.nics_node2)

        _, std_err, _ = self.execute_cli_createplan_cmd(self.ms_node)
        self.assertEquals([], std_err)
        self.execute_cli_showplan_cmd(self.ms_node)

        for node in node_urls:
            nodes.append(self.get_node_filename_from_url(self.ms_node, node))

        node1_hostname = self.get_node_att(nodes[0], 'hostname')
        node2_hostname = self.get_node_att(nodes[1], 'hostname')

        phase_3_2 = 'Configure "dhcp6-subnet" on '\
            'network "test3" on node "{0}"'.\
            format(node2_hostname)

        self.assertEqual(PLAN_TASKS_INITIAL,
                         self.get_task_state(self.ms_node,
                                             phase_3_2,
                                             False))

        phase_7_2 = 'Configure "dhcp6-subnet" on '\
            'network "test3" on node "{0}"'.\
            format(node1_hostname)

        self.assertEqual(PLAN_TASKS_INITIAL,
                         self.get_task_state(self.ms_node,
                                             phase_7_2,
                                             False))

    @attr('all', 'revert', 'story8126', 'story8126_tc06')
    def test_06_n_create_dhcp_v6_service_without_dhcp_subnet(self):
        """
        @tms_id: litpcds_8126_tc06
        @tms_requirements_id: LITPCDS-8126
        @tms_title: Assert dhcp v6 service with no dhcp-subnet item throws
        Validation Error
        @tms_description:  Create a dhcp v6 service that does not have a
        dhcp-subnet and check for a Validation error at create plan.
        @tms_test_steps:
            @step: Create a dhcp6server and inherit this to node1 as primary
            and node2 as non-primary
            @result: Items created
            @step: Create plan and ensure errors are raised.
            @result: Errors raised CardinalityError
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """

        nodes = []

        base_url = "/software/services"
        service_props = "service_name=dhcp_8126"
        service_url = base_url + "/s8126"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp6-service", service_props)

        node_urls = self.find(self.ms_node, "/deployments", "node")

        for node in node_urls:
            nodes.append(self.get_node_filename_from_url(self.ms_node,
                                                         node))
        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s8126"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url)

        node2_dhcp_url = node_urls[1] + "/services/s8126"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node2_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        # create plan
        _, err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                    expect_positive=False)

        # check for error msgs

        err1 = "CardinalityError    Create plan failed: "
        err2 = 'This collection requires a minimum of 1 ' + \
            'items not marked for removal'

        self.assertTrue(self.is_text_in_list(err1, err))
        self.assertTrue(self.is_text_in_list(err2, err))
        self.assertEqual(3, self.count_text_in_list(err1, err))
        self.assertEqual(3, self.count_text_in_list(err2, err))

    @attr('all', 'revert', 'story8126', 'story8126_tc07')
    def test_07_n_create_dhcp_v6_subnet_without_dhcp_range(self):
        """
        @tms_id: litpcds_8126_tc07
        @tms_requirements_id: LITPCDS-8126
        @tms_title: Assert dhcp v6 service with no dhcp-range item throws
        Validation Error
        @tms_description: Create a dhcp-subnet that does not have a dhcp-range
        and check for a Validation error at create plan.
        @tms_test_steps:
            @step: Create a network
            @result: Item created.
            @step: Create a dhcp6service and a dhcp6 subnet
            @result: Items created
            @step: Inherit the dhcp6service to node1 as primary and node2
            as non-primary
            @result: dhcp6service successfully inherited to node1 as primary
            and node2 as non-primary
            @step: Create plan and ensure errors are raised.
            @result: Errors raised CardinalityError
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """

        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]
        # CREATE TEST NETWORK 1
        network_url = networks_path + "/test_network8126"
        props = "name='test1'"
        self.execute_cli_create_cmd(self.ms_node, network_url,
                                    "network", props)

        base_url = "/software/services"

        service_props = "service_name=dhcp_s8126"
        service_url = base_url + "/s8126"
        subnet_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s8126"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp6-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp6-subnet", subnet_props)

        node_urls = self.find(self.ms_node, "/deployments", "node")
        node1_dhcp_url = node_urls[0] + "/services/s8126"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url)

        node2_dhcp_url = node_urls[1] + "/services/s8126"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node2_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        # Create plan
        _, err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                    expect_positive=False)

        # check for error msgs

        err1 = "CardinalityError    Create plan failed: "
        err2 = 'This collection requires a minimum of 1 ' + \
            'items not marked for removal'

        self.assertTrue(self.is_text_in_list(err1, err))
        self.assertTrue(self.is_text_in_list(err2, err))
        self.assertEqual(3, self.count_text_in_list(err1, err))
        self.assertEqual(3, self.count_text_in_list(err2, err))

    @attr('all', 'revert', 'story8126', 'story8126_tc08')
    def test_08_n_create_dhcp_v6_service_range_outside_the_prefix(self):
        """
        @tms_id: litpcds_8126_tc08
        @tms_requirements_id: LITPCDS-8126
        @tms_title: Assert dhcp v6 service with incorrect start and end
        properties throws a Validation Error
        @tms_description:  Create a dhcp v6 service and ranges with addresses
        outside the dhcpv6 adapter IPv6 prefix given for the start and end
        properties, and check for a ValidationError.
        @tms_test_steps:
            @step: Create a network and interfaces on node1 and node2
            @result: Items created.
            @step: Create a dhcp6service, a dhcp6 subnet and a dhcp6 range
            @result: Items created
            @step: Inherit the dhcp6service to node1 as primary and node2
            as non-primary
            @result: dhcp6service successfully inherited to node1 as primary
            and node2 as non-primary
            @step: Create plan and ensure errors are raised.
            @result: Errors raised ValidationError CardinalityError
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """

        self.create_network_and_interfaces()

        free_nics_node1 = []
        free_nics_node2 = []
        node_urls = self.find(self.ms_node, "/deployments", "node")
        node_urls.sort()
        free_nics = \
            self.verify_backup_free_nics(self.ms_node, node_urls[0])
        self.test_node_if1 = free_nics[0]
        free_nics_node1.extend(self.test_node_if1)
        free_nics = \
            self.verify_backup_free_nics(self.ms_node, node_urls[1])
        self.test_node2_if1 = free_nics[0]
        free_nics_node2.extend(self.test_node2_if1)

        # create dhcp service
        base_url = "/software/services"
        service_props = "service_name=dhcp_8126"
        service_url = base_url + "/s8126"
        subnet_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s8126"
        range_start = "2005:2200:82a1:0103:3456:1234:aaaa:aaa0"
        range_end = "2005:2200:82a1:0103:3456:1234:aaab:aaa2"
        range_props = "start={0} end={1}".format(range_start, range_end)
        range_url = subnet_url + "/ranges/r1"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp6-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp6-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range_url,
                                    "dhcp6-range", range_props)

        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s8126"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url)

        node2_dhcp_url = node_urls[1] + "/services/s8126"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node2_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        # Create plan
        _, err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                    expect_positive=False)

        # check for error msgs

        err1 = "ValidationError    Create plan failed: "
        err2 = '"start" address "{0}" is not valid for network "test1"'.\
            format(range_start)
        err3 = '"end" address "{0}" is not valid for network "test1"'.\
            format(range_end)

        self.assertTrue(self.is_text_in_list(err1, err))
        self.assertTrue(self.is_text_in_list(err2, err))
        self.assertTrue(self.is_text_in_list(err3, err))
        self.assertEqual(4, self.count_text_in_list(err1, err))
        self.assertEqual(2, self.count_text_in_list(err2, err))
        self.assertEqual(2, self.count_text_in_list(err2, err))

    @attr('all', 'revert', 'story8126', 'story8126_tc32')
    def test_32_n_deploy_dhcp_v6_service_on_ms(self):
        """
        @tms_id: litpcds_8126_tc32
        @tms_requirements_id: LITPCDS-8126
        @tms_title: Assert deploying dhcp v6 service on MS throws
        Validation Error
        @tms_description:  Deploy a dhcp v6 service on the MS and check for a
        Validation error.
        @tms_test_steps:
            @step: Create a network and interface on the MS
            @result: Items created.
            @step: Create a dhcp6service on te MS
            @result: Item created
            @step: Create plan and ensure errors are raised.
            @result: Errors raised ValidationError CardinalityError
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """

        network_name = "test11"

        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]
        # CREATE TEST NETWORK 1
        network_url = networks_path + "/test_network81265"
        props = "name='{0}'".format(network_name)
        self.execute_cli_create_cmd(self.ms_node, network_url,
                                    "network", props)

        free_nics = \
            self.verify_backup_free_nics(self.ms_node, "/ms")

        self.test_ms_if1 = free_nics[0]

        ms_url = "/ms/network_interfaces/if_81255"

        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='{2}' \
                    ipv6address='2001:2200:82a1:0103::2/64'".\
                    format(self.test_ms_if1["MAC"],
                           self.test_ms_if1["NAME"],
                           network_name)

        self.execute_cli_create_cmd(self.ms_node, ms_url, "eth", eth_props)

        service_props = "service_name=dhcp_81265"
        ms_dhcp_url = "/ms/services/s81265"
        self.execute_cli_create_cmd(
            self.ms_node, ms_dhcp_url,
            "dhcp6-service", service_props
            )

        # Verify error
        _, std_err, _ = self.execute_cli_createplan_cmd(
            self.ms_node, expect_positive=False
            )
        self.assertTrue(self.is_text_in_list(
            'DHCP services may not be deployed'\
            ' on the Management Server "ms1"', std_err
            ))

    @attr('all', 'revert', 'story8126', 'story8126_tc11')
    def test_11_n_deploy_dhcp_v6_service_inherit_on_ms(self):
        """
        @tms_id: litpcds_8126_tc11
        @tms_requirements_id: LITPCDS-8126
        @tms_title: Assert deploying dhcp v6 service on MS, and inheriting it
        throws Validation Error
        @tms_description:  Deploy a dhcp v6 service on the MS inherit it and
        check for a Validation error at create plan.
        @tms_test_steps:
            @step: Create a network and interface on the MS
            @result: Items created.
            @step: Create a dhcp6service under /software with subnet and range
            @result: Item created
            @step: Inherit the dhcp6 service to MS and ensure Error
            ChildNotAllowedError
            @result: Message thrown ChildNotAllowedError
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """

        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]
        # CREATE TEST NETWORK 1
        network_url = networks_path + "/test_network8126"
        props = "name='test1'"
        self.execute_cli_create_cmd(self.ms_node, network_url,
                                    "network", props)

        free_nics = \
            self.verify_backup_free_nics(self.ms_node, "/ms")

        self.test_ms_if1 = free_nics[0]

        ms_url = "/ms/network_interfaces/if_8126"

        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='test1' \
                    ipv6address='2001:2200:82a1:0103::2/64'".\
                    format(self.test_ms_if1["MAC"],
                           self.test_ms_if1["NAME"])

        self.execute_cli_create_cmd(self.ms_node, ms_url, "eth", eth_props)

        base_url = "/software/services"
        service_props = "service_name=dhcp_8126"
        service_url = base_url + "/s8126"
        subnet_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s8126"
        ms_dhcp_url = "/ms/services/s8126"

        range1_start = "2001:2200:82a1:0103:3456:1234:aaaa:aaa2"
        range1_end = "2001:2200:82a1:0103:3456:1234:aabb:aaa2"
        range1_props = "start={0} end={1}".format(range1_start, range1_end)
        range1_url = subnet_url + "/ranges/r1"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp6-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp6-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range1_url,
                                    "dhcp6-range", range1_props)

        _, std_err, _ = self.execute_cli_inherit_cmd(self.ms_node,
                                                     ms_dhcp_url, service_url,
                                                     expect_positive=False)

        # check for error msgs

        self.assertTrue(self.is_text_in_list("ChildNotAllowedError", std_err))
        self.assertTrue(self.is_text_in_list("'s8126' must not be an" +
                                             " inherited item", std_err))

    @attr('all', 'revert', 'story8126', 'story8126_tc12')
    def test_12_n_create_dhcp_v6_subnet_mgmt_network(self):
        """
        @tms_id: litpcds_8126_tc12
        @tms_requirements_id: LITPCDS-8126
        @tms_title: Check dhcp-subnet not allowed on mgmt network
        @tms_description:  Create a dhcp-subnet on the mgmt network and check
        for a Validation error at create plan
        @tms_test_steps:
            @step: Create a dhcp6-service to node1 as primary and node2 as
            non-primary
            @result: Items created.
            @step: Inherit service to both nodes
            @result: Service inherited to both nodes
            @step: Create a plan and ensure error messages raised.
            @result: Message throws ValidationError
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """

        nodes = []
        mgmt_name = self.get_management_network_name(self.ms_node)
        base_url = "/software/services"
        service_props = "service_name=dhcp_8126"
        service_url = base_url + "/s8126"
        subnet_props = "network_name={0}".format(mgmt_name)
        subnet_url = service_url + "/subnets/s8126"

        range1_start = "2001:2200:82a1:0103:3456:1234:aaaa:aaa2"
        range1_end = "2001:2200:82a1:0103:3456:1234:aabb:aaa2"
        range1_props = "start={0} end={1}".format(range1_start, range1_end)
        range1_url = subnet_url + "/ranges/r1"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp6-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp6-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range1_url,
                                    "dhcp6-range", range1_props)

        node_urls = self.find(self.ms_node, "/deployments", "node")

        for node in node_urls:
            nodes.append(self.get_node_filename_from_url(self.ms_node, node))
        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s8126"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url)

        node2_dhcp_url = node_urls[1] + "/services/s8126"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node2_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        # Create plan
        _, err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                    expect_positive=False)

        # check for error msgs

        err1 = "ValidationError    Create plan failed: "
        err2 = '"dhcp6-subnet" must not reference the ' + \
            'management network "mgmt"'
        err3 = '"start" address "{0}" is not valid for network "mgmt"'.\
            format(range1_start)

        err4 = '"end" address "{0}" is not valid for network "mgmt"'.\
            format(range1_end)

        self.assertTrue(self.is_text_in_list(err1, err))
        self.assertTrue(self.is_text_in_list(err2, err))
        self.assertTrue(self.is_text_in_list(err3, err))
        self.assertTrue(self.is_text_in_list(err4, err))
        self.assertEqual(6, self.count_text_in_list(err1, err))
        self.assertEqual(2, self.count_text_in_list(err2, err))
        self.assertEqual(2, self.count_text_in_list(err3, err))
        self.assertEqual(2, self.count_text_in_list(err4, err))

    @attr('all', 'revert', 'story8126', 'story8126_tc13')
    def test_13_n_create_dhcp_v6_subnet_no_network_interfaces(self):
        """
        @tms_id: litpcds_8126_tc13
        @tms_requirements_id: LITPCDS-8126
        @tms_title: Check a Validation error is thrown when a dhcp-subnet with
        a valid network_name is created, but the network has not been
        referenced by the interfaces
        @tms_description:  Create dhcp-subnet with a valid network_name=data
        where data is a valid network but has not been referenced by network
        interfaces on the node. Check for a Validation error at create plan.
        @tms_test_steps:
            @step: Create a network under infrastructure
            @result: Network created
            @step: Create interfaces on node1 and node2
            @result: Interfaces created under node1 and node 2
            @step: Create a non-defined network
            @result: non-defined network created
            @step: Create a dhcp6 service with subnet and range
            @result: Items created.
            @step: Inherit the service onto node1 as primary and onto node2
            as non-primary
            @result: Items inherited
            @step: Create plan and ensure errors are raised
            @result: ValidationErrors are raised
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """

        self.create_network_and_interfaces()
        nodes = []
        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]
        # CREATE TEST NETWORK 1
        network_url = networks_path + "/test_network_non_defined"
        props = "name='non_defined'"
        self.execute_cli_create_cmd(self.ms_node, network_url,
                                    "network", props)

        base_url = "/software/services"
        service_props = "service_name=dhcp_8126"
        service_url = base_url + "/s8126"
        subnet_props = "network_name=non_defined"
        subnet_url = service_url + "/subnets/s8126"

        range1_start = "2001:2200:82a1:0103:3456:1234:aaaa:aaa2"
        range1_end = "2001:2200:82a1:0103:3456:1234:aabb:aaa2"
        range1_props = "start={0} end={1}".format(range1_start, range1_end)
        range1_url = subnet_url + "/ranges/r1"
        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp6-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp6-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range1_url,
                                    "dhcp6-range", range1_props)

        node_urls = self.find(self.ms_node, "/deployments", "node")

        for node in node_urls:
            nodes.append(self.get_node_filename_from_url(self.ms_node,
                                                         node))
        # find nodes hostname
        node1_hostname = self.get_node_att(nodes[0], 'hostname')
        node2_hostname = self.get_node_att(nodes[1], 'hostname')

        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s8126"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url)

        node2_dhcp_url = node_urls[1] + "/services/s8126"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node2_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        # Create plan
        _, err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                    expect_positive=False)

        # check for error msgs

        err1 = "ValidationError    Create plan failed: "
        err2 = 'The network "non_defined" referenced by "dhcp6-subnet" ' \
            'is not configured on node "{0}"'.format(node1_hostname)

        err3 = 'The network "non_defined" referenced by "dhcp6-subnet" ' \
            'is not configured on node "{0}"'.format(node2_hostname)

        self.assertTrue(self.is_text_in_list(err1, err))
        self.assertTrue(self.is_text_in_list(err2, err))
        self.assertTrue(self.is_text_in_list(err3, err))
        self.assertEqual(2, self.count_text_in_list(err1, err))
        self.assertEqual(1, self.count_text_in_list(err2, err))
        self.assertEqual(1, self.count_text_in_list(err3, err))

    @attr('all', 'revert', 'story8126', 'story8126_tc14')
    def test_14_n_create_dhcp_v6_subnets_duplicate_networks(self):
        """
        @tms_id: litpcds_8126_tc14
        @tms_requirements_id: LITPCDS-8126
        @tms_title: Check a Validation error is thrown when subnet items have
        the same network name
        @tms_description:  Create more than one dhcp v6 subnet items, which
        have the same network name and check for a Validation error at create
        plan.
        @tms_test_steps:
            @step: Create a network under infrastructure
            @result: Item created.
            @step: Create interfaces on node1 and node2
            @result: Items created
            @step: Create a dhcp6 service with two subnets and one range under
            each subnet
            @result: Items created.
            @step: Inherit the service onto node1 as primary and onto node2 as
            non-primary
            @result: Items inherited
            @step: Create plan and ensure errors are raised
            @result: CardinalityError are raised
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """

        self.create_network_and_interfaces()
        base_url = "/software/services"
        service_props = "service_name=dhcp_8126"
        service_url = base_url + "/s8126"
        subnet_props = "network_name=test1"
        subnet2_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s8126"
        subnet2_url = service_url + "/subnets/s8127"

        range1_start = "2001:2200:82a1:0103:3456:1234:aaaa:aaa2"
        range1_end = "2001:2200:82a1:0103:3456:1234:aabb:aaa2"
        range1_props = "start={0} end={1}".format(range1_start, range1_end)
        range1_url = subnet_url + "/ranges/r1"

        range2_start = "2001:2200:82a1:0103:3456:1234:abaa:aaa2"
        range2_end = "2001:2200:82a1:0103:3456:1234:acbb:aaa2"
        range2_props = "start={0} end={1}".format(range2_start, range2_end)
        range2_url = subnet_url + "/ranges/r2"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp6-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp6-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, subnet2_url,
                                    "dhcp6-subnet", subnet2_props)

        self.execute_cli_create_cmd(self.ms_node, range1_url,
                                    "dhcp6-range", range1_props)

        self.execute_cli_create_cmd(self.ms_node, range2_url,
                                    "dhcp6-range", range2_props)
        node_urls = self.find(self.ms_node, "/deployments", "node")

        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s8126"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url)

        node2_dhcp_url = node_urls[1] + "/services/s8126"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node2_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        # Create plan
        _, err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                    expect_positive=False)
        # check for error msgs
        err1 = 'Network "test1" may be referenced by at most '\
               'one "dhcp-subnet" and at most one "dhcp6-subnet"'

        self.assertTrue(self.is_text_in_list(err1, err))

    @attr('all', 'revert', 'story8126', 'story8126_tc09')
    def test_09_n_create_dhcp_v6_network_no_ipv6_address(self):
        """
        @tms_id: litpcds_8126_tc09
        @tms_requirements_id: LITPCDS-8126
        @tms_title: Verify validation when dhcp v6 service created with IPv4
        only network
        @tms_description:  Create a dhcp v6 service with IPv4 only network
        @tms_test_steps:
            @step: Create a dhcp v6 service with IPv4 only network
            @result: Item created
            @step: Inherit this dhcp service to node 1 and node 2
            @result: Items inherited
            @step: Create plan
            @result: ValidationError are raised
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """

        nodes = []
        node_urls = self.find(self.ms_node, "/deployments", "node")
        node_urls.sort()

        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]
        # CREATE TEST NETWORK 1
        network_url = networks_path + "/test_network8126"
        props = "name='test1' subnet='192.168.1.0/24'"
        self.execute_cli_create_cmd(self.ms_node, network_url,
                                    "network", props)

        free_nics = \
            self.verify_backup_free_nics(self.ms_node, node_urls[0],
                                         required_free_nics=2,
                                         backup_files=False)
        self.test_node_if1 = free_nics[0]
        self.test_node_if2 = free_nics[1]

        free_nics = \
            self.verify_backup_free_nics(self.ms_node, node_urls[1],
                                         required_free_nics=2,
                                         backup_files=False)
        self.test_node2_if1 = free_nics[0]
        self.test_node2_if2 = free_nics[1]

        # node1 eth1
        if_url_1 = node_urls[0] + "/network_interfaces/if_8126"
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='test1' \
                    ipaddress='192.168.1.1'".\
                    format(self.test_node_if1["MAC"],
                           self.test_node_if1["NAME"])

        self.execute_cli_create_cmd(self.ms_node, if_url_1, "eth", eth_props)

        # node2 eth1
        if_url_2 = node_urls[1] + "/network_interfaces/if_8126"
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='test1' \
                    ipaddress='192.168.1.2'".\
                    format(self.test_node2_if1["MAC"],
                           self.test_node2_if1["NAME"])

        self.execute_cli_create_cmd(self.ms_node, if_url_2, "eth", eth_props)

        # Create the dhcp stuff

        base_url = "/software/services"
        service_props = "service_name=dhcp_8126"
        service_url = base_url + "/s8126"
        subnet_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s8126"
        # intial range
        ranges = [['2001:2200:82a1:0103:3456:1234:aaaa:aaa2',
                   '2001:2200:82a1:0103:3456:1234:aabb:aaa2']]

        range1_start = ranges[0][0]
        range1_end = ranges[0][1]
        range1_props = "start={0} end={1}".format(range1_start, range1_end)
        range1_url = subnet_url + "/ranges/r1"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp6-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp6-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range1_url,
                                    "dhcp6-range", range1_props)

        node_urls = self.find(self.ms_node, "/deployments", "node")

        for node in node_urls:
            nodes.append(self.get_node_filename_from_url(self.ms_node,
                                                         node))
        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s8126"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url)

        node2_dhcp_url = node_urls[1] + "/services/s8126"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node2_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        # create plan
        _, err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                    expect_positive=False)

        # check for error msgs

        err1 = if_url_1
        err2 = if_url_2

        err3 = 'Create plan failed: A network interface that references '\
               'a network that is also referenced by a "dhcp6-subnet", must '\
               'have an IPv6 address defined'

        self.assertTrue(self.is_text_in_list(err1, err))
        self.assertTrue(self.is_text_in_list(err2, err))
        self.assertEqual(2, self.count_text_in_list(err3, err))

    @attr('all', 'revert', 'story8126', 'story8126_tc10')
    def test_10_n_create_dhcp_v6_subnet_overlapping_ranges(self):
        """
        @tms_id: litpcds_8126_tc10
        @tms_requirements_id: LITPCDS-8126
        @tms_title: Verify validation when dhcp-range is created with non ipv6
        addresses
        @tms_description: Create a dhcp-subnet that has two overlapping ranges
        and check for a Validation error.
        @tms_test_steps:
            @step: Create a dhcp service with dhcp6-range start and end values
            @result: Item created
            @step: Create plan
            @result: Plan created successfully
            @step: Inherit to peer nodes node1 & node2
            @result: Items inherited
            @step: create plan
            @result: Plan is created
            @step: Create a second dhcp service with the same dhcp6-range
            start and end values as in the first created dhcp service.
            @result: Item created
            @step: Create plan
            @result: ValidationError are raised
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """

        self.create_network_and_interfaces()

        base_url = "/software/services"
        service_props = "service_name=dhcp_8126"
        service_url = base_url + "/s8126"
        subnet_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s8126"
        # intial range
        ranges = [['2001:2200:82a1:0103:3456:1234:aaaa:1000',
                   '2001:2200:82a1:0103:3456:1234:aabb:2000']]

        range1_start = ranges[0][0]
        range1_end = ranges[0][1]
        range1_props = "start={0} end={1}".format(range1_start, range1_end)
        range1_url = subnet_url + "/ranges/r1"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp6-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp6-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range1_url,
                                    "dhcp6-range", range1_props)

        node_urls = self.find(self.ms_node, "/deployments", "node")

        nodes = []
        for node in node_urls:
            nodes.append(self.get_node_filename_from_url(self.ms_node,
                                                         node))
        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s8126"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url)

        node2_dhcp_url = node_urls[1] + "/services/s8126"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node2_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        # create plan
        self.execute_cli_createplan_cmd(self.ms_node)

        # Create second overlapping range

        range2_start = ranges[0][0]
        range2_end = ranges[0][1]
        range2_props = "start={0} end={1}".format(range2_start, range2_end)
        range2_url = subnet_url + "/ranges/r2"

        self.execute_cli_create_cmd(self.ms_node, range2_url,
                                    "dhcp6-range", range2_props)

        # create plan
        _, err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                    expect_positive=False)

        # check for error msgs

        err1 = node1_dhcp_url + '/subnets/s8126/ranges/r1'
        err2 = node2_dhcp_url + '/subnets/s8126/ranges/r2'
        err3 = 'dhcp6-range overlaps with "{0}"'.\
            format(node1_dhcp_url + '/subnets/s8126/ranges/r2')
        err4 = 'dhcp6-range overlaps with "{0}"'.\
            format(node2_dhcp_url + '/subnets/s8126/ranges/r2')

        self.assertTrue(self.is_text_in_list(err1, err))
        self.assertTrue(self.is_text_in_list(err2, err))
        self.assertTrue(self.is_text_in_list(err3, err))
        self.assertTrue(self.is_text_in_list(err4, err))

    @attr('all', 'revert', 'story8126', 'story8126_tc15')
    def test_15_n_create_dhcp_v6_service_range_with_prefix(self):
        """
        @tms_id: litpcds_8126_tc15
        @tms_requirements_id: LITPCDS-8126
        @tms_title: Verify validation when dhcp-range is created with non ipv6
        addresses
        @tms_description:  Create a dhcp v6 service and ranges with addresses
        and prefixes given for the start and end properties, and check for
        Validation error at create plan.
        @tms_test_steps:
            @step: Create a dhcp v6 service with invalid range values and check
            that ValidationError error is raised
            @result: ValidationError raised
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        node_urls = self.find(self.ms_node, "/deployments", "node")
        node_urls.sort()
        self.create_two_networks_two_interfaces()

        dhcp_service_name = 'dhcp_srv1'
        dhcp_infra_path = '/software/services/dhcp1'
        subnet_name = 'sub1'
        ipv6_range = (
            self.ipv6_prefixes[0] + '::10/64',
            self.ipv6_prefixes[0] + '::20/64'
            )

        self._add_service(dhcp_infra_path, dhcp_service_name)
        self._add_subnet(dhcp_infra_path, subnet_name, self.ipv6_networks[0])

        range_start, range_end = ipv6_range
        _, std_err, _ = self.execute_cli_create_cmd(
            self.ms_node,
            '{0}/subnets/{1}/ranges/r1'.format(
                dhcp_infra_path, subnet_name),
            'dhcp6-range',
            'start={0} end={1}'.format(range_start, range_end),
            expect_positive=False
            )
        self.assertTrue(
            self.is_text_in_list(
                "Invalid IPv6Address value '{0}::10/64'".format(
                    self.ipv6_prefixes[0]), std_err) and \
            self.is_text_in_list(
                "Invalid IPv6Address value '{0}::20/64'".format(
                    self.ipv6_prefixes[0]), std_err)
            )

    @attr('all', 'revert', 'story8126', 'story8126_tc16')
    def test_16_p_deploy_dhcp_v6_and_v4_update_eth_ipv6(self):
        """
        @tms_id: litpcds_8126_tc16
        @tms_requirements_id: LITPCDS-8126
        @tms_title: Deploy dhcp v6 and v4 services to the same interface, then
        update the dhcp v6
        @tms_description:  This deploys a dhcp v6 and dhcp v4 services on
        nodes where both using the same interface on the same network, and
        then updates only the ipv6 address of the eth.
        @tms_test_steps:
            @step: Create a network item
            @result: Item created
            @step: Create interface items on node1 and node2
            @result: Items created
            @step: Create a dhcp6-service with subnet and range
            @result: Items created
            @step: Inherit the dhcp6 service to node1 as primary and to node2
            as non primary
            @result: Items inherited
            @step: Create a second dhcp6 service with subnet and range
            @result: Items created
            @step: Inherit this service to node1 as primary and to node2 as
            non-primary
            @result: Items inherited
            @step: Create and run a plan
            @result: Plan runs successfully.
            @step: Update ipv6address on node1 interface
            @result: Item updated
            @step: Create and run plan
            @result: Plan runs to completion successfully.
            @step: Check the dhcp6.con, check the contents on node1 and node2
            @result: All is as expected.
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        nodes = []
        node_urls = self.find(self.ms_node, "/deployments", "node")
        node_urls.sort()
        self.create_network_and_interfaces()

        dhcp4_service_name = 'dhcp4_srv'
        dhcp6_service_name = 'dhcp6_srv'
        dhcp4_infra_path = '/software/services/dhcp4'
        dhcp6_infra_path = '/software/services/dhcp6'
        subnet4_name = 'sub4'
        subnet6_name = 'sub6'
        dhcp6_ranges = [
            (self.ipv6_prefixes[0] + '::10', self.ipv6_prefixes[0] + '::20')
            ]
        dhcp4_ranges = [
            (self.ipv4_subnet_prefix + '10', self.ipv4_subnet_prefix + '20')
            ]

        # DHCP6
        self._add_service(dhcp6_infra_path, dhcp6_service_name)
        self._add_subnet(dhcp6_infra_path, subnet6_name, self.ipv6_networks[0])
        self._add_ranges(dhcp6_infra_path, subnet6_name, dhcp6_ranges, 1)
        self._add_inherit(
            dhcp6_infra_path, node_urls[0], dhcp6_service_name, 'primary=true'
            )
        self._add_inherit(
            dhcp6_infra_path, node_urls[1], dhcp6_service_name, 'primary=false'
            )

        # DHCP4
        self.execute_cli_create_cmd(
            self.ms_node,
            dhcp4_infra_path,
            'dhcp-service',
            'service_name=' + dhcp4_service_name
            )
        self.execute_cli_create_cmd(
            self.ms_node,
            dhcp4_infra_path + '/subnets/' + subnet4_name,
            'dhcp-subnet',
            'network_name=' + self.ipv6_networks[0]
            )
        range_start, range_end = dhcp4_ranges[0]
        self.execute_cli_create_cmd(
            self.ms_node,
            '{0}/subnets/{1}/ranges/r4'.format(
                dhcp4_infra_path, subnet4_name
                ),
            'dhcp-range',
            'start={0} end={1}'.format(range_start, range_end)
            )
        self.execute_cli_inherit_cmd(
            self.ms_node,
            node_urls[0] + '/services/' + dhcp4_service_name,
            dhcp4_infra_path,
            'primary=true'
            )
        self.execute_cli_inherit_cmd(
            self.ms_node,
            node_urls[1] + '/services/' + dhcp4_service_name,
            dhcp4_infra_path,
            'primary=false'
            )

        for node in node_urls:
            nodes.append(self.get_node_filename_from_url(self.ms_node, node))

        # Setup further nics cleaning in teardown.
        self.interfaces_cleanup(nodes, self.nics_node1, self.nics_node2)

        self._create_and_run_plan()

        # Update IPv6 addr
        self.execute_cli_update_cmd(
            self.ms_node, node_urls[0] + "/network_interfaces/if_8126",
            'ipv6address=' + self.ipv6_prefixes[0] + '::5/64'
            )
        self._create_and_run_plan()

        std_err = self.data_driven_verification(
            node_urls,
            [self.nics_node1[0]],
            [self.nics_node2[0]],
            [[self.ipv6_prefixes[0] + '::' + self.ipv6_masks[0]]],
            dhcp6_ranges
            )
        self.assertEqual([], std_err)

    #@attr('all', 'revert', 'story8126', 'story8126_tc17')
    def obsolete_17_n_create_dhcp_v6_service_one_node_only_p_or_s(self):
        '''
        Obslolete due to fuctionality delivered in LITPCDS-8265
        Steps:
        1. Create a dhcp v6 service that only appears on one node with as
           the primary and check for a Validation error at create plan.
        2. Create a dhcp v6 service that that only appears on one node as
           the secondary and check for a Validation error at create plan.
        '''
        pass

    @attr('all', 'revert', 'story8126', 'story8126_tc18')
    def test_18_n_create_dhcp_v6_service_duplicate_secondary(self):
        """
        @tms_id: litpcds_8126_tc18
        @tms_requirements_id: LITPCDS-8126
        @tms_title: Verify validation when dhcp-range is created with non
        ipv6 addresses
        @tms_description: Create a dhcp v6 service that appears on two nodes,
        but appears both times as secondary and check for a Validation error.
        @tms_test_steps:
            @step: Create a dhcp service
            @result: Item created
            @step: Inherit this dhcp service to node 1 with false both
            assigned to the property primary.
            @result: ValidationError raised as one dhcp6 service must be
            deployed once as primary and one as non-primary.
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        node_urls = self.find(self.ms_node, "/deployments", "node")
        node_urls.sort()
        self.create_two_networks_two_interfaces()

        dhcp_infra_path1 = '/software/services/dhcp1'
        dhcp_service_name1 = 'dhcp_srv'
        dhcp_network1 = self.ipv6_networks[0]
        subnet1_name = 'sub1'
        inherit_name1 = 'dhcp1'
        range1_ips = [
            (self.ipv6_prefixes[0] + '::10', self.ipv6_prefixes[0] + '::20')
            ]

        self._add_service(dhcp_infra_path1, dhcp_service_name1)
        self._add_subnet(dhcp_infra_path1, subnet1_name, dhcp_network1)
        self._add_ranges(dhcp_infra_path1, subnet1_name, range1_ips, 1)
        self._add_inherit(
            dhcp_infra_path1, node_urls[0], inherit_name1, 'primary=false')
        self._add_inherit(
            dhcp_infra_path1, node_urls[1], inherit_name1, 'primary=false')

        _, std_err, _ = self.execute_cli_createplan_cmd(
            self.ms_node, expect_positive=False
            )
        self.assertTrue(self.is_text_in_list(
            'dhcp6-service "dhcp_srv" must be deployed exactly once as '\
            'primary and once as non-primary', std_err))

    @attr('all', 'revert', 'story8126', 'story8126_tc19')
    def test_19_n_non_ipv6_address_dhcp_v6_range(self):
        """
        @tms_id: litpcds_8126_tc19
        @tms_requirements_id: LITPCDS-8126
        @tms_title: Verify validation when dhcp-range is created with non ipv6
        addresses
        @tms_description: Create a dhcp-range with non-ipv6 addresses given
        for the start and end properties, and check for a Validation error.
        @tms_test_steps:
            @step: Create a dhcp service with invalid values for dhcp6-range
            @result: ValidationError raised Invalid IPv6Address value
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        node_urls = self.find(self.ms_node, "/deployments", "node")
        node_urls.sort()
        self.create_two_networks_two_interfaces()

        dhcp_service_name = 'dhcp_srv1'
        dhcp_infra_path = '/software/services/dhcp1'
        subnet_name = 'sub1'
        ipv6_range = ['192.168.64.128/24', '192.168.64.240/24']

        self._add_service(dhcp_infra_path, dhcp_service_name)
        self._add_subnet(dhcp_infra_path, subnet_name, self.ipv6_networks[0])

        range_start, range_end = ipv6_range
        _, std_err, _ = self.execute_cli_create_cmd(
            self.ms_node,
            '{0}/subnets/{1}/ranges/r1'.format(
                dhcp_infra_path, subnet_name),
            'dhcp6-range',
            'start={0} end={1}'.format(range_start, range_end),
            expect_positive=False
            )

        self.assertTrue(
            self.is_text_in_list(
                "Invalid IPv6Address value '{0}'".format(ipv6_range[0]),
                std_err) and \
            self.is_text_in_list(
                "Invalid IPv6Address value '{0}'".format(ipv6_range[1]),
                std_err)
            )

    @attr('all', 'revert', 'story8126', 'story8126_tc20')
    def test_20_n_reuse_dhcp_v4_property(self):
        """
        @tms_id: litpcds_8126_tc20
        @tms_requirements_id: LITPCDS-8126
        @tms_title: Check for a Validation error when dhcp v6 service tries to
        reuse a dhcp v4property
        @tms_description: Create dhcp v6 service, which trying to reuse
        existing dhcp v4 property (service url) and check for a Validation
        error (both services are deployed within the same network).
        @tms_test_steps:
            @step: Create a dhcp6 service
            @result: Item created
            @step: Create a dhcp service with the same service_name as the
            dhcp6 service
            @result: ItemExistsError is raised
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        dhcp_infra_path = '/software/services/dhcp1'
        dhcp_srv_name = 'dhcp_srv'
        self._add_service(dhcp_infra_path, dhcp_srv_name)
        _, std_err, _ = self.execute_cli_create_cmd(
            self.ms_node,
            dhcp_infra_path,
            'dhcp-service',
            'service_name=' + dhcp_srv_name,
            expect_positive=False
            )
        self.assertTrue(self.is_text_in_list(
            'Item already exists in model: dhcp1', std_err))

    @attr('all', 'revert', 'story8126', 'story8126_tc21')
    def test_21_n_two_dhcp_v6_services_on_the_same_nodes(self):
        """
        @tms_id: litpcds_8126_tc21
        @tms_requirements_id: LITPCDS-8126
        @tms_title: Create two full dhcp-services and deploy both services to
        the peer nodes
        @tms_description: Create two full dhcp-services (with subnets and
        ranges) and deploy both services on the same pair of nodes.
        @tms_test_steps:
            @step: Create two full dhcp-services
            @result: Item created
            @step: Inherit these dhcp services to node1 and node2
            @result: Items inherited
            @step: Create plan and check for ValidationError
            @result: ValidationError messages are raised
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """

        node_urls = self.find(self.ms_node, "/deployments", "node")
        node_urls.sort()
        self.create_two_networks_two_interfaces()

        dhcp_service_name1 = 'dhcp_srv1'
        dhcp_service_name2 = 'dhcp_srv2'
        dhcp_infra_path1 = '/software/services/dhcp1'
        dhcp_infra_path2 = '/software/services/dhcp2'
        subnet1_name = 'sub1'
        subnet2_name = 'sub2'
        ipv6_ranges = [
            (self.ipv6_prefixes[0] + '::10', self.ipv6_prefixes[0] + '::20')
            ]

        # First set
        self._add_service(dhcp_infra_path1, dhcp_service_name1)
        self._add_subnet(dhcp_infra_path1, subnet1_name, self.ipv6_networks[0])
        self._add_ranges(dhcp_infra_path1, subnet1_name, ipv6_ranges, 1)
        self._add_inherit(
            dhcp_infra_path1, node_urls[0], dhcp_service_name1, 'primary=true'
            )
        self._add_inherit(
            dhcp_infra_path1, node_urls[1], dhcp_service_name1, 'primary=false'
            )

        # Second set
        self._add_service(dhcp_infra_path2, dhcp_service_name2)
        self._add_subnet(dhcp_infra_path2, subnet2_name, self.ipv6_networks[0])
        self._add_ranges(dhcp_infra_path2, subnet2_name, ipv6_ranges, 1)
        self._add_inherit(
            dhcp_infra_path2, node_urls[0], dhcp_service_name2, 'primary=true'
            )
        self._add_inherit(
            dhcp_infra_path2, node_urls[1], dhcp_service_name2, 'primary=false'
            )

        # Verify error
        _, std_err, _ = self.execute_cli_createplan_cmd(
            self.ms_node, expect_positive=False
            )

        node1_fname = self.get_node_filename_from_url(
            self.ms_node, node_urls[0]
            )

        self.assertTrue(self.is_text_in_list(
            'Node "{0}" must have at most one dhcp6-service'.\
            format(node1_fname), std_err))

    @attr('all', 'revert', 'story8126', 'story8126_tc22')
    def test_22_n_create_dhcp_v6_subnet_invalid_network_name(self):
        """
        @tms_id: litpcds_8126_tc22
        @tms_requirements_id: LITPCDS-8126
        @tms_title: Create a dhcp-subnet item type with invalid network
        @tms_description: Create a dhcp-subnet item type with network_name=test
        where test is an invalid network and check for a Validation error at
        create plan.
        @tms_test_steps:
            @step: Create a dhcp service with an invalid subnet item property
            @result: Item created
            @step: Inherit this dhcp service to node1 and node2
            @result: Items inherited
            @step: Create plan
            @result: ValidationError is raised as the network specified is
            invalid and not configured on the node
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        node_urls = self.find(self.ms_node, "/deployments", "node")
        node_urls.sort()
        dhcp_infra_path = '/software/services/dhcp'
        dhcp_service_name = 'dhcp_srv'
        dhcp_network = 'none__such'
        subnet1_name = 'sub1'
        range1_ips = [('2002::10', '2002::20')]

        self._add_service(dhcp_infra_path, dhcp_service_name)
        self._add_subnet(dhcp_infra_path, subnet1_name, dhcp_network)
        self._add_ranges(dhcp_infra_path, subnet1_name, range1_ips, 1)
        self._add_inherit(
            dhcp_infra_path, node_urls[0], dhcp_service_name, 'primary=true')
        self._add_inherit(
            dhcp_infra_path, node_urls[1], dhcp_service_name, 'primary=false')

        _, std_err, _ = self.execute_cli_createplan_cmd(
            self.ms_node, expect_positive=False
            )

        node1_fname = self.get_node_filename_from_url(
            self.ms_node, node_urls[0]
            )

        node2_fname = self.get_node_filename_from_url(
            self.ms_node, node_urls[1]
            )

        self.assertTrue(self.is_text_in_list(
            'The network "none__such" referenced by "dhcp6-subnet" is not'\
            ' configured on node "{0}"'.format(node2_fname), std_err))

        self.assertTrue(self.is_text_in_list(
            'The network "none__such" referenced by "dhcp6-subnet" is not'\
            ' configured on node "{0}"'.format(node1_fname), std_err))

    @attr('all', 'revert', 'story8126', 'story8126_tc23')
    def test_23_n_create_dhcp_v6_services_duplicate_service_name(self):
        """
        @tms_id: litpcds_8126_tc23
        @tms_requirements_id: LITPCDS-8126
        @tms_title: Create two dhcp v6 services, which have the same
        service_name
        @tms_description: Create two dhcp v6 services, which have the same
        service_name and check for a Validation error at create plan.
        @tms_test_steps:
            @step: Create the first dhcp v6 service with service_name
            dhcp_srv
            @result: Item created
            @step: Inherit the dhcp service to node1 and node2
            @result: Items created
            @step: Create a second dhcp v6 service with service_name dhcp_srv
            @result: Item created
            @step: Inherit this service to node1 and node2
            @result: plan executes successfully
            @step: Create plan
            @result: ValidationError error message thrown at create_plan as
            there were two dhcp services created which have the same
            service_name.
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """

        node_urls = self.find(self.ms_node, "/deployments", "node")
        node_urls.sort()
        self.create_two_networks_two_interfaces()

        dhcp_infra_path1 = '/software/services/dhcp1'
        dhcp_infra_path2 = '/software/services/dhcp2'
        dhcp_service_name1 = 'dhcp_srv'
        dhcp_service_name2 = 'dhcp_srv'
        dhcp_network1 = self.ipv6_networks[0]
        dhcp_network2 = self.ipv6_networks[1]
        subnet1_name = 'sub1'
        subnet2_name = 'sub2'
        inherit_name1 = 'dhcp1'
        inherit_name2 = 'dhcp2'
        range1_ips = [
            (self.ipv6_prefixes[0] + '::10', self.ipv6_prefixes[0] + '::20')
            ]
        range2_ips = [
            (self.ipv6_prefixes[1] + '::10', self.ipv6_prefixes[1] + '::20')
            ]

        self._add_service(dhcp_infra_path1, dhcp_service_name1)
        self._add_subnet(dhcp_infra_path1, subnet1_name, dhcp_network1)
        self._add_ranges(dhcp_infra_path1, subnet1_name, range1_ips, 1)
        self._add_inherit(
            dhcp_infra_path1, node_urls[0], inherit_name1, 'primary=true')
        self._add_inherit(
            dhcp_infra_path1, node_urls[1], inherit_name1, 'primary=false')

        self._add_service(dhcp_infra_path2, dhcp_service_name2)
        self._add_subnet(dhcp_infra_path2, subnet2_name, dhcp_network2)
        self._add_ranges(dhcp_infra_path2, subnet2_name, range2_ips, 1)
        self._add_inherit(
            dhcp_infra_path2, node_urls[0], inherit_name2, 'primary=true')
        self._add_inherit(
            dhcp_infra_path2, node_urls[1], inherit_name2, 'primary=false')

        _, std_err, _ = self.execute_cli_createplan_cmd(
            self.ms_node, expect_positive=False
            )
        self.assertTrue(self.is_text_in_list(
            'dhcp6-service name "dhcp_srv" is not unique across'\
            ' all deployments', std_err))

    def _plan_tasks_states(self, stdout):
        '''
        Get number of tasks from show_plan, organized by state
        '''

        tasks_states = {'Initial': 0,
                        'Running': 0,
                        'Success': 0,
                        'Failed': 0,
                        'Stopped': 0}

        num_phases = self.cli.get_num_phases_in_plan(stdout)
        for phase in xrange(1, num_phases + 1):
            num_tasks = self.cli.get_num_tasks_in_phase(stdout, phase)
            for task in xrange(1, num_tasks + 1):
                task_state = self.cli.get_task_status(stdout, phase, task)
                tasks_states[task_state] += 1

        return tasks_states

    #attr('all', 'revert', 'story8126', 'story8126_tc24')
    def obsolete_24_p_deploy_dhcp_v6_idempotent_plan(self):
        '''
        Description:
        This test is being obsoleted as it was relying upon a specific series
        of plan tasks to be generated in a specific order, which no longer
        occurs thanks to a change in core. To actually test idempotents a
        dhcp service would need to be deployed, following which the LITP model
        containing the dhcp service specification would need to be deleted
        and the same specification then used to populate the current LITP
        model, followed by a create and run plan which should be successful.

            This deploys a dhcp-service on nodes where plan is designed
            to fail and is rerun it again.
        Steps:
            1- Create a full dhcp v6 service with a subnet on networkX
               and ranges.
            2- Deploy the service on a pair of nodes. One of the phase
               of the plan outside of dhcp v6 is designed to fail.
            3- Run Plan and check failed task(s)
            5- Recreate and run the the same plan again
            6- Check tasks consistency
        '''
        pass
