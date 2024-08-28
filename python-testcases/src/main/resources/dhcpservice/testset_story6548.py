'''
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     January 2015
@author:    Kieran Duggan, Boyan Mihovski
@summary:   Integration
            Agile: STORY-6548
'''

from litp_generic_test import GenericTest, attr
import test_constants
from test_constants import PLAN_TASKS_INITIAL


class Story6548(GenericTest):
    """
    As a LITP user I want to specify a DHCP service to run on a
    pair of peer nodes so that there is a DHCP service available
    for virtual machines running in the LITP complex (ipv4 only).
    """

    test_node_if1 = None
    test_node_if2 = None
    test_node_if2 = None
    test_node2_if1 = None
    test_node2_if2 = None
    nics_node1 = None
    nics_node2 = None
    test_ms_if1 = None

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
        super(Story6548, self).setUp()

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
        super(Story6548, self).tearDown()

    def create_two_test_networks_two_interfaces(self):
        """
        Description:
            Litp create two test interfaces and networks per node:
        Actions:
            1. Litp create two test interfaces and networks
                for two dhcp subnets.
        Results:
            litp create command for direct plan task execution
        """
        node_urls = self.find(self.ms_node, "/deployments", "node")
        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]
        # CREATE TEST NETWORK 1
        network_url = networks_path + "/test_network6548"
        props = "name='test1' subnet='10.10.10.0/24'"
        self.execute_cli_create_cmd(self.ms_node, network_url,
                                    "network", props)

        # CREATE TEST NETWORK 2
        network_url = networks_path + "/test_network6549"
        props = "name='test2' subnet='20.20.20.0/25'"
        self.execute_cli_create_cmd(self.ms_node, network_url,
                                    "network", props)

        free_nics = \
            self.verify_backup_free_nics(self.ms_node, node_urls[0],
                                         required_free_nics=2)
        self.test_node_if1 = free_nics[0]
        self.test_node_if2 = free_nics[1]

        free_nics = \
            self.verify_backup_free_nics(self.ms_node, node_urls[1],
                                         required_free_nics=2)
        self.test_node2_if1 = free_nics[0]
        self.test_node2_if2 = free_nics[1]

        # node1 eth1
        if_url = node_urls[0] + "/network_interfaces/if_6548"
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='test1' ipaddress='10.10.10.1'".\
                    format(self.test_node_if1["MAC"],
                           self.test_node_if1["NAME"])

        self.execute_cli_create_cmd(self.ms_node, if_url, "eth", eth_props)

        # node1 eth2
        if_url = node_urls[0] + "/network_interfaces/if_6549"
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='test2' ipaddress='20.20.20.1'".\
                    format(self.test_node_if2["MAC"],
                           self.test_node_if2["NAME"])

        self.execute_cli_create_cmd(self.ms_node, if_url, "eth", eth_props)

        # node2 eth1
        if_url = node_urls[1] + "/network_interfaces/if_6548"
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='test1' ipaddress='10.10.10.2'".\
                    format(self.test_node2_if1["MAC"],
                           self.test_node2_if1["NAME"])

        self.execute_cli_create_cmd(self.ms_node, if_url, "eth", eth_props)

        # node2 eth2
        if_url = node_urls[1] + "/network_interfaces/if_6549"
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='test2' ipaddress='20.20.20.2'".\
                    format(self.test_node2_if2["MAC"],
                           self.test_node2_if2["NAME"])

        self.execute_cli_create_cmd(self.ms_node, if_url, "eth", eth_props)

        self.nics_node1 = [self.test_node_if2["NAME"],
                           self.test_node_if1["NAME"]]
        self.nics_node2 = [self.test_node2_if2["NAME"],
                           self.test_node2_if1["NAME"]]

    def create_test_network_and_interfaces(self):
        """
        Description:
            Litp create one test interface and network per node:
        Actions:
            1. Litp create one test interface and network
                for one dhcp subnets.
        Results:
            litp create command for direct plan task execution
        """

        node_urls = self.find(self.ms_node, "/deployments", "node")
        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]
        # CREATE TEST NETWORK 1
        network_url = networks_path + "/test_network6548"
        props = "name='test1' subnet='10.10.10.0/24'"
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
        if_url = node_urls[0] + "/network_interfaces/if_6548"
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='test1' ipaddress='10.10.10.1'".\
                    format(self.test_node_if1["MAC"],
                           self.test_node_if1["NAME"])

        self.execute_cli_create_cmd(self.ms_node, if_url, "eth", eth_props)

        # node2 eth
        if_url = node_urls[1] + "/network_interfaces/if_6548"
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='test1' ipaddress='10.10.10.2'".\
                    format(self.test_node2_if1["MAC"],
                           self.test_node2_if1["NAME"])

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
            Check that /etc/dhcp/dhcpd.conf, /etc/sysconfig/dhcpd and
            /etc/dhcp/dhcpd.pools are populated after
            the dhcp service installation.
        Args:
            node_fname (list): all nodes to be de configured.
            dhcpd_conf (str): path to dhcpd.conf.
            dhcpd.pools (list): path to dhcpd.pools.
            dhcpd_sysconf (str): The full path to /etc/sysconfig/dhcpd
        Results:
            The errors generated after the validation.
        """
        errors = []
        # check the existence of dhcpd.conf into the node
        if not self.remote_path_exists(node_fname,
                                       dhcpd_conf):
            errors.append("dhcpd.conf doesn't exist into the node")
        # check the existence of /etc/sysconfig/dhcpd
        if not self.remote_path_exists(node_fname,
                                       dhcpd_sysconf):
            errors.append("/etc/sysconfig/dhcpd" +
                          "doesn't exist into the node")

        # check the existence of dhcpd.pools into the nodes
        if not self.remote_path_exists(node_fname,
                                       dhcpd_pools):
            errors.append("dhcpd.pools" +
                          "doesn't exist into the node")
        # check the existence of /etc/sysconfig/dhcpd
        if not self.remote_path_exists(node_fname,
                                       dhcpd_sysconf):
            errors.append("/etc/sysconfig/dhcpd" +
                          "doesn't exist into the node")

        # check the existence of dhcpd.pools into the nodes
        if not self.remote_path_exists(node_fname,
                                       dhcpd_pools):
            errors.append("dhcpd.pools" +
                          "doesn't exist into the node")

        return errors

    def check_dhcpd_conf_content(self, node_path, dhcpd_conf, server_ip,
                                 peer_ip, role):
        """
        Description:
            Checking /etc/sysconfig/dhcpd values after successfull plan.
        Args:
            node_path (list): all nodes to be configured.
            dhcpd_conf (str): path to conf file configured.
            server_ips (str): Primary server IP address.
            peer_ip (str): Secondary server IP address.
            role (str): Role of the server.
        Results:
            The errors generated after the validation.
        """
        # check one node
        errors = []
        # CHECK dhcpd.conf FILE CONTENT NODES
        std_out = self.get_file_contents(node_path, dhcpd_conf,
                                         su_root=True)
        server_addr = "address {0};".format(server_ip)
        peer_addr = "peer address {0};".format(peer_ip)

        if not self.is_text_in_list(role, std_out):
            errors.append('The node dhcp role '
                          'is not correct')

        if not self.is_text_in_list(server_addr, std_out) or not \
                self.is_text_in_list(peer_addr, std_out):
            errors.append('The node dhcp IP '
                          'address is not correct')

        return errors

    def check_sysconf_dhcpd_content(self, node_fname, node_ifs, dhcpd_sysconf):
        """
        Description:
            Checking /etc/sysconfig/dhcpd values after successfull plan.
        Args:
            node_fname (list): all nodes to be configured.
            node_ifs (list): Used networking adapters.
            dhcpd_sysconf (str): The full path to /etc/sysconfig/dhcpd
        Results:
            The errors generated after the validation.
        """
        errors = []

        std_out = self.get_file_contents(node_fname,
                                         dhcpd_sysconf)
        indices = [i for i, s in enumerate(std_out) if 'DHCPDARGS' in s]
        if len(indices) == 0:
            errors.append("No DHCPDARGS declarations found.")
            return errors
        elif len(indices) > 1:
            errors.append("Duplicate DHCPDARGS declarations found.")
            return errors
        split_args = std_out[indices[0]].replace("\"", '').split()
        for iface in node_ifs:
            if not self.is_text_in_list(iface, split_args):
                errors.append("The dhcp server" +
                              " not listening the correct adapter")

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
            expected_subnet = "subnet {0} netmask {1}".format(item[0], item[1])
            expected_subnet_mask = "option subnet-mask {0};".format(item[1])
            if not self.is_text_in_list(expected_subnet, std_out) or not \
                    self.is_text_in_list(expected_subnet_mask, std_out):
                errors.append("The dhcp {0} {1}" +
                              "configuration is" +
                              " not correct".
                              format(expected_subnet, expected_subnet_mask))
            self.assertEqual(len(dhcp_subnet),
                             self.count_text_in_list("subnet ", std_out))
            self.assertEqual(len(dhcp_subnet),
                             self.count_text_in_list("subnet-mask", std_out))
        return errors

    def check_pools_conf_ranges(self, std_out, ranges):
        """
        Description:
            Checking /etc/dhcp/dhcpd.pool values for IP ranges
            after successfull plan.
        Args:
            std_out (list): The content of the file after successfull plan.
            dhcpd_props (list): dhcp values from the model.
        Results:
            The errors generated after the validation.
        """

        errors = []

        for item in ranges:
            expected = "range {0} {1};".format(item[0], item[1])
            if not self.is_text_in_list(expected, std_out):
                errors.append('The dhcp {0} '
                              'configuration is'
                              ' not correct'.format(expected))

            self.assertEqual(len(ranges),
                             self.count_text_in_list("range", std_out))
        return errors

    def data_driven_verification(self, node_urls,
                                 node1_ifs, node2_ifs,
                                 node1_mgmt_if_ip, node2_mgmt_if_ip,
                                 dhcp_subnet, ranges):
        """
        Description:
            Check system configuration, output of the executed plan.
        Args:
            dhcpd_props (list): dhcpd properties which coming
            from the model (single subnet).
            node_urls (list): all nodes to be configured.
            node1_ifs (list): used interfaces  - node1.
            node2_ifs (list): used interfaces - node2.
            dhcp_ips (list): primary, secondary servers IPs.
            dhcp_subnets (list): network addresses for used subnets.
            dhcp_subnet_masks (list): subnet masks for used subnets.
        Results:
            stderr of checking configuration
        """
        errors = []
        # dhcpd.conf path
        dhcpd_conf = "{0}/dhcpd.conf".format(test_constants.
                                             DHCPD_CONF_DIR)
        # dhcpd.pools path
        dhcpd_pools = "{0}/dhcpd.pools".format(test_constants.
                                               DHCPD_CONF_DIR)
        # dhcpd path
        dhcpd_sysconf = "{0}/dhcpd".format(test_constants.
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
                role = "primary"
                server_address = node1_mgmt_if_ip
                peer_address = node2_mgmt_if_ip
                node_ifs = node1_ifs
            else:
                role = "secondary"
                server_address = node2_mgmt_if_ip
                peer_address = node1_mgmt_if_ip
                node_ifs = node2_ifs

            check_dhcpd_conf = self.check_dhcpd_conf_content(node_fname,
                                                             dhcpd_conf,
                                                             server_address,
                                                             peer_address,
                                                             role)
            errors.extend(check_dhcpd_conf)
            # CHECK /etc/sysconfig/dhcpd FILE CONTENT NODES

            check_sysconf_dhcpd = self. \
                check_sysconf_dhcpd_content(node_fname,
                                            node_ifs,
                                            dhcpd_sysconf)
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

    @attr('all', 'revert', 'story6548', 'story6548_tc01', 'cdb_priority1')
    def test_01_p_configure_extend_remove_full_dhcp_service(self):
        """
        @tms_id: litpcds_6548_tc01
        @tms_requirements_id: LITPCDS-6548
        @tms_title: Config, extend and remove a full dhcp_service
        @tms_description: Creates a model with a dhcp-service, a
        single dhcp-subnet and a single dhcp-range. It then adds a new subnet
        with three ranges to the service. It removes one of these new ranges.
        It then removes the subnet the other two range from the service.
        Finally it removes the dhcp-service completely
        @tms_test_steps:
            @step: Create a dhcp-service, a dhcp-subnet(on a non-mgmt-network)
            and specify a single dhcp-range.
            @result: A dhcp-service containing a dhcp-subnet and a specified
            dhcp range is created successfully
            @step: Deploy the dhcp-service on two peer nodes, as the primary
            on node1 and as the secondary on node2.
            @result:dhcp-service successfully deployed on node1 as primary,
            and as secondary on node2
            @step: Create and run plan, then check config.
            @result: Plan successfully run and config matches expected output
            @step: Add a new subnet and with three ranges to the applied
            dhcp-service.
            @result: New subnet added to existing dhcp-service successfully
            @step: Create and run plan, then check that the new ranges and
            subnet are configured
            @result: Plan successfully run and config matches expected output
            @step: Remove the full dhcp-service
            @result: dhcp-service successfully removed
            @step: Create and run plan then check that the dhcp service has
            been deconfigured correctly on the peer nodes
            @result: Plan has run successfully and the dhcp is not configured
            on the peer nodes as expected.
        @tms_test_precondition:  N/A
        @tms_execution_type: Automated
        """

        nodes = []
        ranges = [['10.10.10.3', '10.10.10.3']]

        # Get nodes list and urls
        node_urls = self.find(self.ms_node, "/deployments", "node")
        node_urls.sort()
        for node in node_urls:
            nodes.append(self.get_node_filename_from_url(self.ms_node,
                                                         node))

        # get mgmt ip node 1
        eth_path = self.find(self.ms_node, node_urls[0], "bridge")[0]
        node1_mgmt_if_ip = self.get_props_from_url(self.ms_node, eth_path,
                                                   "ipaddress")

        # get mgmt ip node 2
        eth_path = self.find(self.ms_node, node_urls[1], "bridge")[0]
        node2_mgmt_if_ip = self.get_props_from_url(self.ms_node, eth_path,
                                                   "ipaddress")

        free_nics = \
            self.verify_backup_free_nics(self.ms_node, node_urls[0],
                                         required_free_nics=2,
                                         backup_files=False)
        test_node_if1 = free_nics[0]
        test_node_if2 = free_nics[1]

        free_nics_node1 = [test_node_if1['NAME'],
                           test_node_if2['NAME']]
        free_nics = \
            self.verify_backup_free_nics(self.ms_node, node_urls[1],
                                         required_free_nics=2,
                                         backup_files=False)
        test_node2_if1 = free_nics[0]
        test_node2_if2 = free_nics[1]
        free_nics_node2 = [test_node2_if1['NAME'],
                           test_node2_if2['NAME']]

        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]
        # CREATE TEST NETWORK 1
        first_network_url = networks_path + "/test1_network6548"
        second_network_url = networks_path + "/test2_network6548"
        first_net_name = 'test1'
        second_net_name = 'test2'

        dhcp_subnet = [['10.10.10.0', '255.255.255.0']]
        props = "name={0} subnet={1}/24".format(first_net_name,
                                                dhcp_subnet[0][0])
        self.execute_cli_create_cmd(self.ms_node, first_network_url,
                                    "network", props)

        # define eth props
        first_subnet_eth_props_node1 = \
            "macaddress={0} device_name={1} ipaddress='10.10.10.1' "\
            "network_name={2}".format(test_node_if1['MAC'],
                                      test_node_if1['NAME'],
                                      first_net_name)

        first_subnet_eth_props_node2 = \
            "macaddress={0} device_name={1} ipaddress='10.10.10.2' "\
            "network_name={2}".format(test_node2_if1['MAC'],
                                      test_node2_if1['NAME'],
                                      first_net_name)
        first_subnet_node1_if_url = \
            node_urls[0] + "/network_interfaces/1if_6548"
        first_subnet_node2_if_url = \
            node_urls[1] + "/network_interfaces/1if_6548"

        second_subnet_eth_props_node1 = \
            "macaddress={0} device_name={1} ipaddress='20.20.20.1' "\
            "network_name={2}".format(test_node_if2['MAC'],
                                      test_node_if2['NAME'],
                                      second_net_name)

        second_subnet_eth_props_node2 = \
            "macaddress={0} device_name={1} ipaddress='20.20.20.2' "\
            "network_name={2}".format(test_node2_if2['MAC'],
                                      test_node2_if2['NAME'],
                                      second_net_name)

        second_subnet_node1_if_url = \
            node_urls[0] + "/network_interfaces/2if_6548"
        second_subnet_node2_if_url = \
            node_urls[1] + "/network_interfaces/2if_6548"

        # create dhcp service
        base_url = "/software/services"
        service_props = "service_name=dhcp_6548"
        service_url = base_url + "/s6548"
        first_subnet_props = "network_name=test1"
        second_subnet_props = "network_name=test2"
        first_subnet_url = service_url + "/subnets/1s6548"
        second_subnet_url = service_url + "/subnets/2s6548"
        node1_dhcp_url = node_urls[0] + "/services/s6548"
        node2_dhcp_url = node_urls[1] + "/services/s6548"

        first_range_url = first_subnet_url + "/ranges/r1"

        second_range_url = second_subnet_url + "/ranges/r2"

        third_range_url = second_subnet_url + "/ranges/r3"

        fourth_range_url = second_subnet_url + "/ranges/r4"

        # create eth adapters on nodes only - first subnet
        self.execute_cli_create_cmd(self.ms_node, first_subnet_node1_if_url,
                                    "eth", first_subnet_eth_props_node1)
        self.execute_cli_create_cmd(self.ms_node, first_subnet_node2_if_url,
                                    "eth", first_subnet_eth_props_node2)

        # Deploy dhcp service with one subnet and range
        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, first_subnet_url,
                                    "dhcp-subnet", first_subnet_props)

        self.execute_cli_create_cmd(self.ms_node, first_range_url,
                                    "dhcp-range", "start={0} end={1}".
                                    format(ranges[0][0], ranges[0][1]))

        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url)
        self.execute_cli_inherit_cmd(self.ms_node, node2_dhcp_url,
                                     service_url, "primary=false")

        # create plan
        self.execute_cli_createplan_cmd(self.ms_node)
        # run plan
        self.execute_cli_runplan_cmd(self.ms_node)
        self.assertTrue(self.wait_for_plan_state(self.ms_node,
                                                 test_constants.PLAN_COMPLETE))

        # Check dhcpd process per NODE to be active
        cmd = "pgrep -l dhcpd"
        _, _, rc = self.run_command(nodes[0], cmd, su_root=True)
        self.assertEqual(0, rc)

        _, _, rc = self.run_command(nodes[1], cmd, su_root=True)
        self.assertEqual(0, rc)

        # Check dhcpd process auto-start per NODE to be active

        cmd = "/sbin/chkconfig | grep dhcpd"
        stdout, _, _ = self.run_command(nodes[0], cmd, su_root=True)
        self.assertTrue(self.count_text_in_list("on", stdout))
        stdout, _, _ = self.run_command(nodes[1], cmd, su_root=True)
        self.assertTrue(self.count_text_in_list("on", stdout))

        # Check that dhcp service with one subnet is configured correctly
        # Start and stop ranges are validated against the model
        # because only one subnet is used

        props = self.get_props_from_url(self.ms_node, service_url)
        std_err = self.data_driven_verification(node_urls,
                                                [free_nics_node1[0]],
                                                [free_nics_node2[0]],
                                                node1_mgmt_if_ip,
                                                node2_mgmt_if_ip,
                                                dhcp_subnet,
                                                ranges)
        self.assertEqual([], std_err)

        # Add a new subnet and with three ranges to the applied dhcp-service.
        # Run plan and check that the new ranges and subnet are configured.

        # create eth adapters on nodes only - second subnet
        ranges_from_two_to_four = [['20.20.20.8', '20.20.20.15'],
                                   ['20.20.20.16', '20.20.20.20'],
                                   ['20.20.20.21', '20.20.20.26']]
        ranges.extend(ranges_from_two_to_four)
        # second subnet definition
        second_subnet = ['20.20.20.0', '255.255.255.192']
        dhcp_subnet.append(second_subnet)

        props = "name={0} subnet={1}/26".format(second_net_name,
                                                second_subnet[0])
        self.execute_cli_create_cmd(self.ms_node, second_network_url,
                                    "network", props)
        self.execute_cli_create_cmd(self.ms_node, second_subnet_node1_if_url,
                                    "eth", second_subnet_eth_props_node1)
        self.execute_cli_create_cmd(self.ms_node, second_subnet_node2_if_url,
                                    "eth", second_subnet_eth_props_node2)

        # Deploy dhcp service with second subnet and three ranges

        self.execute_cli_create_cmd(self.ms_node, second_subnet_url,
                                    "dhcp-subnet", second_subnet_props)

        self.execute_cli_create_cmd(self.ms_node, second_range_url,
                                    "dhcp-range", "start={0} end={1}".
                                    format(ranges[1][0], ranges[1][1]))

        self.execute_cli_create_cmd(self.ms_node, third_range_url,
                                    "dhcp-range", "start={0} end={1}".
                                    format(ranges[2][0], ranges[2][1]))

        self.execute_cli_create_cmd(self.ms_node, fourth_range_url,
                                    "dhcp-range", "start={0} end={1}".
                                    format(ranges[3][0], ranges[3][1]))

        # create plan
        self.execute_cli_createplan_cmd(self.ms_node)
        # run plan
        self.execute_cli_runplan_cmd(self.ms_node)
        self.assertTrue(self.wait_for_plan_state(self.ms_node,
                                                 test_constants.PLAN_COMPLETE))

        # Check that dhcp service is configured correctly
        std_err = self.data_driven_verification(node_urls,
                                                free_nics_node1,
                                                free_nics_node2,
                                                node1_mgmt_if_ip,
                                                node2_mgmt_if_ip,
                                                dhcp_subnet,
                                                ranges)
        self.assertEqual([], std_err)

        # Check dhcpd process per NODE to be active
        cmd = "pgrep -l dhcpd"
        _, _, rc = self.run_command(nodes[0], cmd, su_root=True)
        self.assertEqual(0, rc)

        _, _, rc = self.run_command(nodes[1], cmd, su_root=True)
        self.assertEqual(0, rc)

        # Remove the full dhcp-service
        # Run plan and check that it has been deconfigured correctly

        self.execute_cli_remove_cmd(self.ms_node, node1_dhcp_url)

        self.execute_cli_remove_cmd(self.ms_node, node2_dhcp_url)

        self.execute_cli_remove_cmd(self.ms_node, service_url)

        # Setup further nics cleaning in teardown.
        self.interfaces_cleanup(nodes, free_nics_node1, free_nics_node2)

        # create plan
        self.execute_cli_createplan_cmd(self.ms_node)
        # run plan
        self.execute_cli_runplan_cmd(self.ms_node)
        self.assertTrue(self.wait_for_plan_state(self.ms_node,
                                                 test_constants.PLAN_COMPLETE))

        # Check that dhcp service is configured correctly
        std_err = self.data_driven_verification(node_urls,
                                                free_nics_node1,
                                                free_nics_node2,
                                                node1_mgmt_if_ip,
                                                node2_mgmt_if_ip,
                                                dhcp_subnet,
                                                ranges)

        self.assertEqual([], std_err)

        # Check dhcpd process per NODE to be not active
        cmd = "pgrep -l dhcpd"
        _, _, rc = self.run_command(nodes[0], cmd, su_root=True)
        self.assertEqual(1, rc)

        _, _, rc = self.run_command(nodes[1], cmd, su_root=True)
        self.assertEqual(1, rc)

        # Check dhcpd process auto-start per NODE to be not active

        cmd = "/sbin/chkconfig | grep dhcpd"
        stdout, _, _ = self.run_command(nodes[0], cmd, su_root=True)
        self.assertFalse(self.count_text_in_list("on", stdout))

        stdout, _, _ = self.run_command(nodes[0], cmd, su_root=True)
        self.assertFalse(self.count_text_in_list("on", stdout))

    @attr('all', 'revert', 'story6548', 'story6548_tc02')
    def test_02_p_create_update_full_dhcp_service(self):
        """
        @tms_id: litpcds_6548_tc02
        @tms_requirements_id: LITPCDS-6548
        @tms_title: Create and update a full dhcp service
        @tms_description: Creates a model with a dhcp-service, multiple
        subnets, and multiple ranges. It then updates all the properties of a
        service, range and subnet.(including primary/secondary values)
        @tms_test_steps:
            @step:Create two network items under /infrastructure
            @result: Items created
            @step: Create two eth type network interface items on both node1
            and node2
            @result: Item created
            @step: Create a dhcp-service with two dhcp-subnets (on
            non-mgmt-networks) and specify more than one dhcp-range per subnet.
            @result: A dhcp-service containing two dhcp-subnets and more than
            one specified dhcp range is created successfully
            @step: Inherit the dhcp-service onto node1 as primary and node2 as
            non-primary.
            @result: dhcp-service successfully deployed on node1 as primary,
            and as non-primary on node2
            @step: Create and run plan, then check the configuration.
            @result: Plan successfully run and config matches expected output
            @step: Create a third network item under /infrastructure
            @result: Third network item create successfully
            @step: Update the service_name property of the dhcp-service
            @result: service_name property for dhcp_service is successfully
            updated
            @step: Update the start and end properties of a dhcp-range
            (extending the range)
            @result: start and end properties are successfully updated to
            the new values
            @step: Update the start and end properties of a dhcp-range
            (Decreasing the range)
            @result: start and end properties are successfully updated to
            the new values
            @step: Add a new range in the same plan as an existing range is
            updated to test for bug LITPCDS-9039
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
        @tms_test_precondition:  N/A
        @tms_execution_type: Automated
        """

        self.create_two_test_networks_two_interfaces()

        nodes = []

        base_url = "/software/services"
        service_props = "service_name=dhcp_6548"
        service_url = base_url + "/s6548"
        subnet_props = "network_name=test1"
        subnet2_props = "network_name=test2"
        subnet_url = service_url + "/subnets/s6548"
        subnet2_url = service_url + "/subnets/s6549"

        range1_start = "10.10.10.4"
        range1_end = "10.10.10.10"
        range1_props = "start={0} end={1}".format(range1_start, range1_end)
        range1_url = subnet_url + "/ranges/r1"

        range2_start = "10.10.10.12"
        range2_end = "10.10.10.15"
        range2_props = "start={0} end={1}".format(range2_start, range2_end)
        range2_url = subnet_url + "/ranges/r2"

        range3_start = "10.10.10.19"
        range3_end = "10.10.10.25"
        range3_props = "start={0} end={1}".format(range3_start, range3_end)
        range3_url = subnet_url + "/ranges/r3"

        range4_start = "20.20.20.4"
        range4_end = "20.20.20.12"
        range4_props = "start={0} end={1}".format(range4_start, range4_end)
        range4_url = subnet2_url + "/ranges/r4"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, subnet2_url,
                                    "dhcp-subnet", subnet2_props)

        self.execute_cli_create_cmd(self.ms_node, range1_url,
                                    "dhcp-range", range1_props)

        self.execute_cli_create_cmd(self.ms_node, range2_url,
                                    "dhcp-range", range2_props)

        self.execute_cli_create_cmd(self.ms_node, range3_url,
                                    "dhcp-range", range3_props)

        self.execute_cli_create_cmd(self.ms_node, range4_url,
                                    "dhcp-range", range4_props)

        node_urls = self.find(self.ms_node, "/deployments", "node")

        for node in node_urls:
            nodes.append(self.get_node_filename_from_url(self.ms_node,
                                                         node))
        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s6548"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url)

        node2_dhcp_url = node_urls[1] + "/services/s6548"
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

        # Check that dhcp service is configured correctly

        ranges = [['10.10.10.4', '10.10.10.10'],
                  ['10.10.10.12', '10.10.10.15'],
                  ['10.10.10.19', '10.10.10.25'],
                  ['20.20.20.4', '20.20.20.12']]

        # get mgmt ip node 1
        eth_path = self.find(self.ms_node, node_urls[0], "bridge")[0]
        node1_mgmt_if_ip = self.get_props_from_url(self.ms_node, eth_path,
                                                   "ipaddress")

        # get mgmt ip node 2
        eth_path = self.find(self.ms_node, node_urls[1], "bridge")[0]
        node2_mgmt_if_ip = self.get_props_from_url(self.ms_node, eth_path,
                                                   "ipaddress")
        # used dhcp subnet
        dhcp_subnet = [['10.10.10.0', '255.255.255.0'],
                       ['20.20.20.0', '255.255.255.128']]

        std_err = self.data_driven_verification(node_urls,
                                                self.nics_node1,
                                                self.nics_node2,
                                                node1_mgmt_if_ip,
                                                node2_mgmt_if_ip,
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
        props = "name='test3' subnet='30.30.30.0/25'"
        self.execute_cli_create_cmd(self.ms_node, network_url,
                                    "network", props)

        # Update the network_name
        subnet2_props = "network_name=test3"
        self.execute_cli_update_cmd(self.ms_node, subnet2_url, subnet2_props)

        # Update the range ips
        range4_start = "30.30.30.4"
        range4_end = "30.30.30.12"
        range4_props = "start={0} end={1}".format(range4_start, range4_end)
        self.execute_cli_update_cmd(self.ms_node, range4_url, range4_props)

        # update any interfaces using that network
        # node1 eth
        if1_url = node_urls[0] + "/network_interfaces/if_6549"
        if1_props = "ipaddress=30.30.30.1 network_name=test3"
        self.execute_cli_update_cmd(self.ms_node, if1_url, if1_props)
        # node2 eth
        if2_url = node_urls[1] + "/network_interfaces/if_6549"
        if2_props = "ipaddress=30.30.30.2 network_name=test3"
        self.execute_cli_update_cmd(self.ms_node, if2_url, if2_props)

        # update the service_name of the service
        update_props = "service_name=dhcp_update"
        self.execute_cli_update_cmd(self.ms_node, service_url, update_props)

        # decrease range1 and increase range2
        range1_start = '10.10.10.5'
        range1_end = '10.10.10.8'
        range1_props = "start={0} end={1}".format(range1_start, range1_end)
        self.execute_cli_update_cmd(self.ms_node, range1_url, range1_props)

        range2_start = '10.10.10.9'
        range2_end = '10.10.10.17'
        range2_props = "start={0} end={1}".format(range2_start, range2_end)
        self.execute_cli_update_cmd(self.ms_node, range2_url, range2_props)

        #Add a new range in the same plan as an existing range is updated
        range5_start = "10.10.10.44"
        range5_end = "10.10.10.49"
        range5_props = "start={0} end={1}".format(range5_start, range5_end)
        range5_url = subnet_url + "/ranges/r5"

        self.execute_cli_create_cmd(self.ms_node, range5_url,
                                    "dhcp-range", range5_props)

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

        # Check that dhcp service is configured correctly

        dhcp_subnet[1] = ['30.30.30.0', '255.255.255.128']
        # third range remain inchanged
        ranges[0] = ['10.10.10.5', '10.10.10.8']
        ranges[1] = ['10.10.10.9', '10.10.10.17']
        ranges[3] = ['30.30.30.4', '30.30.30.12']
        new_range = ['10.10.10.44', '10.10.10.49']
        ranges.append(new_range)

        # The roles are reversed and checked urls are updated.
        new_roles_nodes_urls = [node_urls[1], node_urls[0]]

        std_err = self.data_driven_verification(new_roles_nodes_urls,
                                                self.nics_node1,
                                                self.nics_node2,
                                                node2_mgmt_if_ip,
                                                node1_mgmt_if_ip,
                                                dhcp_subnet,
                                                ranges)

        self.assertEqual([], std_err)

    @attr('all', 'revert', 'story6548', 'story6548_tc03')
    def test_03_p_deploy_dhcp_update_eth_ip(self):
        """
        @tms_id: litpcds_6548_tc03
        @tms_requirements_id: LITPCDS-6548
        @tms_title: Deploy dhcp-service to peer nodes and update an eth IP
        @tms_description: This deploys a dhcp-service on nodes where an eth is
        on the same network, and then updates the ip of the eth.
        @tms_test_steps:
            @step: Create network item under infrastructure
            @result: Item created successfully.
            @step: Create a eth type network interface on node 1 and node2
            @result: Items created
            @step: Create a full dhcp-service with a dhcp-subnet and dhcp-range
            @result: dhcp-service, dhcp-subnet, and dhcp-range created
            successfully.
            @step: Inherit the dhcp-service to node1 as primary and to node2
            as non primary.
            @result: dhcp-service successfully inherited to the peer nodes
            @step: Create, run plan and check the configuration.
            @result: Plan run successfully and config matches expected output
            @step: Update the ipaddress of the eth on node1.
            @result: IP addresses for eth interface successfully changed on
            node1
            @step: Create and run plan then check that the ipaddress was
            successfully updated.
            @result: Plan is run successfully and ipaddress confirmed to be
            successfully updated
        @tms_test_precondition:  N/A
        @tms_execution_type: Automated
        """

        self.create_test_network_and_interfaces()

        nodes = []
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
        service_props = "service_name=dhcp_6548"
        service_url = base_url + "/s6548"
        subnet_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s6548"
        range_start = "10.10.10.3"
        range_end = "10.10.10.7"
        range_props = "start={0} end={1}".format(range_start, range_end)
        range_url = subnet_url + "/ranges/r1"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range_url,
                                    "dhcp-range", range_props)

        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s6548"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url)

        node2_dhcp_url = node_urls[1] + "/services/s6548"
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

        # update the ip of the eth
        # node1 eth
        if_url = node_urls[0] + "/network_interfaces/if_6548"
        update_props = "ipaddress='10.10.10.51'"

        self.execute_cli_update_cmd(self.ms_node, if_url, update_props)

        # Setup further nics cleaning in teardown.
        for node in node_urls:
            nodes.append(self.get_node_filename_from_url(self.ms_node, node))

        self.interfaces_cleanup(nodes, self.nics_node1, self.nics_node2)

        # create plan
        self.execute_cli_createplan_cmd(self.ms_node)
        # run plan
        self.execute_cli_runplan_cmd(self.ms_node)
        self.assertTrue(self.wait_for_plan_state(self.ms_node,
                                                 test_constants.PLAN_COMPLETE))

        # CHECK INTERFACE IS PINGABLE
        cmd = self.net.get_ping_cmd("10.10.10.51", 10)
        _, stderr, ret_code = self.run_command(nodes[0], cmd)
        self.assertEqual(0, ret_code)
        self.assertEqual([], stderr)

    @attr('all', 'revert', 'story6548', 'story6548_tc04')
    def test_04_n_deploy_dhcp_service_on_ms(self):
        """
        @tms_id: litpcds_6548_tc04
        @tms_requirements_id: LITPCDS-6548
        @tms_title: Inherit the dhcp_service to the MS
        @tms_description: Deploy a dhcp-service on the MS and check for a
        Validation error.
        @tms_test_steps:
            @step: Create network item under infrastructure
            @result: Item created successfully.
            @step: Create network interface item on MS
            @result: Item created successfully
            @step: Create a dhcp-service with dhcp-subnet and dhcp-range
            @result: Item created successfully
            @step: Inherit the dhcp-service to the MS
            @result: ChildNotAllowedError raised.
        @tms_test_precondition:  N/A
        @tms_execution_type: Automated
        """

        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]
        # CREATE TEST NETWORK 1
        network_url = networks_path + "/test_network6548"
        props = "name='test1' subnet='10.10.10.0/24'"
        self.execute_cli_create_cmd(self.ms_node, network_url,
                                    "network", props)

        free_nics = \
            self.verify_backup_free_nics(self.ms_node, "/ms")

        self.test_ms_if1 = free_nics[0]

        ms_url = "/ms/network_interfaces/if_6548"
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='test1' ipaddress='10.10.10.21'".\
                    format(self.test_ms_if1["MAC"],
                           self.test_ms_if1["NAME"])

        self.execute_cli_create_cmd(self.ms_node, ms_url, "eth", eth_props)

        base_url = "/software/services"
        service_props = "service_name=dhcp_6548"
        service_url = base_url + "/s6548"
        subnet_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s6548"
        range_start = "10.10.10.1"
        range_end = "10.10.10.7"
        range_props = "start={0} end={1}".format(range_start, range_end)
        range_url = subnet_url + "/ranges/r1"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range_url,
                                    "dhcp-range", range_props)
        ms_dhcp_url = "/ms/services/s6548"
        _, std_err, _ = self.execute_cli_inherit_cmd(self.ms_node,
                                                     ms_dhcp_url, service_url,
                                                     expect_positive=False)

        self.assertTrue(self.is_text_in_list("ChildNotAllowedError", std_err))

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list('must not be an inherited '
                                             'item', std_err))

    @attr('all', 'revert', 'story6548', 'story6548_tc05')
    def test_05_n_create_dhcp_services_duplicate_service_name(self):
        """
        @tms_id: litpcds_6548_tc05
        @tms_requirements_id: LITPCDS-6548
        @tms_title: Create two dhcp services with the same name of the
        service_name property
        @tms_description: Create two dhcp services, which have the same service
        _name and check for a Validation error.
        @tms_test_steps:
            @step: Create two dhcp-service items which have the same
            service_name
            @result: Items created successfully.
            @step: Inherit the dhcp-service to node1 as non-primary
            @result: Item inherited successfully.
            @step: Create plan and ensure ValidationError messages as the
            service name is not unique
            @result: ValidationErrors are raised.
        @tms_test_precondition:  N/A
        @tms_execution_type: Automated
        """

        node_urls = self.find(self.ms_node, "/deployments", "node")
        base_url = "/software/services"

        service_props = "service_name=dhcp_6548"
        service_url = base_url + "/s6548"
        service_url2 = base_url + "/s6549"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, service_url2,
                                    "dhcp-service", service_props)

        node1_dhcp_url = node_urls[0] + "/services/s6548"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        # Create plan
        _, std_err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                        expect_positive=False)

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list("ValidationError", std_err))

        # Check expected Error is present
        expected_msg = 'dhcp-service name "dhcp_6548" is not ' \
                       'unique across all deployments'
        self.assertTrue(self.is_text_in_list(expected_msg, std_err))

    @attr('all', 'revert', 'story6548', 'story6548_tc08')
    def test_08_n_create_dhcp_subnet_invalid_network_name(self):
        """
        @tms_id: litpcds_6548_tc08
        @tms_requirements_id: LITPCDS-6548
        @tms_title: Create a dhcp subnet with invalid network name as theres
        no network interfaces
        @tms_description: Create a dhcp-subnet item type with network_name=abc
        where abc is an invalid network and check for a Validation error.
        @tms_test_steps:
                @step: Create a dhcp-service
                @result: Item created successfully.
                @step: Create a subnet on the dhcp-service with
                network_name=abc
                @result: Item created successfully.
                @step: Create a dhcp-range with start and end values
                @result: Item created successfully.
                @step: Inherit the dhcp-service to node1 as non-primary
                @result: Item inherited successfully.
                @step: Create plan and ensure ValidationError messages are
                raised as the network referenced in dhcp-subnet is not
                configured on node1
                @result: ValidationErrors are raised.
        @tms_test_precondition:  N/A
        @tms_execution_type: Automated
        """

        base_url = "/software/services"

        service_props = "service_name=dhcp_6548"
        service_url = base_url + "/s6548"
        subnet_props = "network_name=abc"
        subnet_url = service_url + "/subnets/s6548"
        range_start = "10.10.10.1"
        range_end = "10.10.10.7"
        range_props = "start={0} end={1}".format(range_start, range_end)
        range_url = subnet_url + "/ranges/r1"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range_url,
                                    "dhcp-range", range_props)
        node_urls = self.find(self.ms_node, "/deployments", "node")
        node1_dhcp_url = node_urls[0] + "/services/s6548"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        # Create plan
        _, std_err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                        expect_positive=False)

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list("ValidationError", std_err))

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list('Create plan failed: The '
                                             'network "abc" referenced by '
                                             '"dhcp-subnet" is not '
                                             'configured on node ',
                                             std_err))

    @attr('all', 'revert', 'story6548', 'story6548_tc09')
    def test_09_n_create_dhcp_subnet_no_network_interfaces(self):
        """
        @tms_id: litpcds_6548_tc09
        @tms_requirements_id: LITPCDS-6548
        @tms_title: Create a dhcp subnet when theres no network interfaces
        @tms_description: Create dhcp-subnet with a valid network_name=data
        where data is a valid network but has not been referenced by network
        interfaces on the node. Check for a Validation error
        @tms_test_steps:
            @step: Create network item under infrastructure
            @result: Item created.
            @step: Create a dhcp-service
            @result: Item created
            @step: Create a subnet on the dhcp-service with network_name=abc
            @result: Item created
            @step: Create a dhcp-range with start and end values
            @result: Item created
            @step: Inherit the dhcp-service to node1 as non-primary and to
            node2 as primary
            @result: Items inherited
            @step: Create plan and ensure ValidationError messages are raised
            as the network referenced in dhcp-subnet is not configured on the
            nodes
            @result: ValidationErrors are raised.
        @tms_test_precondition:  N/A
        @tms_execution_type: Automated
        """

        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]
        # CREATE TEST NETWORK 1
        network_url = networks_path + "/test_network6548"
        props = "name='test1' subnet='10.10.10.0/24'"
        self.execute_cli_create_cmd(self.ms_node, network_url,
                                    "network", props)

        base_url = "/software/services"
        service_props = "service_name=dhcp_6548"
        service_url = base_url + "/s6548"
        subnet_props = "network_name=abc"
        subnet_url = service_url + "/subnets/s6548"
        range_start = "10.10.10.1"
        range_end = "10.10.10.5"
        range_props = "start={0} end={1}".format(range_start, range_end)
        range_url = subnet_url + "/ranges/r1"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range_url,
                                    "dhcp-range", range_props)

        node_urls = self.find(self.ms_node, "/deployments", "node")
        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s6548"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        node2_dhcp_url = node_urls[1] + "/services/s6548"
        self.execute_cli_inherit_cmd(self.ms_node, node2_dhcp_url, service_url)

        # Create plan
        _, std_err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                        expect_positive=False)

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list("ValidationError", std_err))

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list('Create plan failed: The '
                                             'network "abc" referenced '
                                             'by "dhcp-subnet" is not '
                                             'configured on node', std_err))

    @attr('all', 'revert', 'story6548', 'story6548_tc10')
    def test_10_n_create_dhcp_subnet_mgmt_network(self):
        """
        @tms_id: litpcds_6548_tc10
        @tms_requirements_id: LITPCDS-6548
        @tms_title: Create dhcp subnet on the mgmt network.
        @tms_description: Create a dhcp-subnet on the mgmt network and check
        for a Validation error.
        @tms_test_steps:
            @step: Create network item under infrastructure and create an eth
            type network interface on both node1 and node2
            @result: Items created.
            @step: Create a dhcp-service with a dhcp-range and a dhcp-subnet
            with network_name=mgmt
            @result: Item created
            @step: Inherit the dhcp-service to node1 as non-primary and to
            node2 as primary
            @result: Items inherited
            @step: Create plan and ensure ValidationError messages are raised
            as the dhcp-subnet must not reference the management network
            @result: ValidationErrors are raised.
        @tms_test_precondition:  N/A
        @tms_execution_type: Automated
        """

        mgmt_name = self.get_management_network_name(self.ms_node)
        self.create_test_network_and_interfaces()

        base_url = "/software/services"

        service_props = "service_name=dhcp_6548"
        service_url = base_url + "/s6548"
        subnet_props = "network_name={0}".format(mgmt_name)
        subnet_url = service_url + "/subnets/s6548"
        range_start = "10.10.10.1"
        range_end = "10.10.10.5"
        range_props = "start={0} end={1}".format(range_start, range_end)
        range_url = subnet_url + "/ranges/r1"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range_url,
                                    "dhcp-range", range_props)

        node_urls = self.find(self.ms_node, "/deployments", "node")
        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s6548"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        node2_dhcp_url = node_urls[1] + "/services/s6548"
        self.execute_cli_inherit_cmd(self.ms_node, node2_dhcp_url, service_url)

        # Create plan
        _, std_err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                        expect_positive=False)

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list("ValidationError", std_err))
        # Check expected Error is present
        self.assertTrue(self.is_text_in_list('Create plan failed: '
                                             '"dhcp-subnet" '
                                             'must not reference the '
                                             'management network "mgmt"',
                                             std_err))

    @attr('all', 'revert', 'story6548', 'story6548_tc11')
    def test_11_n_create_dhcp_subnets_duplicate_networks(self):
        """
        @tms_id: litpcds_6548_tc11
        @tms_requirements_id: LITPCDS-6548
        @tms_title: Create dhcp subnets with duplicate networks
        @tms_description: Create a deployment referencing a network more than
        once across the deployment.
        @tms_test_steps:
            @step: Create network item under infrastructure
            @result: Item created.
            @step: Create a dhcp-service
            @result: Item created
            @step: Created a subnet on the dhcp-service with a dhcp-range
            @result: Item created
            @step: Create a duplicate dhcp-subnet on the same dhcp-service but
            with a different dhcp-range value.
            @result: Items created.
            @step: Inherit the dhcp-service to node1 as non-primary and to
            node2 as primary
            @result: Items inherited
            @step: Create plan and ensure ValidationError messages are raised
            as the network specified on the dhcp-subnet isnt configured on
            the nodes
            @result: ValidationErrors are raised.
        @tms_test_precondition:  N/A
        @tms_execution_type: Automated
        """

        node_urls = self.find(self.ms_node, "/deployments", "node")
        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]
        # CREATE TEST NETWORK 1
        network_url = networks_path + "/test_network6548"
        props = "name='test1' subnet='10.10.10.0/24'"
        self.execute_cli_create_cmd(self.ms_node, network_url,
                                    "network", props)

        base_url = "/software/services"

        service_props = "service_name=dhcp_6548"
        service_url = base_url + "/s6548"
        subnet_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s6548"
        subnet2_props = "network_name=test1"
        subnet2_url = service_url + "/subnets/s6549"
        range_start = "10.10.10.1"
        range_end = "10.10.10.7"
        range2_start = "10.10.10.9"
        range2_end = "10.10.10.14"
        range_props = "start={0} end={1}".format(range_start, range_end)
        range_url = subnet_url + "/ranges/r1"
        range2_props = "start={0} end={1}".format(range2_start, range2_end)
        range2_url = subnet2_url + "/ranges/r1"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, subnet2_url,
                                    "dhcp-subnet", subnet2_props)

        self.execute_cli_create_cmd(self.ms_node, range_url,
                                    "dhcp-range", range_props)

        self.execute_cli_create_cmd(self.ms_node, range2_url,
                                    "dhcp-range", range2_props)

        node1_dhcp_url = node_urls[0] + "/services/s6548"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        node2_dhcp_url = node_urls[1] + "/services/s6548"
        self.execute_cli_inherit_cmd(self.ms_node,
                                     node2_dhcp_url, service_url)

        # Create plan
        _, std_err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                        expect_positive=False)

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list("ValidationError", std_err))

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list(' Create plan failed: The '
                                             'network "test1" referenced by '
                                             '"dhcp-subnet" is not configured '
                                             'on node', std_err))

    @attr('all', 'revert', 'story6548', 'story6548_tc12')
    def test_12_n_create_dhcp_subnet_overlapping_ranges(self):
        """
        @tms_id: litpcds_6548_tc12
        @tms_requirements_id: LITPCDS-6548
        @tms_title: Create a dhcp subnet with overlapping ranges
        @tms_description: Create a dhcp-subnet that has two overlapping ranges
        and check for a Validation error.
        @tms_test_steps:
            @step: Create network item under infrastructure
            @result: Item created.
            @step: Create an eth type network interface item on both node1
            and node2
            @result: Items created
            @step:Create a dhcp-service item with dhcp-subnet and dhcp-range
            @result: Item created
            @step: Create a second dhcp-range item with the same start and end
            values as in the other dhcp-subnet
            @result: Item created.
            @step: Inherit the dhcp-service to node1 as non-primary and to
            node2 as primary
            @result: Items inherited
            @step: Create plan and ensure ValidationError messages are raised
            as the dhcp-range values overlap
            @result: ValidationErrors are raised.
        @tms_test_precondition:  N/A
        @tms_execution_type: Automated
        """

        node_urls = self.find(self.ms_node, "/deployments", "node")
        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]
        # CREATE TEST NETWORK 1
        network_url = networks_path + "/test_network6548"
        props = "name='test1' subnet='10.10.10.0/24'"
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
        if_url = node_urls[0] + "/network_interfaces/if_2069"
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='test1' ipaddress='10.10.10.21'".\
                    format(self.test_node_if1["MAC"],
                           self.test_node_if1["NAME"])

        self.execute_cli_create_cmd(self.ms_node, if_url, "eth", eth_props)

        # node2 eth
        if_url = node_urls[1] + "/network_interfaces/if_2069"
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='test1' ipaddress='10.10.10.22'".\
                    format(self.test_node_if1["MAC"],
                           self.test_node_if1["NAME"])

        self.execute_cli_create_cmd(self.ms_node, if_url, "eth", eth_props)

        base_url = "/software/services"
        service_props = "service_name=dhcp_6548"
        service_url = base_url + "/s6548"
        subnet_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s6548"
        range_start = "10.10.10.1"
        range_end = "10.10.10.5"
        range_props = "start={0} end={1}".format(range_start, range_end)
        range_url = subnet_url + "/ranges/r1"
        range2_props = "start={0} end={1}".format(range_start, range_end)
        range2_url = subnet_url + "/ranges/r2"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range_url,
                                    "dhcp-range", range_props)

        self.execute_cli_create_cmd(self.ms_node, range2_url,
                                    "dhcp-range", range2_props)

        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s6548"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        node2_dhcp_url = node_urls[1] + "/services/s6548"
        self.execute_cli_inherit_cmd(self.ms_node,
                                     node2_dhcp_url, service_url)

        # Create plan
        _, std_err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                        expect_positive=False)

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list("ValidationError", std_err))

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list('Create plan failed: dhcp-range '
                                             'overlaps with ',
                                             std_err))

    #@attr('all', 'revert', 'story6548', 'story6548_tc14')
    def obsolete_14_n_create_dhcp_service_one_node_only_primary(self):
        """
        Obslolete due to fuctionality delivered in LITPCDS-8265
        Description:
            Create a dhcp service that only appears on one node
            as the primary and check for a Validation error.
        """

        self.create_test_network_and_interfaces()

        base_url = "/software/services"
        service_props = "service_name=dhcp_6548"
        service_url = base_url + "/s6548"
        subnet_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s6548"
        range_start = "10.10.10.1"
        range_end = "10.10.10.5"
        range_props = "start={0} end={1}".format(range_start, range_end)
        range_url = subnet_url + "/ranges/r1"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range_url,
                                    "dhcp-range", range_props)

        node_urls = self.find(self.ms_node, "/deployments", "node")
        # inherit service on one node
        node2_dhcp_url = node_urls[1] + "/services/s6548"
        self.execute_cli_inherit_cmd(self.ms_node,
                                     node2_dhcp_url, service_url)

        # Create plan
        _, std_err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                        expect_positive=False)

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list("ValidationError", std_err))

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list('dhcp-service "dhcp_6548" must '
                                             'be deployed exactly once as '
                                             'primary and once as non-primary',
                                             std_err))

    #@attr('all', 'revert', 'story6548', 'story6548_tc15')
    def obsolete_15_n_create_dhcp_service_one_node_only_non_primary(self):
        """
        Obslolete due to fuctionality delivered in LITPCDS-8265
        Description:
            Create a dhcp service that only appears on one node
            as non-primary  and check for a Validation error.
        """

        self.create_test_network_and_interfaces()

        base_url = "/software/services"
        service_props = "service_name=dhcp_6548"
        service_url = base_url + "/s6548"
        subnet_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s6548"
        range_start = "10.10.10.1"
        range_end = "10.10.10.5"
        range_props = "start={0} end={1}".format(range_start, range_end)
        range_url = subnet_url + "/ranges/r1"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range_url,
                                    "dhcp-range", range_props)

        node_urls = self.find(self.ms_node, "/deployments", "node")
        # inherit service on one node
        node1_dhcp_url = node_urls[0] + "/services/s6548"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        # Create plan
        _, std_err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                        expect_positive=False)

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list("ValidationError", std_err))

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list('dhcp-service "dhcp_6548" must '
                                             'be deployed exactly once as '
                                             'primary and once as non-primary',
                                             std_err))

    @attr('all', 'revert', 'story6548', 'story6548_tc16')
    def test_16_n_create_dhcp_service_duplicate_primary(self):
        """
        @tms_id: litpcds_6548_tc16
        @tms_requirements_id: LITPCDS-6548
        @tms_title: Create two dhcp_service items both as primary
        @tms_description: Create a dhcp-service that appears on two nodes, but
        appears both times as primary and check for a Validation error.
        @tms_test_steps:
            @step: Create network item under infrastructure
            @result: Item created.
            @step: Create network interface items on node1 and node2
            @result: Items created
            @step: Create a dhcp-service with subnet and range values
            @result: Item created
            @step: Inherit the dhcp-service to node1 and node2 both as primary
            @result: Items inherited
            @step: Create plan and ensure ValidationError messages are raised
            as the dhcp-service should be deployed as one primary and one as
            non-primary
            @result: ValidationErrors are raised.
        @tms_test_precondition:  N/A
        @tms_execution_type: Automated
        """

        self.create_test_network_and_interfaces()

        base_url = "/software/services"
        service_props = "service_name=dhcp_6548"
        service_url = base_url + "/s6548"
        subnet_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s6548"
        range_start = "10.10.10.1"
        range_end = "10.10.10.5"
        range_props = "start={0} end={1}".format(range_start, range_end)
        range_url = subnet_url + "/ranges/r1"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range_url,
                                    "dhcp-range", range_props)

        node_urls = self.find(self.ms_node, "/deployments", "node")
        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s6548"
        self.execute_cli_inherit_cmd(self.ms_node,
                                     node1_dhcp_url, service_url)

        node2_dhcp_url = node_urls[1] + "/services/s6548"
        self.execute_cli_inherit_cmd(self.ms_node,
                                     node2_dhcp_url, service_url)

        # Create plan
        _, std_err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                        expect_positive=False)

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list("ValidationError", std_err))

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list('must be deployed exactly once '
                                             'as primary and once as '
                                             'non-primary',
                                             std_err))
        # Check expected Error is present
        self.assertTrue(self.is_text_in_list('lies within the dhcp-range',
                                             std_err))

    @attr('all', 'revert', 'story6548', 'story6548_tc17')
    def test_17_n_create_dhcp_service_duplicate_secondary(self):
        """
        @tms_id: litpcds_6548_tc17
        @tms_requirements_id: LITPCDS-6548
        @tms_title: Create two dhcp service items both as non-primary
        @tms_description: Create a dhcp-service that appears on two nodes, but
        appears both times as secondary and check for a Validation error.
        @tms_test_steps:
            @step: Create network item under infrastructure
            @result: Item created.
            @step: Create network interface items on node1 and node2
            @result: Items created
            @step: Create a dhcp-service with subnet and range values
            @result: Item created
            @step: Inherit the dhcp-service to node1 and node2 both as
            non-primary
            @result: Items inherited
            @step: Create plan and ensure ValidationError messages are raised
            as the dhcp-service should be deployed as primary and as
            non-primary
            @result: ValidationErrors are raised.
        @tms_test_precondition:  N/A
        @tms_execution_type: Automated
        """

        self.create_test_network_and_interfaces()

        base_url = "/software/services"
        service_props = "service_name=dhcp_6548"
        service_url = base_url + "/s6548"
        subnet_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s6548"
        range_start = "10.10.10.4"
        range_end = "10.10.10.8"
        range_props = "start={0} end={1}".format(range_start, range_end)
        range_url = subnet_url + "/ranges/r1"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range_url,
                                    "dhcp-range", range_props)

        node_urls = self.find(self.ms_node, "/deployments", "node")
        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s6548"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        node2_dhcp_url = node_urls[1] + "/services/s6548"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node2_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        # Create plan
        _, std_err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                        expect_positive=False)

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list("ValidationError", std_err))

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list('must be deployed exactly once as'
                                             ' primary and once'
                                             ' as non-primary',
                                             std_err))

    @attr('all', 'revert', 'story6548', 'story6548_tc18')
    def test_18_n_create_dhcp_service_both_roles_on_same_node(self):
        """
        @tms_id: litpcds_6548_tc18
        @tms_requirements_id: LITPCDS-6548
        @tms_title: Create two dhcp service items on the same node
        @tms_description: Create a dhcp-service that appears twice on the same
        node and check for a Validation error.
        @tms_test_steps:
            @step: Create network item under infrastructure
            @result: Item created.
            @step: Create an eth type network interface items on node1 and
            node2
            @result: Items created
            @step: Create a dhcp-service with subnet and range values
            @result: Item created
            @step: Inherit the dhcp-service to node1 as primary and to node1
            as non-primary
            @result: Items inherited
            @step: Create plan and ensure ValidationError messages are raised.
            @result: ValidationErrors are raised.
        @tms_test_precondition:  N/A
        @tms_execution_type: Automated
        """
        self.create_test_network_and_interfaces()

        base_url = "/software/services"
        service_props = "service_name=dhcp_6548"
        service_url = base_url + "/s6548"
        subnet_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s6548"
        range_start = "10.10.10.1"
        range_end = "10.10.10.5"
        range_props = "start={0} end={1}".format(range_start, range_end)
        range_url = subnet_url + "/ranges/r1"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range_url,
                                    "dhcp-range", range_props)

        node_urls = self.find(self.ms_node, "/deployments", "node")
        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s6548"
        self.execute_cli_inherit_cmd(self.ms_node,
                                     node1_dhcp_url, service_url)

        node1_dhcp_url = node_urls[0] + "/services/s6549"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        # Create plan
        _, std_err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                        expect_positive=False)

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list("ValidationError", std_err))
        # Check expected Error is present
        self.assertTrue(self.is_text_in_list('must have at most one '
                                             'dhcp-service', std_err))

    @attr('all', 'revert', 'story6548', 'story6548_tc20')
    def test_20_n_two_dhcp_services_on_the_same_nodes(self):
        """
        @tms_id: litpcds_6548_tc20
        @tms_requirements_id: LITPCDS-6548
        @tms_title: Create two dhcp services on the peer nodes
        @tms_description: Create two full dhcp-services(with subnets and
        ranges) and deploy both services on the peer nodes. Check for
        a validation error
        @tms_test_steps:
            @step: Create two networks items under /infrastructure and create
            two eth type network interfaces on both peer nodes
            @result: Items created
            @step: Create a dhcp service with subnet and ranges
            @result: Item created
            @step: Inherit this dhcp service to node1 as the primary and to
            node2 as non-primary.
            @result: Items inherited
            @step: Create a second dhcp-service with subnet and ranges
            @result: Item created
            @step: Inherit this dhcp service to node1 as the primary and to
            node2 as non-primary.
            @result: Item inherited to nodes
            @step: Create plan and and ensure ValidationErrors are raised as
            dhcp-range lies within
            @result: ValidationErrors are raised.
        @tms_test_precondition:  N/A
        @tms_execution_type: Automated
        """

        self.create_two_test_networks_two_interfaces()

        node_urls = self.find(self.ms_node, "/deployments", "node")

        base_url = "/software/services"
        service_props = "service_name=dhcp_6548"
        service_url = base_url + "/s6548"
        subnet_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s6548"
        range_start = "10.10.10.1"
        range_end = "10.10.10.5"
        range_props = "start={0} end={1}".format(range_start, range_end)
        range_url = subnet_url + "/ranges/r1"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range_url,
                                    "dhcp-range", range_props)

        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s6548"
        self.execute_cli_inherit_cmd(self.ms_node,
                                     node1_dhcp_url, service_url)

        node2_dhcp_url = node_urls[1] + "/services/s6548"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node2_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        # Create second service and deploy on the same pair of nodes
        base_url = "/software/services"
        service_props = "service_name=dhcp_6549"
        service_url = base_url + "/s6549"
        subnet_props = "network_name=test2"
        subnet_url = service_url + "/subnets/s6549"
        range_start = "20.20.20.1"
        range_end = "20.20.20.5"
        range_props = "start={0} end={1}".format(range_start, range_end)
        range_url = subnet_url + "/ranges/r1"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range_url,
                                    "dhcp-range", range_props)

        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s6549"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url)

        node2_dhcp_url = node_urls[1] + "/services/s6549"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node2_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        # Create plan
        _, std_err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                        expect_positive=False)

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list("ValidationError", std_err))

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list('must have at most one '
                                             'dhcp-service', std_err))

    @attr('all', 'revert', 'story6548', 'story6548_tc21')
    def test_21_n_create_dhcp_range_invalid_network_addresses(self):
        """
        @tms_id: litpcds_6548_tc21
        @tms_requirements_id: LITPCDS-6548
        @tms_title: Create a dhcp service with invalid network addresses
        @tms_description: Create a dhcp-subnet item type with network_name=abc
        where abc is an invalid network and check for a Validation error.
        @tms_test_steps:
            @step: Create a network item under instruction
            @result: Item created
            @step: Create a dhcp-service with dhcp-subnet and dhcp-range
            @result: Item created
            @step: Inherit the dhcp-service to the peer nodes; node1 & node2
            @result: Items inherited
            @step: Create plan and ensure ValidationErrors are raised.
            @result: ValidationsErrors are raised
        @tms_test_precondition:  N/A
        @tms_execution_type: Automated
        """

        base_url = "/software/services"

        service_props = "service_name=dhcp_6548"
        service_url = base_url + "/s6548"
        subnet_props = "network_name=abc"
        subnet_url = service_url + "/subnets/s6548"
        # ipv4address does not match network
        range_start = "50.20.20.4"
        range_end = "50.20.20.7"
        range_props = "start={0} end={1}".format(range_start, range_end)
        range_url = subnet_url + "/ranges/r1"
        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]
        network_url = networks_path + "/test_network6550"
        props = "name='abc' subnet='40.20.20.0/24'"
        self.execute_cli_create_cmd(self.ms_node, network_url,
                                    "network", props)

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range_url,
                                    "dhcp-range", range_props)

        node_urls = self.find(self.ms_node, "/deployments", "node")
        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s6548"
        self.execute_cli_inherit_cmd(self.ms_node,
                                     node1_dhcp_url, service_url)

        node2_dhcp_url = node_urls[1] + "/services/s6548"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node2_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        # Create plan
        _, std_err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                        expect_positive=False)
        # Check expected Error is present
        self.assertTrue(self.is_text_in_list("ValidationError", std_err))

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list('"start" address "50.20.20.4" '
                                             'is not valid for network',
                                             std_err))

        self.assertTrue(self.is_text_in_list('"end" address "50.20.20.7" '
                                             'is not valid for network',
                                             std_err))

    @attr('all', 'revert', 'story6548', 'story6548_tc29')
    def test_29_n_create_dhcp_subnet_hb_network(self):
        """
        @tms_id: litpcds_6548_tc29
        @tms_requirements_id: LITPCDS-6548
        @tms_title: Create a dhcp subnet on hb_network
        @tms_description: Create a dhcp-service with a subnet on a heartbeat
        network. Check for a validation error
        @tms_test_steps:
            @step: Create network item under /infrastructure and create eth
            type interfaces on the peer nodes
            @result: Items created
            @step: Create dhcp-service with subnet and range
            @result: dhcp-service successfully created
            @step: Inherit this service to node1 as primary and node2 as
            non-primary
            @result: dhcp-service successfully inherited to node1 as primary
            and node2 as non-primary
            @step: Create plan and ensure it raises a VaildationError
            @result: ValidationError raised.
        @tms_test_precondition:  N/A
        @tms_execution_type: Automated
        """

        node_urls = self.find(self.ms_node, "/deployments", "node")
        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]
        # CREATE TEST NETWORK
        network_url = networks_path + "/heartbeat_test"
        props = "name='hb_test' "
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
        if_url = node_urls[0] + "/network_interfaces/if_6548"
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='hb_test'".\
                    format(self.test_node_if1["MAC"],
                           self.test_node_if1["NAME"])
        self.execute_cli_create_cmd(self.ms_node, if_url, "eth", eth_props)

        # node2 eth
        if_url = node_urls[1] + "/network_interfaces/if_6548"
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='hb_test'".\
                    format(self.test_node2_if1["MAC"],
                           self.test_node2_if1["NAME"])

        self.execute_cli_create_cmd(self.ms_node, if_url, "eth", eth_props)

        self.nics_node1 = [self.test_node_if1["NAME"]]
        self.nics_node2 = [self.test_node2_if1["NAME"]]

        base_url = "/software/services"

        service_props = "service_name=dhcp_6548"
        service_url = base_url + "/s6548"
        subnet_props = "network_name=hb_test"
        subnet_url = service_url + "/subnets/s6548"
        range_start = "20.20.20.4"
        range_end = "20.20.20.7"
        range_props = "start={0} end={1}".format(range_start, range_end)
        range_url = subnet_url + "/ranges/r1"
        # GET NETWORKS PATH

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range_url,
                                    "dhcp-range", range_props)

        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s6548"
        self.execute_cli_inherit_cmd(self.ms_node,
                                     node1_dhcp_url, service_url)

        node2_dhcp_url = node_urls[1] + "/services/s6548"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node2_dhcp_url,
                                     service_url, props="{0}".
                                     format(primary_prop))

        # Create plan
        _, std_err, _ = self.execute_cli_createplan_cmd(self.ms_node,
                                                        expect_positive=False)

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list("ValidationError", std_err))

        # Check expected Error is present
        self.assertTrue(self.is_text_in_list('Network "hb_test" does '
                                             'not have a subnet specified',
                                             std_err))

    @attr('all', 'revert', 'story6548', 'story6548_tc30')
    def test_30_p_update_network_name_and_range_dhcp_service(self):
        """
        @tms_id: litpcds_6548_tc30
        @tms_requirements_id: LITPCDS-6548
        @tms_title: Update network name and range on dhcp_service
        @tms_description: Creates a dhcp-service on nodes where an eth is on
        the networkX. It then updates networkX, updates the network of the
        subnet and ensures that a plan was created successfully. NOTE: This
        verifies bug LITPCDS-8883
        @tms_test_steps:
            @step: Create a full dhcp-service with a subnet on network with
            name test1 and ranges
            @result: dhcp-service, dhcp-subnet, and dhcp-range created
            successfully
            @step: Deploy the service onto the peer nodes. The nodes will have
            an eth with an ipaddress on network with name test1
            @result: dhcp-service successfully deployed to nodes
            @step: Update network item property name test1 to test3 as
            well as updating the subnet
            @result: The name and subnet properties successfully updated on
            network
            @step: Update the ipaddress of the dhcp-subnet and dhcp-range and
            the interfaces on the nodes
            @result: dhcp-subnet, dhcp-range and the interfaces on the nodes
            have been successfully updated
            @step: Create plan and check tasks are in Initial state
            @result: Plan created and tasks are in state Initial
        @tms_test_precondition:  N/A
        @tms_execution_type: Automated
        """

        self.create_test_network_and_interfaces()

        nodes = []
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
        service_props = "service_name=dhcp_6548"
        service_url = base_url + "/s6548"
        subnet_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s6548"
        range_start = "10.10.10.3"
        range_end = "10.10.10.7"
        range_props = "start={0} end={1}".format(range_start, range_end)
        range_url = subnet_url + "/ranges/r1"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range_url,
                                    "dhcp-range", range_props)
        # inherit service on both nodes
        node1_dhcp_url = node_urls[0] + "/services/s6548"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url)

        node2_dhcp_url = node_urls[1] + "/services/s6548"
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
        network_url = networks_path + "/test_network6548"
        props = "name='test3' subnet='80.80.80.0/24'"
        self.execute_cli_update_cmd(self.ms_node, network_url, props)

        # Update the network_name
        subnet_props = "network_name=test3"
        self.execute_cli_update_cmd(self.ms_node, subnet_url, subnet_props)

        # Update the range ips
        range_start = "80.80.80.3"
        range_end = "80.80.80.7"
        range_props = "start={0} end={1}".format(range_start, range_end)
        self.execute_cli_update_cmd(self.ms_node, range_url, range_props)

        # update any interfaces using that network
        # node1 eth
        if1_url = node_urls[0] + "/network_interfaces/if_6548"
        if1_props = "ipaddress='80.80.80.51' network_name='test3'"
        self.execute_cli_update_cmd(self.ms_node, if1_url, if1_props)
        # node2 eth
        if2_url = node_urls[1] + "/network_interfaces/if_6548"
        if2_props = "ipaddress='80.80.80.52' network_name='test3'"
        self.execute_cli_update_cmd(self.ms_node, if2_url, if2_props)

        #create plan
        _, std_err, _ = self.execute_cli_createplan_cmd(self.ms_node)
        self.assertEquals([], std_err)
        self.execute_cli_showplan_cmd(self.ms_node)

        for node in node_urls:
            nodes.append(self.get_node_filename_from_url(self.ms_node, node))

        node1_hostname = self.get_node_att(nodes[0], 'hostname')
        node2_hostname = self.get_node_att(nodes[1], 'hostname')
        phase_3_2 = 'Configure "dhcp-subnet" on '\
            'network "test3" on node "{0}"'.\
            format(node2_hostname)

        self.assertEqual(PLAN_TASKS_INITIAL,
                         self.get_task_state(self.ms_node,
                                             phase_3_2,
                                             False))

        phase_7_2 = 'Configure "dhcp-subnet" on '\
            'network "test3" on node "{0}"'.\
            format(node1_hostname)

        self.assertEqual(PLAN_TASKS_INITIAL,
                         self.get_task_state(self.ms_node,
                                             phase_7_2,
                                             False))
