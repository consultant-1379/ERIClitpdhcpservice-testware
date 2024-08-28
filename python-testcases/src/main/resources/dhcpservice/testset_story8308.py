'''
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     Febuary 2015
@author:    Carlos Novo
@summary:   Integration
            Agile: STORY-8308
'''

from litp_generic_test import GenericTest, attr
import test_constants


class Story8308(GenericTest):
    """
    As a LITP User I want to add ntp-servers option in the dhcp service,
    so I can configure which ntp servers will be used by my VMs
    """

    test_node_if1 = None
    test_node_if2 = None
    test_node_if2 = None
    test_node2_if1 = None
    test_node2_if2 = None
    nics_node1 = None
    nics_node2 = None
    test_ms_if1 = None

    node_urls = None
    service_url = None
    dhcpd_conf = None

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
        super(Story8308, self).setUp()

        # 2. Set up variables used in the test
        self.ms_node = self.get_management_node_filenames()[0]

        self.node_urls = self.find(self.ms_node, "/deployments", "node")
        self.service_url = "/software/services/s8308"
        # dhcpd.conf path
        self.dhcpd_conf = "{0}/dhcpd.conf".format(test_constants.
                                                  DHCPD_CONF_DIR)

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
        super(Story8308, self).tearDown()

    def check_servers_status(self, status):
        """
        Checks dhcpd server status
        """
        nodes = []
        for node in self.node_urls:
            nodes.append(self.get_node_filename_from_url(self.ms_node,
                                                         node))

        cmd = '/sbin/service dhcpd status'
        for node in nodes:
            stdout, _, _ = self.run_command(node,
                                            cmd,
                                            su_root=True)

            self.assertTrue(self.is_text_in_list(status, stdout))

    def create_network_and_interfaces(self):
        """
        Description:
            Litp create one test interface and network per node:
        Actions:
            1. Litp create one test interface and network
                for one dhcp subnets.
        Results:
            litp create command for direct plan task execution
        """

        nodes = []
        for node in self.node_urls:
            nodes.append(self.get_node_filename_from_url(self.ms_node,
                                                         node))
        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]
        # CREATE TEST NETWORK 1
        network_url = networks_path + "/test_network8308"
        props = "name='test1' subnet='10.10.10.0/24'"
        self.execute_cli_create_cmd(self.ms_node, network_url,
                                    "network", props)

        # Add an eth to the nodes with an ipaddress on the associated network
        free_nics = \
            self.verify_backup_free_nics(self.ms_node, self.node_urls[0])
        self.test_node_if1 = free_nics[0]

        free_nics = \
            self.verify_backup_free_nics(self.ms_node, self.node_urls[1])
        self.test_node2_if1 = free_nics[0]

        # node1 eth
        if_url = self.node_urls[0] + "/network_interfaces/if_8308"
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='test1' ipaddress='10.10.10.1'".\
                    format(self.test_node_if1["MAC"],
                           self.test_node_if1["NAME"])

        self.execute_cli_create_cmd(self.ms_node, if_url, "eth", eth_props)

        # node2 eth
        if_url = self.node_urls[1] + "/network_interfaces/if_8308"
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='test1' ipaddress='10.10.10.2'".\
                    format(self.test_node2_if1["MAC"],
                           self.test_node2_if1["NAME"])

        self.execute_cli_create_cmd(self.ms_node, if_url, "eth", eth_props)

        # NODE1 DECONFIGURE test interface 1
        self.add_nic_to_cleanup(nodes[0],
                                self.test_node_if1["NAME"],
                                flush_ip=True)
        # NODE2 DECONFIGURE test interface 2
        self.add_nic_to_cleanup(nodes[1],
                                self.test_node2_if1["NAME"],
                                flush_ip=True)

    def create_base_dhcp_server(self, ntpservers=""):
        """
        Creates full dhcpd service
        """

        expected = "option ntp-servers {0};".format(", ".
                                                    join(ntpservers.
                                                         split(',')))

        self.create_network_and_interfaces()

        # create dhcp service
        service_props = "service_name=dhcp_8308 ntpservers={0} "\
                        "nameservers='8.8.8.8'".format(ntpservers)
        subnet_props = "network_name=test1"
        subnet_url = self.service_url + "/subnets/s8308"
        range_start = "10.10.10.3"
        range_end = "10.10.10.7"
        range_props = "start={0} end={1}".format(range_start, range_end)
        range_url = subnet_url + "/ranges/r1"
        ntpservers_props = "ntpservers={0}".format(ntpservers)

        self.execute_cli_create_cmd(self.ms_node, self.service_url,
                                    "dhcp-service",
                                    service_props)

        self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                    "dhcp-subnet", subnet_props)

        self.execute_cli_create_cmd(self.ms_node, range_url,
                                    "dhcp-range", range_props)

        self.execute_cli_update_cmd(self.ms_node,
                                    self.service_url, ntpservers_props)

        # inherit service on both nodes
        node1_dhcp_url = self.node_urls[0] + "/services/s8308"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     self.service_url)

        node2_dhcp_url = self.node_urls[1] + "/services/s8308"
        primary_prop = "primary=false"
        self.execute_cli_inherit_cmd(self.ms_node, node2_dhcp_url,
                                     self.service_url, props="{0}".
                                     format(primary_prop))

        # create plan
        self.execute_cli_createplan_cmd(self.ms_node)
        # run plan
        self.execute_cli_runplan_cmd(self.ms_node)
        self.assertTrue(self.wait_for_plan_state(self.ms_node,
                                                 test_constants.PLAN_COMPLETE))

        # check .conf file exists
        for node_url in self.node_urls:
            node_fname = self.get_node_filename_from_url(self.ms_node,
                                                         node_url)
            std_out = self.get_file_contents(node_fname, self.dhcpd_conf)

            self.assertTrue(self.is_text_in_list(expected, std_out))

        self.check_servers_status('running')

        return True

    @attr('all', 'revert', 'story8308', 'story8308_tc01')
    def test_01_p_install_test(self):
        """
        @tms_id: litpcds_8308_tc01
        @tms_requirements_id: LITPCDS-8308
        @tms_title: Deploys a DHCP server on two nodes
        @tms_description: Create a deployment with a dhcp service (with
        ntpservers ) deployed on both nodes
        @tms_test_steps:
            @step: Create a network item
            @result: Item created
            @step: Create one eth type network interface on each of the peer
            nodes.
            @result: Items created.
            @step: Create a dhcp-service with dhcp-subnet and dhcp-range
            @result: Items created.
            @step: Update property ntpservers on the dhcp-service
            @result: Item updated.
            @step: Inherit the dhcp-service to node1 as primary and to node2
            as non-primary
            @result: Items inherited
            @step: Create and run plan
            @result: Plan runs successfully.
            @step: Check that the dhcpd.conf file is configured correctly on
            node1 and node2
            @result: dhcpd.conf file is configured correctly
            @step: Check that the dhcpd service is running on node1 and node2
            @result: The dhcpd service is running as expected.
        @tms_test_precondition:  N/A
        @tms_execution_type: Automated
        """

        self.assertTrue(self.create_base_dhcp_server(ntpservers="1.1.1.1"))

    @attr('all', 'revert', 'story8308', 'story8308_tc02')
    def test_02_p_create_update_remove_netservers_prop(self):
        """
        @tms_id: litpcds_8308_tc02
        @tms_requirements_id: LITPCDS-8308
        @tms_title: Create, update, and remove ntpservers properties
        @tms_description: Creates a DHCP service with the ntpservers property
        set. It then updates and removes the property
        @tms_test_steps:
        @step: Create a dhcp service with a list of two ntpservers
        (ntpservers=""0.ie.pool.ntp.org,1.1.1.1"")
        @result: dhcp service siccessfully created
        @step: Deploy the service on both nodes
        @result: dhcp service successfully deployed to peer nodes
        @step: Check that the .conf file is configured correctly with both
        servers in same order.
        @result: Configuration matches expected output
        @step: Check that dhcpd service is running on nodes
        @result: dhcpd service confirmed to be running on peer nodes
        @step: Update the ntpservers values, adding a new ipv4 address
        (ntpservers=""2.2.2.2,0.ie.pool.ntp.org,1.1.1.1"")
        @result: ntpservers values are updated
        @step: Check that the .conf file is configured correctly and in right
        order.
        @result: Configuration matches expected output
        @step: Check that dhcpd service is running on nodes
        @result: dhcpd service confirmed to be running on peer nodes
        @step:  Update the ntpservers values, adding a new FQDN name
        (ntpservers=""ntp-server.server-1.org., 2.2.2.2,0.ie.pool.ntp.org,
        1.1.1.1"")
        @result: ntpservers values and FQDN name updated
        @step:  Check that the .conf file is configured correctly and in
        right order.
        @result: Configuration matches expected output
        @step:  Check that dhcpd service is running on nodes
        @result: dhcpd service confirmed to be running on peer nodes
        @step: Update the ntpservers values, removing one of the ipv4
        addresses (ntpservers=""ntp-server.server-1.org.,
        2.2.2.2,0.ie.pool.ntp.org"")
        @result: ntpservers values successfully updated
        @step:  Check that the .conf file is configured correctly and in
        right order.
        @result: Configuration matches expected output
        @step:  Check that dhcpd service is running on nodes
        @result: dhcpd service confirmed to be running on peer nodes
        @step: Update the ntpservers values, removing one of the FQDN names
        (ntpservers=""ntp-server.server-1.org.,2.2.2.2"")
        @result: @result: ntpservers values updated and FQDN name removed
        @step:  Check that the .conf file is configured correctly and
                in right order.
        @result: Configuration matches expected output
        @step: Check that dhcpd service is running on nodes
        @result: dhcpd service confirmed to be running on peer nodes
        @step: Remove the ntpservers property
        @result: ntpservers properties successfully removed
        @step: Check that the .conf file is configured correctly
        @result: Configuration matches expected output
        @step:  Check that dhcpd service is running on nodes
        @result: dhcpd service confirmed to be running on peer nodes
        @tms_test_precondition: N/A
        @tms_execution_type: Automated
        """

        self.assertTrue(self.create_base_dhcp_server
                        (ntpservers='0.ie.pool.ntp.org,1.1.1.1'))

        # Steps 1 to 16

        steps_ntpservers = [
            # "0.ie.pool.ntp.org,1.1.1.1",  # Already covered in create_base
            "2.2.2.2,0.ie.pool.ntp.org,1.1.1.1",  # step 5
            "ntp-server.server-1.org,2.2.2.2,0.ie.pool.ntp.org",  # step 8
            "ntp-server.server-1.org,2.2.2.2"  # step 14
            ]

        for ntpservers in steps_ntpservers:

            update_props = "ntpservers={0}".format(ntpservers)
            expected = "option ntp-servers {0};".format(", ".
                                                        join(ntpservers.split
                                                             (',')))

            self.execute_cli_update_cmd(self.ms_node,
                                        self.service_url, update_props)

            # create plan and run_plan
            self.execute_cli_createplan_cmd(self.ms_node)
            self.execute_cli_runplan_cmd(self.ms_node)
            self.assertTrue(self.wait_for_plan_state(self.ms_node,
                                                     test_constants.
                                                     PLAN_COMPLETE))

            # 6 check .conf file exists
            for node_url in self.node_urls:
                node_fname = self.get_node_filename_from_url(self.ms_node,
                                                             node_url)
                std_out = self.get_file_contents(node_fname, self.dhcpd_conf)

                self.assertTrue(self.is_text_in_list(expected, std_out))

                self.check_servers_status('running')

        # Step 17 remove ntpservers

        self.execute_cli_update_cmd(self.ms_node, self.service_url,
                                    "ntpservers", action_del=True)

        self.execute_cli_createplan_cmd(self.ms_node)
        self.execute_cli_runplan_cmd(self.ms_node)
        self.assertTrue(self.wait_for_plan_state(self.ms_node,
                                                 test_constants.PLAN_COMPLETE))

        for node_url in self.node_urls:
            node_fname = self.get_node_filename_from_url(self.ms_node,
                                                         node_url)
            std_out = self.get_file_contents(node_fname, self.dhcpd_conf)

            expected = "option ntp-servers"
            self.assertFalse(self.is_text_in_list(expected, std_out))

            self.check_servers_status('running')

    @attr('all', 'revert', 'story8308', 'story8308_tc03')
    def test_03_n_validate_ntpservers_property(self):
        """
        @tms_id: litpcds_8308_tc03
        @tms_requirements_id: LITPCDS-8308
        @tms_title: Validate the value assigned to ntpservers
        @tms_description: Verify that ValidationError is thrown when a not
        permitted value is given to as a value to ntpservers
        @tms_test_steps:
            @step: Create a dhcp service with an empty list
            (ntpservers=\"\"\"\")
            @result: DHCP service created
            @step:Create a dhcp service with duplicated IPs
            (ntpservers=""1.1.1.1,1.1.1.1,3.3.3.3"")
            @result: DHCP service created
            @step:Create a dhcp service with duplicated FQDN
            (ntpservers=""server1.org,2.2.2.2,server1.org"")
            @result: DHCP service created
            @step:Create a dhcp service with an invalid IP
            (ntpservers=""1.1.1.1,1.2.3.4.5,2.2.2.2"")
            @result: DHCP service created
            @step:Create a dhcp service with an invalid IP
            (ntpservers=""1.1.1.1,555,2.2.2.2"")
            @result: DHCP service created
            @step:Create a dhcp service with an invalid FQDN
            (ntpservers=""1.1.1.1,server_1.com"")
            @result: DHCP service created
            @step:Create a dhcp service with an invalid separator
            (ntpservers=""1.1.1.1;2.2.2;2 3.3.3.3"")
            @result: DHCP service created
            @step:Create a dhcp service with white spaces
            (ntpservers=""1.1.1.1, 2.2.2.2, 3.3.3.3"")
            @result: DHCP service created
        @tms_test_precondition: N/A
        @tms_execution_type: Automated
        """

        ######################################################################
        # 1
        ######################################################################

        ntpservers = ""
        service_props = "service_name=dhcp_8308 ntpservers={0}".\
            format(ntpservers)

        _, stderr, _ = self.execute_cli_create_cmd(self.ms_node,
                                                   self.service_url,
                                                   "dhcp-service",
                                                   service_props,
                                                   expect_positive=False)

        self.assertTrue(self.is_text_in_list("Invalid value", stderr))

        ######################################################################
        # 2
        ######################################################################

        ntpservers = "1.1.1.1,2.2.2.2,1.1.1.1"
        service_props = "service_name=dhcp_8308 ntpservers={0}".\
            format(ntpservers)

        _, stderr, _ = self.execute_cli_create_cmd(self.ms_node,
                                                   self.service_url,
                                                   "dhcp-service",
                                                   service_props,
                                                   expect_positive=False)

        self.assertTrue(self.is_text_in_list("Duplicate NTP server "
                                             "address(es) detected", stderr))

        ######################################################################
        # 3
        ######################################################################

        ntpservers = "server1.org,1.1.1.1,server1.org"
        service_props = "service_name=dhcp_8308 ntpservers={0}".\
            format(ntpservers)

        _, stderr, _ = self.execute_cli_create_cmd(self.ms_node,
                                                   self.service_url,
                                                   "dhcp-service",
                                                   service_props,
                                                   expect_positive=False)

        self.assertTrue(self.is_text_in_list("Duplicate NTP server "
                                             "address(es) detected", stderr))

        ######################################################################
        # 4
        ######################################################################

        ntpservers = "1.1.1.1,1.2.3.4.5,2.2.2.2"
        service_props = "service_name=dhcp_8308 ntpservers={0}".\
            format(ntpservers)

        _, stderr, _ = self.execute_cli_create_cmd(self.ms_node,
                                                   self.service_url,
                                                   "dhcp-service",
                                                   service_props,
                                                   expect_positive=False)

        self.assertTrue(self.is_text_in_list('NTP address "1.2.3.4.5" '
                                             'is not valid.', stderr))

        ######################################################################
        # 5
        ######################################################################

        ntpservers = "1.1.1.1,555,2.2.2.2"
        service_props = "service_name=dhcp_8308 ntpservers={0}".\
            format(ntpservers)

        _, stderr, _ = self.execute_cli_create_cmd(self.ms_node,
                                                   self.service_url,
                                                   "dhcp-service",
                                                   service_props,
                                                   expect_positive=False)

        self.assertTrue(self.is_text_in_list('NTP address "555" is not valid.',
                                             stderr))

        ######################################################################
        # 6
        ######################################################################

        ntpservers = "1.1.1.1,server_1.com"
        service_props = "service_name=dhcp_8308 ntpservers={0}".\
            format(ntpservers)

        _, stderr, _ = self.execute_cli_create_cmd(self.ms_node,
                                                   self.service_url,
                                                   "dhcp-service",
                                                   service_props,
                                                   expect_positive=False)

        self.assertTrue(self.is_text_in_list('Hostname in "server_1.com" '
                                             'cannot contain underscores',
                                             stderr))

        ######################################################################
        # 7
        ######################################################################

        ntpservers = "'1.1.1.1;2.2.2.2;3.3.3.3'"
        service_props = "service_name=dhcp_8308 ntpservers={0}".\
            format(ntpservers)

        _, stderr, _ = self.execute_cli_create_cmd(self.ms_node,
                                                   self.service_url,
                                                   "dhcp-service",
                                                   service_props,
                                                   expect_positive=False)

        self.assertTrue(self.is_text_in_list("Invalid value", stderr))

        ######################################################################
        # 8
        ######################################################################

        ntpservers = "'1.1.1.1, 2.2.2.2, 3.3.3.3'"
        service_props = "service_name=dhcp_8308 ntpservers={0}".\
            format(ntpservers)

        _, stderr, _ = self.execute_cli_create_cmd(self.ms_node,
                                                   self.service_url,
                                                   "dhcp-service",
                                                   service_props,
                                                   expect_positive=False)

        self.assertTrue(self.is_text_in_list("Invalid value", stderr))

    #attr('all', 'revert', 'story8308', 'story8308_tc05')
    def obsolete_05_p_deploy_dhcp_idempotent_plan(self):
        """
        Description:
        This test is being obsoleted as it was relying upon a specific series
        of plan tasks to be generated in a specific order, which no longer
        occurs thanks to a change in core. To actually test idempotents a
        dhcp service would need to be deployed, following which the LITP model
        containing the dhcp service specification would need to be deleted
        and the same specification then used to populate the current LITP
        model, followed by a create and run plan which should be successful.

        This deploys a dhcp-service on nodes where plan is designed to fail and
        is rerun it again.
        Steps:

            1. Create a full dhcp-service with a subnet on networkX and ranges.
            2. Deploy the service on a pair of nodes. One of the phase of the
            plan outside of dhcp is designed to fail.
            3. Run Plan and check the output (only the designed to fail tasks
            should not pass).
            4. Recreate and run the the same plan again (no dhcp tasks should
            be occurred).
        """
        pass
