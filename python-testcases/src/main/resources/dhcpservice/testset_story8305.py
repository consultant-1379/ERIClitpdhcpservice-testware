'''
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     Febuary 2015
@author:    Kieran Duggan
@summary:   Integration
            Agile: STORY-8305
'''

from litp_generic_test import GenericTest, attr
import test_constants


class Story8305(GenericTest):
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
        super(Story8305, self).setUp()

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
        super(Story8305, self).tearDown()

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

        nodes = []
        node_urls = self.find(self.ms_node, "/deployments", "node")
        for node in node_urls:
            nodes.append(self.get_node_filename_from_url(self.ms_node,
                                                         node))
        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]
        # CREATE TEST NETWORK 1
        network_url = networks_path + "/test_network8305"
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
        if_url = node_urls[0] + "/network_interfaces/if_8305"
        eth_props = "macaddress='{0}' device_name='{1}' \
                    network_name='test1' ipaddress='10.10.10.1'".\
                    format(self.test_node_if1["MAC"],
                           self.test_node_if1["NAME"])

        self.execute_cli_create_cmd(self.ms_node, if_url, "eth", eth_props)

        # node2 eth
        if_url = node_urls[1] + "/network_interfaces/if_8305"
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

    @attr('all', 'revert', 'story8305', 'story8305_tc01')
    def test_01_p_create_update_remove_nameserver_prop(self):
        """
        @tms_id: litpcds_8305_tc01
        @tms_requirements_id: LITPCDS-8305
        @tms_title: Creates, updates and removes nameserver_property
        @tms_description: Creates a DHCP service with the nameservers property
        set. It then updates and removes the property.
        @tms_test_steps:
            @step: Create a dhcp service with nameservers options specified
            and with the values in priority order.
            @result: Items created
            @step: Inherit dhcp service to both peer nodes node1 & node2
            @result: dhcp-service successfully inherited to peer nodes
            @step: Create and run plan
            @result: Plan execution is successful.
            @step: Check file dhcpd.conf exists and the contents of the file
            @result: File exists and contents are as expected
            @step: Update the nameservers property, adding a new ipv4 address
            @result: Item is updated
            @step: Create and run plan
            @result: Plan execution is successful.
            @step: Check file dhcpd.conf exists and the contents of the file
            @result: File exists and contents are as expected
            @step: Update the nameserver property, removing one of the ipv4
            addresses
            @result: Item is updated
            @step: Create and run plan
            @result: Plan execution is successful.
            @step:  Delete the nameservers property
            @result: Item deleted.
            @step: Check file dhcpd.conf exists and the contents of the file
            @result: File exists and contents are as expected
        @tms_test_precondition: N/A
        @tms_execution_type: Automated
        """

        self.create_test_network_and_interfaces()
        node_urls = self.find(self.ms_node, "/deployments", "node")

        #create dhcp service
        base_url = "/software/services"
        nameservers = "20.20.20.21,10.100.100.2"
        service_props = "service_name=dhcp_8305 \
                         nameservers={0}".format(nameservers)
        service_url = base_url + "/s8305"
        subnet_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s8305"
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
        node1_dhcp_url = node_urls[0] + "/services/s8305"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url)

        node2_dhcp_url = node_urls[1] + "/services/s8305"
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
        # dhcpd.conf path
        dhcpd_conf = "{0}/dhcpd.conf".format(test_constants.
                                             DHCPD_CONF_DIR)

        #check .conf file exists
        for node_url in node_urls:
            node_fname = self.get_node_filename_from_url(self.ms_node,
                                                         node_url)
            std_out = self.get_file_contents(node_fname, dhcpd_conf)

            expected = \
                "option domain-name-servers 20.20.20.21, 10.100.100.2;"
            self.assertTrue(self.is_text_in_list(expected, std_out))

        #Update the nameserver property, adding a new ipv4 address
        nameservers = "20.20.20.21,10.10.10.55,10.100.100.2"
        update_props = "nameservers={0}".format(nameservers)

        self.execute_cli_update_cmd(self.ms_node, service_url, update_props)

        # create plan
        self.execute_cli_createplan_cmd(self.ms_node)
        # run plan
        self.execute_cli_runplan_cmd(self.ms_node)
        self.assertTrue(self.wait_for_plan_state(self.ms_node,
                                                 test_constants.PLAN_COMPLETE))

        #check .conf file exists
        for node_url in node_urls:
            node_fname = self.get_node_filename_from_url(self.ms_node,
                                                         node_url)
            std_out = self.get_file_contents(node_fname, dhcpd_conf)

            expected = \
                "option domain-name-servers 20.20.20.21, 10.10.10.55, " + \
                "10.100.100.2;"
            self.assertTrue(self.is_text_in_list(expected, std_out))

        #Update the nameserver property, removing one of the ipv4 addresses
        nameservers = "20.20.20.21,10.10.10.55"
        update_props = "nameservers={0}".format(nameservers)

        self.execute_cli_update_cmd(self.ms_node, service_url, update_props)

        # create plan
        self.execute_cli_createplan_cmd(self.ms_node)
        # run plan
        self.execute_cli_runplan_cmd(self.ms_node)
        self.assertTrue(self.wait_for_plan_state(self.ms_node,
                                                 test_constants.PLAN_COMPLETE))

        #check .conf file exists
        for node_url in node_urls:
            node_fname = self.get_node_filename_from_url(self.ms_node,
                                                         node_url)
            std_out = self.get_file_contents(node_fname, dhcpd_conf)

            expected = \
                "option domain-name-servers 20.20.20.21, 10.10.10.55;"
            self.assertTrue(self.is_text_in_list(expected, std_out))

        #Delete the nameserver property
        self.execute_cli_update_cmd(self.ms_node, service_url,
                                    "nameservers", action_del=True)

        # create plan
        self.execute_cli_createplan_cmd(self.ms_node)
        # run plan
        self.execute_cli_runplan_cmd(self.ms_node)
        self.assertTrue(self.wait_for_plan_state(self.ms_node,
                                                 test_constants.PLAN_COMPLETE))

        #check .conf file exists
        for node_url in node_urls:
            node_fname = self.get_node_filename_from_url(self.ms_node,
                                                         node_url)
            std_out = self.get_file_contents(node_fname, dhcpd_conf)

            expected = "option domain-name-servers"
            self.assertFalse(self.is_text_in_list(expected, std_out))

    @attr('all', 'revert', 'story8305', 'story8305_tc02')
    def test_02_n_validate_nameserver_properties(self):
        """
        @tms_id: litpcds_8305_tc02
        @tms_requirements_id: LITPCDS-8305
        @tms_title: Validate values assigned to nameservers
        @tms_description: Verify ValidationErrors are thrown when a not
        permitted value is given to nameservers.
        @tms_test_steps:
            @step: Create a dhcp-service item using a list of four
            nameservers(where a max of 3 is allowed)
            @result: A ValidationError is thrown with the message A maximum
            of 3 values for the "nameservers" property can be specified
            @step: Create a dhcp service using a non-ipv4 value for nameservers
            @result: A ValidationError is thrown with the message
            "nameservers" must be a IPv4 address or a comma-separated list of
            valid IPv4 addresses
            @step: Create a dhcp service with an invalid ipv4 address
            @result: A ValidationError is thrown with the message
            "nameservers" must be a IPv4 address or a comma-separated list of
            valid IPv4 addresses
            @step: Create a dhcp service using duplicate ipv4addresses in
            nameservers
            @result: A ValidationError is thrown with the message Duplicate
            IP address(es) detected: "10.10.10.10"
            @step: Create a dhcp service using a list of ipv4 addresses
            separated by a space
            @result: A ValidationError is thrown with the message
            "nameservers" must be a IPv4 address or a comma-separated list of
            valid IPv4 addresses
            @step: Create a dhcp service using a list of ipv4 addresses
            separated by a character other than a comma
            @result: A ValidationError is thrown with the message
            "nameservers" must be a IPv4 address or a comma-separated list of
            valid IPv4 addresses
            @step: Create a dhcp service using a value that is not a digit as
            the first value
            @result: A ValidationError is thrown with the message
            "nameservers" must be a IPv4 address or a comma-separated list of
            valid IPv4 addresses
            @step: Create a dhcp service with a mixture of this
            invalid scenarios: duplicate values, invalid ipv4adress and a list
            of four as opposed to three
            @result: A ValidationError is thrown with the message Duplicate
            IP address(es) detected: "10.10.10.17"  A maximum of 3 values for
            the "nameservers" property can be specified.
        @tms_test_precondition: N/A
        @tms_execution_type: Automated
        """

        base_url = "/software/services"
        service_url = base_url + "/s8305"
        service_name = "service_name=dhcp_8305"
        service_props = []
        error_msgs = []

        std_msg = 'ValidationError in property: "nameservers"'
        msg1 = '"nameservers" must be a IPv4 address or a ' + \
               'comma-separated list of valid IPv4 addresses'
        msg2 = 'Duplicate IP address(es) detected: "10.10.10.10"'
        msg3 = 'A maximum of 3 values for the "nameservers" property ' + \
               'can be specified'
        msg4 = 'Duplicate IP address(es) detected: "10.10.10.17"' + \
               ' A maximum of 3 values for the "nameservers"' + \
               ' property can be specified.'

        val1 = "20.20.20.21"
        val2 = "10.100.100.2"
        val3 = "10.10.10.17"
        val4 = "20.100.100.2"

        service_props.append("{0} nameservers={1},{2},{3},{4}".\
                        format(service_name, val1, val2, val3, val4))
        error_msgs.append(msg3)

        service_props.append("{0} nameservers='abc'".\
                                    format(service_name))
        error_msgs.append(msg1)

        service_props.append("{0} nameservers='10.10.10.256'".\
                                                        format(service_name))
        error_msgs.append(msg1)

        service_props.append("{0} nameservers='10.10.10.10,10.10.10.10'".\
                                                        format(service_name))
        error_msgs.append(msg2)

        service_props.append("{0} nameservers='20.20.20.21, 10.100.100.2'".\
                                                        format(service_name))
        error_msgs.append(msg1)

        service_props.append("{0} nameservers='20.20.20.21-10.100.100.2'".\
                                                        format(service_name))
        error_msgs.append(msg1)

        service_props.append("{0} nameservers=' ,10.100.100.2'".\
                                                        format(service_name))
        error_msgs.append(msg1)

        service_props.append("{0} nameservers=' '".\
                                                        format(service_name))
        error_msgs.append(msg1)

        service_props.append("{0} nameservers={1},{2},{3},{3}".\
                        format(service_name, val1, val2, val3, val4))
        error_msgs.append(msg4)

        index = 0
        for prop in service_props:
            _, std_err, _ = self.execute_cli_create_cmd(self.ms_node, \
                service_url, "dhcp-service", prop, expect_positive=False)
            self.assertTrue(self.is_text_in_list(std_msg, std_err))
            self.assertTrue(self.is_text_in_list(error_msgs[index], std_err))
            index += 1

    @attr('all', 'revert', 'story8305', 'story8305_tc03')
    def test_03_p_create_update_remove_search_prop(self):
        """
        @tms_id: litpcds_8305_tc03
        @tms_requirements_id: LITPCDS-8305
        @tms_title: Creates, updates and removes domainsearch property
        @tms_description: Creates a DHCP service with the domainsearch property
        set. It then updates and removes the property.
        @tms_test_steps:
            @step: Create a dhcp service with domainsearch options specified
            and with the values in priority order.
            @result: Items created
            @step: Inherit dhcp service to both peer nodes node1 & node2
            @result: dhcp-service successfully inherited to peer nodes
            @step: Create and run plan
            @result: Plan execution is successful.
            @step: Check file dhcpd.conf exists and the contents of the file
            OR @Step: Check the dhcpd.conf file is configured corretly
            @result: File exists and contents are as expected
            @step: Update the domainsearch property, adding a new address
            @result: Item is updated
            @step: Create and run plan
            @result: Plan execution is successful.
            @step: Check file dhcpd.conf exists and the contents of the file
            @result: File exists and contents are as expected
            @step: Update the domainsearch property, removing one of the
            addresses
            @result: Item is updated
            @step: Create and run plan
            @result: Plan execution is successful.
            @step:  Delete the domainsearch property
            @result: Item deleted.
            @step: Check file dhcpd.conf exists and the contents of the file
            @result: File exists and contents are as expected
        @tms_test_precondition: N/A
        @tms_execution_type: Automated
        """

        self.create_test_network_and_interfaces()
        node_urls = self.find(self.ms_node, "/deployments", "node")

        #create dhcp service
        base_url = "/software/services"
        domains = "foo.com,bar.com"
        nameservers = "nameservers=20.20.20.21,10.100.100.2"
        service_props = "service_name=dhcp_8305 {0} domainsearch={1}".\
                                            format(nameservers, domains)
        service_url = base_url + "/s8305"
        subnet_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s8305"
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
        node1_dhcp_url = node_urls[0] + "/services/s8305"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url)

        node2_dhcp_url = node_urls[1] + "/services/s8305"
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

        # dhcpd.conf path
        dhcpd_conf = "{0}/dhcpd.conf".format(test_constants.
                                             DHCPD_CONF_DIR)

        #check .conf file is configured
        for node_url in node_urls:
            node_fname = self.get_node_filename_from_url(self.ms_node,
                                                         node_url)
            std_out = self.get_file_contents(node_fname, dhcpd_conf)

            expected = \
                'option domain-search "foo.com", "bar.com";'
            self.assertTrue(self.is_text_in_list(expected, std_out))

        #Update the search property, adding a new domain
        search_props = "foo.com,bar.com,foobar.com"
        update_props = "domainsearch={0}".format(search_props)

        self.execute_cli_update_cmd(self.ms_node, service_url, update_props)

        # create plan
        self.execute_cli_createplan_cmd(self.ms_node)
        # run plan
        self.execute_cli_runplan_cmd(self.ms_node)
        self.assertTrue(self.wait_for_plan_state(self.ms_node,
                                                 test_constants.PLAN_COMPLETE))

        #check .conf file is configured
        for node_url in node_urls:
            node_fname = self.get_node_filename_from_url(self.ms_node,
                                                         node_url)
            std_out = self.get_file_contents(node_fname, dhcpd_conf)

            expected = \
                'option domain-search "foo.com", "bar.com", "foobar.com";'
            self.assertTrue(self.is_text_in_list(expected, std_out))

            expected = \
                "option domain-name-servers 20.20.20.21, 10.100.100.2;"
            self.assertTrue(self.is_text_in_list(expected, std_out))

        #Update the domainsearch property, removing one of the ipv4 addresses
        search_props = "foo.com,foobar.com"
        update_props = "domainsearch={0}".format(search_props)

        self.execute_cli_update_cmd(self.ms_node, service_url, update_props)

        # create plan
        self.execute_cli_createplan_cmd(self.ms_node)
        # run plan
        self.execute_cli_runplan_cmd(self.ms_node)
        self.assertTrue(self.wait_for_plan_state(self.ms_node,
                                                 test_constants.PLAN_COMPLETE))
        #check .conf file exists
        for node_url in node_urls:
            node_fname = self.get_node_filename_from_url(self.ms_node,
                                                         node_url)
            std_out = self.get_file_contents(node_fname, dhcpd_conf)

            expected = \
                'option domain-search "foo.com", "foobar.com";'
            self.assertTrue(self.is_text_in_list(expected, std_out))

            expected = \
                "option domain-name-servers 20.20.20.21, 10.100.100.2;"
            self.assertTrue(self.is_text_in_list(expected, std_out))

        #Delete the domainsearch property
        self.execute_cli_update_cmd(self.ms_node, service_url,
                                    "domainsearch", action_del=True)

        # create plan
        self.execute_cli_createplan_cmd(self.ms_node)
        # run plan
        self.execute_cli_runplan_cmd(self.ms_node)
        self.assertTrue(self.wait_for_plan_state(self.ms_node,
                                                 test_constants.PLAN_COMPLETE))

        #check .conf file exists
        for node_url in node_urls:
            node_fname = self.get_node_filename_from_url(self.ms_node,
                                                         node_url)
            std_out = self.get_file_contents(node_fname, dhcpd_conf)

            expected = "option domain-search"
            self.assertFalse(self.is_text_in_list(expected, std_out))

            expected = \
                "option domain-name-servers 20.20.20.21, 10.100.100.2;"
            self.assertTrue(self.is_text_in_list(expected, std_out))

    @attr('all', 'revert', 'story8305', 'story8305_tc04')
    def test_04_n_validate_domain_search_prop(self):
        """
        @tms_id: litpcds_8305_tc04
        @tms_requirements_id: LITPCDS-8305
        @tms_title: Validate the domainsearch property
        @tms_description:  Verify ValidationErrors are thrown when a not
        permitted value is given to domainsearch
        @tms_test_steps:
            @step: Create a dhcp service with the domainsearch with a list of
            seven domains(max six allowed)
            @result: A ValidationError is thrown with the message A maximum
            of 6 values for the "domainsearch" property can be specified
            @step: Create a dhcp service with the domainsearch with a domain
            list containing more than 256 characters
            @result: A ValidationError is thrown with the message The value
            of the "domainsearch" property cannot exceed 256 characters
            @step: Create a dhcp service with the domainsearch without a
            nameservers property
            @result: A ValidationError is thrown with the message The
            property "nameservers" must be specified if a "domainsearch" value
            is provided
            @step: Create a dhcp service with the domainsearch property with
            duplicate values
            @result: A ValidationError is thrown with the message Duplicate
            domainsearch values detected: "foo.com"
            @step: Create a dhcp service with a mixture of this invalid
            scenarios
            @result: A ValidationError is thrown with the message Duplicate
            domainsearch values detected: "foo.com" A maximum of 6 values for
            the "domainsearch" property can be specified.  The value of the
            "domainsearch" property cannot exceed 256 characters.
        @tms_test_precondition: N/A
        @tms_execution_type: Automated
        """

        base_url = "/software/services"
        service_url = base_url + "/s8305"
        service_name = "service_name=dhcp_8305"
        nameservers = "nameservers=20.20.20.21,10.100.100.2"
        service_props = []
        error_msgs = []

        std_msg = 'ValidationError in property:'
        msg1 = 'A maximum of 6 values for the "domainsearch" property ' + \
               'can be specified'
        msg2 = 'The value of the "domainsearch" property cannot exceed ' + \
               '256 characters'
        msg3 = 'The property "nameservers" must be specified if ' + \
               'a "domainsearch" value is provided'
        msg4 = 'Duplicate domainsearch values detected: "foo.com"'
        msg5 = 'Duplicate domainsearch values detected: "foo.com"' + \
               ' A maximum of 6 values for the "domainsearch" property' + \
               ' can be specified.  The value of the "domainsearch"' + \
               ' property cannot exceed 256 characters.'

        val1 = 'foo.com'
        val2 = 'bar.com'
        val3 = 'foobar.com'
        val4 = 'aaa.com'
        val5 = 'bbb.com'
        val6 = 'ddd.com'
        val7 = 'eee.com'

        invalid1 = "foobarfoobarfoobarfoobarfoobarfoobarfoobarfoobar" + \
                 "foobarfoobarfoobarfoobarfoobarfoobarfoobarfoobarfoobar" + \
                 "foobarfoobarfoobar.com"

        invalid2 = "abcbarfoobarfoobarfoobarfoobarfoobarfoobarfoobar" + \
                 "foobarfoobarfoobarfoobarfoobarfoobarfoobarfoobarfoobar" + \
                 "foobarfoobarfoobarfoobarfoobar.com"

        #Specify a list of seven domains(max of six is allowed)
        service_props.append( \
                "{0} {1} domainsearch='{2},{3},{4},{5},{6},{7},{8}'".\
                 format(service_name, nameservers, val1, val2, \
                 val3, val4, val5, val6, val7))
        error_msgs.append(msg1)

        #Specify a domain list containing more than 256 characters
        service_props.append("{0} {1} domainsearch='{2},{3}'".\
                    format(service_name, nameservers, invalid1, invalid2))
        error_msgs.append(msg2)

        #Specify a domainsearch property without a nameserver property
        service_props.append("{0} domainsearch='{1},{2}'".\
                    format(service_name, val1, val2))
        error_msgs.append(msg3)

        #Specify a domainsearch property with duplicate values
        service_props.append("{0} {1} domainsearch='{2},{3}'".\
                    format(service_name, nameservers, val1, val1))
        error_msgs.append(msg4)

        #Specify a list of seven domains(max of six is allowed)
        service_props.append( \
                "{0} {1} domainsearch='{2},{2},{3},{4},{5},{6},{7}'".\
                 format(service_name, nameservers, val1, val2, \
                 val3, val4, invalid1, invalid2))
        error_msgs.append(msg5)

        index = 0
        for prop in service_props:
            _, std_err, _ = self.execute_cli_create_cmd(self.ms_node, \
                    service_url, "dhcp-service", prop, expect_positive=False)
            self.assertTrue(self.is_text_in_list(std_msg, std_err))
            self.assertTrue(self.is_text_in_list(error_msgs[index], std_err))
            index += 1

    @attr('all', 'revert', 'story8305', 'story8305_tc05')
    def test_05_p_create_service_with_search_nameserver_and_ntp(self):
        """
        @tms_id: litpcds_8305_tc05
        @tms_requirements_id: LITPCDS-8305
        @tms_title: Create DHCP service with nameservers, ntp and search
        properties set.
        @tms_description: creates a DHCP service with the nameserver, ntp and
        the search property set.
        @tms_test_steps:
            @step: Create a dhcp service with the nameserver, ntp and search
            options specified and with the values in priority order.
            @result: dhcp-service created successfully
            @step: Inherit this service to node1 and node2
            @result: dhcp-service inherited to node1 and node2
            @step: Create and run plan
            @result: Plan created and run successfully
            @step: Check that the dhcp.conf file is configured correctly
            @result: dhcp.conf confirmed to match expected output
        @tms_test_precondition: N/A
        @tms_execution_type: Automated
        """

        self.create_test_network_and_interfaces()
        node_urls = self.find(self.ms_node, "/deployments", "node")

        #create dhcp service
        base_url = "/software/services"
        nameservers = "nameservers='20.20.20.21,10.100.100.2'"
        search = "domainsearch='foo.com,bar.com'"
        ntp = "ntpservers='10.44.86.5,10.100.100.2'"
        service_props = "service_name=dhcp_8305 \
                    {0} {1} {2}".format(nameservers, search, ntp)
        service_url = base_url + "/s8305"
        subnet_props = "network_name=test1"
        subnet_url = service_url + "/subnets/s8305"
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
        node1_dhcp_url = node_urls[0] + "/services/s8305"
        self.execute_cli_inherit_cmd(self.ms_node, node1_dhcp_url,
                                     service_url)

        node2_dhcp_url = node_urls[1] + "/services/s8305"
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
        # dhcpd.conf path
        dhcpd_conf = "{0}/dhcpd.conf".format(test_constants.
                                             DHCPD_CONF_DIR)

        #check .conf file exists
        for node_url in node_urls:
            node_fname = self.get_node_filename_from_url(self.ms_node,
                                                         node_url)
            std_out = self.get_file_contents(node_fname, dhcpd_conf)

            expected_ns = \
                "option domain-name-servers 20.20.20.21, 10.100.100.2;"
            expected_search = \
                'option domain-search "foo.com", "bar.com";'
            expected_ntp = \
                'option ntp-servers 10.44.86.5, 10.100.100.2;'
            self.assertTrue(self.is_text_in_list(expected_ns, std_out))
            self.assertTrue(self.is_text_in_list(expected_search, std_out))
            self.assertTrue(self.is_text_in_list(expected_ntp, std_out))
