'''
COPYRIGHT Ericsson 2019
The copyright to the computer program(s) herein is the property of
Ericsson Inc. The programs may be used and/or copied only with written
permission from Ericsson Inc. or in accordance with the terms and
conditions stipulated in the agreement/contract under which the
program(s) have been supplied.

@since:     March 2015
@author:    Carlos Novo, Remy Horton, Philip Daly
@summary:   Integration
            Agile: STORY-8265
'''

from litp_generic_test import GenericTest, attr
import test_constants


class Story8265(GenericTest):
    """
    As a LITP user I want to specify a DHCP service to run
    on a single node so that there is a DHCP service available
    for virtual machines running in the LITP complex
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

        self.node_urls = []
        self.nodes_names = []
        self.networks = []
        self.subnets = []
        self.nodes_free_nics = []
        self.base = '192.169.'
        self.base_v6 = '2001:AAAA:BBBB:'
        self.ipv6_networks = None

        # 1. Call super class setup
        super(Story8265, self).setUp()

        # 2. Set up variables used in the test
        self.ms_node = self.get_management_node_filenames()[0]

        self.node_urls = self.find(self.ms_node, "/deployments", "node")
        self.node_urls.sort()

        for node in self.node_urls:
            self.nodes_names.append(self.get_node_filename_from_url(\
                                         self.ms_node, node))
        self.list_managed_nodes = self.get_managed_node_filenames()
        self.primary_node_url = self.get_node_url_from_filename(
                                self.ms_node, self.list_managed_nodes[0])
        self.secondary_node_url = self.get_node_url_from_filename(
                                  self.ms_node, self.list_managed_nodes[1])

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
        super(Story8265, self).tearDown()

    def create_n_networks_n_interfaces(self, number, version=4):
        """
        Description:
            Litp create n test interfaces and networks per node:
        Actions:
            1. Litp create n test interfaces and networks
                for n dhcp subnets.
        Results:
            litp create command for direct plan task execution
        """

        self.assertTrue(version in [4, 6])

        # GET NETWORKS PATH
        networks_path = self.find(self.ms_node, "/infrastructure",
                                  "network", False)[0]

        # GET NEEDED FREE NICS
        self.nodes_free_nics = []
        for node in [0, 1]:
            self.nodes_free_nics.append(
                self.verify_backup_free_nics(self.ms_node,
                                             self.node_urls[node],
                                             required_free_nics=number))

        # CREATE NEEDED NETWORKS
        prefixes = []
        self.networks = []
        self.subnets = []
        if version == 4:
            mask = "/24"
        else:
            mask = "/64"

        for i in xrange(0, number):

            if version == 4:
                prefix = '{0}{1}'.format(self.base, i + 1)
            else:
                prefix = '{0}{1}{1}{1}{1}'.format(self.base_v6, i + 1)
                subnet = '{0}::{1}'.format(prefix, mask)
                self.subnets.append(subnet)

            prefixes.append(prefix)
            network_name = 'test{0}'.format(i + 1)
            self.networks.append(network_name)

            network_url = networks_path + "/test_network8265{0}".format(i + 1)
            props = "name='{0}'".format(network_name)

            if version == 4:
                props = props + " subnet='{0}.0{1}'".format(prefix, mask)

            self.execute_cli_create_cmd(self.ms_node, network_url,
                                        "network", props)

            for node in [0, 1]:
                # eth i
                if_url = self.node_urls[node] + \
                    "/network_interfaces/if_8265_{0}".format(i + 1)

                if version == 4:
                    ipaddress = "{0}.{1}".format(prefixes[i], 1 + node)
                    address_prop = 'ipaddress'
                else:
                    address_prop = 'ipv6address'
                    ipaddress = "{0}::{1}{2}".format(prefixes[i],
                                              1 + node,
                                              mask)

                eth_props = "macaddress='{0}' device_name='{1}' \
                            network_name='{2}' \
                            {3}='{4}'".\
                            format(self.nodes_free_nics[node][i]["MAC"],
                                   self.nodes_free_nics[node][i]["NAME"],
                                   network_name,
                                   address_prop,
                                   ipaddress)

                self.execute_cli_create_cmd(self.ms_node, if_url,
                                            "eth", eth_props)

                self.add_nic_to_cleanup(self.nodes_names[node],
                                        self.nodes_free_nics[node][i]['NAME'],
                                        flush_ip=True)

        self.ipv6_networks = [p + '::' for p in prefixes]

    def check_dhcpd6_conf_content(self, node_path, dhcpd_conf, role):
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

    def check_dhcpd_conf_content(self, node_path, dhcpd_conf, preference=None,
                                 dhcp_ntp_srv=None, dhcp_name_srv=None):
        """
        Description:
            Checking /etc/sysconfig/dhcpd values after successfull plan.
        Args:
            node_path (list): all nodes to be configured.
            dhcpd_conf (str): path to conf file configured.
            preference (str): spected preference
        Results:
            The errors generated after the validation.
        """

        # check one node
        errors = []
        # CHECK dhcpd.conf FILE CONTENT NODES
        std_out = self.get_file_contents(node_path, dhcpd_conf,
                                         su_root=True)

        # If preference is not specified, then we do not want failover
        # section in the file
        if not preference:
            if self.is_text_in_list("BEGIN DHCP Failover", std_out):
                errors.append('The node dhcp v4 role '
                              'is not correct')
        else:
            if not self.is_text_in_list("{0};".format(preference), std_out):
                errors.append('The node dhcp v4 role '
                              'is not correct')

        if dhcp_ntp_srv:
            if not self.is_text_in_list(
                    "option ntp-servers {0};".format(
                    dhcp_ntp_srv.replace(",", ", ")),
                    std_out
                    ):
                errors.append('The node dhcp v4 ntp-server '
                              'is not correct')
        if dhcp_name_srv:
            if not self.is_text_in_list(
                    "option domain-name-servers {0};".format(
                    dhcp_name_srv.replace(",", ", ")),
                    std_out
                    ):
                errors.append('The node dhcp v4 domain-name-servers '
                              'is not correct')

        return errors

    def check_sysconf_dhcpd_content(self, node_fname, node_ifs, dhcpd_sysconf,
                                    version=4):
        """
        Description:
            Checking /etc/sysconfig/dhcpd[6] values after successfull plan.
        Args:
            node_fname (list): all nodes to be configured.
            node_ifs (list): Used networking adapters.
            dhcpd_sysconf (str): path to dhcpd[6] sysconf file.
        Results:
            The errors generated after the validation.
        """
        self.assertTrue(version in (4, 6))

        errors = []

        std_out = self.get_file_contents(node_fname,
                                         dhcpd_sysconf)

        for iface in node_ifs:
            if not self.is_text_in_list(iface['NAME'], std_out):
                errors.append("The dhcp v{0} server" +
                              " not listening adapter: {1}".
                              format(version, iface['NAME']))

        return errors

    def check_pools_conf_subnet(self, std_out, dhcp_subnets, version=4):
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

        self.assertTrue(version in (4, 6))
        subnet_str = "subnet" if version == 4 else "subnet6"

        errors = []

        for item in dhcp_subnets:
            expected_subnet = "{0} {1}".format(subnet_str, item[0])
            if not self.is_text_in_list(expected_subnet, std_out):
                errors.append(
                    'Incorrect subnet config for {0}'.format(item)
                    )
            self.assertEqual(len(dhcp_subnets),
                             self.count_text_in_list("{0} ".format(subnet_str),
                                                     std_out))
        return errors

    def check_pools_conf_ranges(self, std_out, subnets_ranges, version=4):
        """
        Description:
            Checking /etc/dhcp/dhcpd6.pool values for IP ranges
            after successfull plan.
        Args:
            std_out (list): The content of the file after successfull plan.
            subnet_ranges (list of lists): Used dhcp v6 ranges per subnet.
        Results:
            The errors generated after the validation.
        """

        self.assertTrue(version in (4, 6))
        range_str = "range" if version == 4 else "range6"

        errors = []

        num_ranges = 0
        for subnet in subnets_ranges:
            for ip_range in subnet:
                num_ranges += 1
                if isinstance(ip_range, tuple):
                    range_start, range_end = ip_range
                    expected = "{0} {1} {2};".format(
                        range_str, range_start, range_end
                        )
                else:
                    expected = "{0} {1} {2};".format(
                        range_str, ip_range[0], ip_range[1]
                        )
                if not self.is_text_in_list(expected, std_out):
                    errors.append(
                        'The dhcp v{0} {1} configuration is '\
                        'not correct'.format(version, expected)
                        )
        self.assertEqual(num_ranges,
                         self.count_text_in_list(range_str, std_out))

        return errors

    def check_existents_of_the_confs(self, node_fname, dhcpd_conf,
                                     dhcpd_pools, dhcpd_sysconf,
                                     version=4):
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

        self.assertTrue(version in (4, 6))
        file_name = "dhcpd" if version == 4 else "dhcpd6"

        errors = []
        # check the existence of dhcpd.conf into the node
        if not self.remote_path_exists(node_fname,
                                       dhcpd_conf):
            errors.append("{0}.conf doesn't exist into the node".\
                          format(file_name))
        # check the existence of /etc/sysconfig/dhcpd[6]
        if not self.remote_path_exists(node_fname,
                                       dhcpd_sysconf):
            errors.append("/etc/sysconfig/{0}" +
                          "doesn't exist into the node".format(file_name))

        # check the existence of dhcpd.pools into the nodes
        if not self.remote_path_exists(node_fname,
                                       dhcpd_pools):
            errors.append("{0}.pools" +
                          "doesn't exist into the node".format(file_name))
        # check the existence of /etc/sysconfig/dhcpd[6]
        if not self.remote_path_exists(node_fname,
                                       dhcpd_sysconf):
            errors.append("/etc/sysconfig/{0}" +
                          "doesn't exist into the node".format(file_name))

        # check the existence of dhcpd.pools into the nodes
        if not self.remote_path_exists(node_fname,
                                       dhcpd_pools):
            errors.append("{0}.pools" +
                          "doesn't exist into the node".format(file_name))

        return errors

    def datadriven_verification_check_one_node(self, node, subnets, ranges,
                                               preference,
                                               version=4,
                                               dhcp_ntp_srv=None,
                                               dhcp_name_srv=None
                                               ):
        """
        Description:
            Check system configuration, output of the executed plan.
        Args:
            node (int): index of checked node (0|1|..)
            subnets (list): list of dhcp subnets.
            ranges (list): Used dhcp ranges.
            preference (str): spected preference string.
            version (int): dhcp version (4|6)
        Results:
            stderr of checking configuration
        """

        self.assertTrue(version in [4, 6])
        file_name = "dhcpd" if version == 4 else "dhcpd6"

        node_url = self.node_urls[node]

        errors = []
        # dhcpd.conf path
        dhcpd_conf = "{0}/{1}.conf".format(test_constants.DHCPD_CONF_DIR,
                                           file_name)
        # dhcpd.pools path
        dhcpd_pools = "{0}/{1}.pools".format(test_constants.DHCPD_CONF_DIR,
                                                file_name)
        # dhcpd path
        dhcpd_sysconf = "{0}/{1}".format(test_constants.DHCPD_DHCPDARGS_FILE,
                                         file_name)

        self.log("info", "VERIFYING NODE {0}".format(node_url))
        node_fname = self.get_node_filename_from_url(self.ms_node,
                                                     node_url)
        check_files_existence = \
            self.check_existents_of_the_confs(node_fname, dhcpd_conf,
                                              dhcpd_pools, dhcpd_sysconf,
                                              version=version)
        errors.extend(check_files_existence)
        # CHECK dhcpd.conf FILE CONTENT NODES

        if version == 4:
            check_dhcpd_conf = self.check_dhcpd_conf_content(
                node_fname, dhcpd_conf, preference,
                dhcp_ntp_srv, dhcp_name_srv
                )
        else:
            check_dhcpd_conf = self.check_dhcpd6_conf_content(node_fname,
                                                             dhcpd_conf,
                                                             preference)
        errors.extend(check_dhcpd_conf)

        # CHECK /etc/sysconfig/dhcpd FILE CONTENT NODES
        check_sysconf_dhcpd = self. \
            check_sysconf_dhcpd_content(node_fname,
                                        self.nodes_free_nics[node],
                                        dhcpd_sysconf, version=version)

        errors.extend(check_sysconf_dhcpd)

        # CHECK dhcpd.pools FILE CONTENT NODES
        std_out = self.get_file_contents(node_fname, dhcpd_pools,
                                         su_root=True)
        check_subnet_conf = \
            self.check_pools_conf_subnet(std_out, subnets, version=version)
        errors.extend(check_subnet_conf)

        check_ranges_conf = \
            self.check_pools_conf_ranges(std_out, ranges, version=version)
        errors.extend(check_ranges_conf)

        return errors

    @attr('all', 'revert', 'story8265', 'story8265_tc01')
    def test_01_p_dhcp_single_node(self):
        """
        @tms_id: litpcds_8265_tc01
        @tms_requirements_id: LITPCDS-8265
        @tms_title: Deploy a dhcp service to one single node.
        @tms_description: To ensure that it is possible to deploy a dhcp
        service on a single peer node following cluster initial install
        @tms_test_steps:
                @step: Create three network items with two eths on each network
                @result: Items created.
                @step: Create dhcp service item with valid values in properties
                service_name, nameservers and ntpservers
                @result: Item created.
                @step: Create three child subnets on the dhcp-service
                @result: Items created.
                @step: Create three dhcp ranges below the first subnet, two
                ranges below the second subnet, and a single range below the
                third subnet.
                @result: Items created.
                @step: Inherit the dhcp-service onto node 2.
                @result: Item inherited
                @step: Create and run plan.
                @result: Plan executed successfully.
                @step: Verify that the service is running on node2, serving the
                expected ranges and that the nameservers, search and
                ntpservers properties have been applied
                @result: Service running as expected on node2
                @step: Verify that no listing for the service exists on node 1.
                @result: Nothing on node1 exists for this service
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """

        self.create_n_networks_n_interfaces(3, 4)

        # 1 CREATE SERVICE
        base_url = "/software/services"
        name_srvrs = '4.4.4.4,8.8.8.8'
        ntp_srvrs = 'ntp.server.one,1.1.1.1'
        service_props = "service_name=dhcp_8265 " \
            "nameservers='{0}' " \
            "ntpservers='{1}'".format(name_srvrs, ntp_srvrs)
        service_url = base_url + "/s8265"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp-service", service_props)

        # 2 CREATE SUBNETS
        subnets_urls = []
        for subnet in [1, 2, 3]:
            subnet_url = service_url + "/subnets/s8265{0}".format(subnet)
            subnets_urls.append(subnet_url)
            subnet_props = "network_name=test{0}".format(subnet)
            self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                        "dhcp-subnet", subnet_props)

        # 3 CREATE RANGES
        subnets_ranges = \
                  [[
                    [self.base + '1.10', self.base + '1.20'],
                    [self.base + '1.30', self.base + '1.40'],
                    [self.base + '1.50', self.base + '1.60'],
                  ],
                  [
                    [self.base + '2.10', self.base + '2.20'],
                    [self.base + '2.30', self.base + '2.40'],
                  ],
                  [
                    [self.base + '3.10', self.base + '3.20']
                  ]]

        for subnet, ranges in enumerate(subnets_ranges):
            for i, ips_range in enumerate(ranges):
                start, end = ips_range
                range_props = "start={0} end={1}".format(start, end)
                range_url = subnets_urls[subnet] + '/ranges/r{0}'.format(i + 1)
                self.execute_cli_create_cmd(self.ms_node, range_url,
                                            "dhcp-range", range_props)

        # 4 INHERIT SERVICE ON NODE 2
        node_dhcp_url = self.node_urls[1] + "/services/s8265"
        self.execute_cli_inherit_cmd(self.ms_node, node_dhcp_url,
                                     service_url)

        # 5.1 CREATE PLAN
        self._create_and_run_plan(12)

        # 6.1 CHECK CONFIG FOR NODE 2
        # WE DO NOT CARE ABOUT NODE 1
        std_err = self.datadriven_verification_check_one_node(
            1,
            self.subnets,
            subnets_ranges,
            None,
            4,
            ntp_srvrs,
            name_srvrs
            )

        self.assertEqual([], std_err)

        # 6.2 CHECK PROCESS IS RUNNING ON NODE 2
        cmd = "/bin/ps aux | /bin/grep 'd[h]cpd'"
        _, _, rc = self.run_command(self.nodes_names[1], cmd, su_root=True)
        self.assertEqual(0, rc)

        # 7 CHECK PROCESS IS NOT RUNNING ON NODE 1
        _, _, rc = self.run_command(self.nodes_names[0], cmd, su_root=True)
        self.assertNotEqual(0, rc)

        # CHECK DHCP SERVER IS SET UP TO START ON BOOT FOR NODE 2
        cmd = "/sbin/chkconfig | /bin/grep dhcpd"
        stdout, _, _ = self.run_command(self.nodes_names[1], cmd, su_root=True)
        self.assertTrue(self.count_text_in_list("on", stdout))

        # CHECK DHCP SERVER IS NOT SET UP TO START ON BOOT FOR NODE 1
        stdout, _, _ = self.run_command(self.nodes_names[0], cmd, su_root=True)
        self.assertFalse(self.count_text_in_list("on", stdout))

    @attr('all', 'revert', 'story8265', 'story8265_tc02')
    def test_02_p_dhcp6_single_node(self):
        """
        @tms_id: litpcds_8265_tc02
        @tms_requirements_id: LITPCDS-8265
        @tms_title:  Deploy a dhcp6 service to one single node.
        @tms_description: To ensure that it is possible to deploy a dhcp
        service on a single peer node following cluster initial install.
        @tms_test_steps:
            @step: Create three network items with two eths on each network
            @result: Items created.
            @step: Create a dhcp6-service item with valid values in properties
            service_name, nameservers and ntpservers
            @result: Item created.
            @step: Create three dhcp6 subnets on the dhcp6-service
            @result: Items created.
            @step: Create three dhcp ranges below the first subnet, two ranges
            below the second subnet, and a single range below the third subnet.
            @result: Items created.
            @step: Inherit the dhcp-service onto node 2.
            @result: Item inherited
            @step: Create and run plan.
            @result: Plan executed successfully.
            @step: Verify that the service is running, serving the expected
            ranges, and set to 255 on node 2.
            @result: Service running on node2 as expected.
            @step:  Verify that no listing for the service exists on node 1.
            @result: Service is not running on node1
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """

        self.create_n_networks_n_interfaces(3, 6)

        # 1 CREATE SERVICE
        base_url = "/software/services"
        service_props = "service_name=dhcp_8265 "
        service_url = base_url + "/s8265"

        self.execute_cli_create_cmd(self.ms_node, service_url,
                                    "dhcp6-service", service_props)

        # 2 CREATE SUBNETS
        subnets_urls = []
        for subnet in [1, 2, 3]:
            subnet_url = service_url + "/subnets/s8265{0}".format(subnet)
            subnets_urls.append(subnet_url)
            subnet_props = "network_name=test{0}".format(subnet)
            self.execute_cli_create_cmd(self.ms_node, subnet_url,
                                        "dhcp6-subnet", subnet_props)

        # 3 CREATE RANGES
        subnets_ranges = \
                  [[
                    [self.base_v6 + '1111::100', self.base_v6 + '1111::200'],
                    [self.base_v6 + '1111::300', self.base_v6 + '1111::400'],
                    [self.base_v6 + '1111::500', self.base_v6 + '1111::600'],
                  ],
                  [
                    [self.base_v6 + '2222::100', self.base_v6 + '2222::200'],
                    [self.base_v6 + '2222::300', self.base_v6 + '2222::400'],
                  ],
                  [
                    [self.base_v6 + '3333::100', self.base_v6 + '3333::200']
                  ]]

        for subnet, ranges in enumerate(subnets_ranges):
            for i, ips_range in enumerate(ranges):
                start, end = ips_range
                range_props = "start={0} end={1}".format(start, end)
                range_url = subnets_urls[subnet] + '/ranges/r{0}'.format(i + 1)
                self.execute_cli_create_cmd(self.ms_node, range_url,
                                            "dhcp6-range", range_props)

        # 4 INHERIT SERVICE ON NODE 2
        node_dhcp_url = self.node_urls[1] + "/services/s8265"
        self.execute_cli_inherit_cmd(self.ms_node, node_dhcp_url,
                                     service_url)

        # 5.1 CREATE PLAN
        self._create_and_run_plan(12)

        # 6.1 CHECK CONFIG FOR NODE 2
        # WE DO NOT CARE ABOUT NODE 1
        std_err = self.datadriven_verification_check_one_node(
            1,
            self.subnets,
            subnets_ranges,
            '255',
            6
            )

        self.assertEqual([], std_err)

        # 6.2 CHECK PROCESS IS RUNNING ON NODE 2
        cmd = "/bin/ps aux | /bin/grep 'd[h]cpd -6'"
        _, _, rc = self.run_command(self.nodes_names[1], cmd, su_root=True)
        self.assertEqual(0, rc)

        # 7 CHECK PROCESS IS NOT RUNNING ON NODE 1
        _, _, rc = self.run_command(self.nodes_names[0], cmd, su_root=True)
        self.assertNotEqual(0, rc)

        # CHECK DHCP SERVER IS SET UP TO START ON BOOT FOR NODE 2
        cmd = "/sbin/chkconfig | /bin/grep dhcpd6"
        stdout, _, _ = self.run_command(self.nodes_names[1], cmd, su_root=True)
        self.assertTrue(self.count_text_in_list("on", stdout))

        # CHECK DHCP SERVER IS NOT SET UP TO START ON BOOT FOR NODE 1
        stdout, _, _ = self.run_command(self.nodes_names[0], cmd, su_root=True)
        self.assertFalse(self.count_text_in_list("on", stdout))

    def _create_and_run_plan(self, timeout_delay=10):
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

    @attr('all', 'revert', 'story8265', 'story8265_tc15')
    def test_15_p_dhcp_1_node_update_sub_and_rnge_and_srvs_expan(self):
        """
        @tms_id: litpcds_8265_tc15
        @tms_requirements_id: LITPCDS-8265
        @tms_title:  Deploy a dhcp-service updating the range and subnet
        @tms_description: To ensure that it is possible to update existing
        ranges, add ranges to an existing subnet, add new subnets on a dhcp
        service deployed on a single node, and to also expand the service to
        run on two nodes.
        @tms_test_steps:
            @step: Create five network items with two eths on each network
            @result: Items created.
            @step: Create a dhcp4-service item with valid values in properties
            service_name, nameservers, ntpservers and domainsearch
            @result: Item created.
            @step: Create three dhcp4 subnets on the dhcp4-service
            @result: Items created.
            @step: Create three dhcp ranges below the first subnet,
                   two ranges below the second subnet, and a single
                   range below the third subnet.
            @result: Items created.
            @step: Inherit the dhcp-service onto node 2 as non primary
            @result: Item inherited
            @step: Create and run plan.
            @result: Plan executed successfully.
            @step: Update two of the existing ranges below the first subnet
                   to use new values.
            @result: Items updated
            @step: Create two new ranges below the first subnet
            @result: Items created
            @step: Create three new ranges below the second subnet.
            @result: Items created
            @step: Create two new subnets with three ranges below the first
                   new subnet, a one range below the second new subnet
            @result: Items created
            @step: Inherit the service to node 2 as primary and to node1 as
                   non-primary
            @result: Items inherited.
            @step:  Create and run plan.
            @result: Plan executed successfully.
            @step: Verify that the service is running, serving the expected
               ranges, and that the nameservers, search and
               ntpservers properties have been applied on both peer nodes.
                Ensure node2 has been set to primary and node1 has been
                set to non-primary, and dhcp-failover information has
                been added.
            @result: Service running, information
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        self.create_n_networks_n_interfaces(5)

        base_path = '/software/services'
        base_ipv4 = self.base
        dhcp_svc_name = 'dhcp4'
        dhcp_ntp_srv = '192.168.0.251'
        dhcp_name_srv = '192.168.0.252'
        dhcp_search = 'example.com'

        dhcp_subnet_names = ['s1', 's2', 's3']
        dhcp_ranges = [
            [
                (base_ipv4 + '1.100', base_ipv4 + '1.120'),
                (base_ipv4 + '1.121', base_ipv4 + '1.140'),
                (base_ipv4 + '1.141', base_ipv4 + '1.150')
            ],
            [
                (base_ipv4 + '2.100', base_ipv4 + '2.120'),
                (base_ipv4 + '2.121', base_ipv4 + '2.140'),
            ],
            [
                (base_ipv4 + '3.100', base_ipv4 + '3.120')
            ]
        ]
        dhcp_range_updates_to_subnet1 = [
            (base_ipv4 + '1.200', base_ipv4 + '1.219'),
            (base_ipv4 + '1.221', base_ipv4 + '1.229')
            ]
        dhcp_range_additions = [
            [
                (base_ipv4 + '1.151', base_ipv4 + '1.154'),
                (base_ipv4 + '1.156', base_ipv4 + '1.159')
            ],
            [
                (base_ipv4 + '2.141', base_ipv4 + '2.145'),
                (base_ipv4 + '2.151', base_ipv4 + '2.155'),
                (base_ipv4 + '2.161', base_ipv4 + '2.165')
            ],
            [
                # Intentionally empty..
            ]
        ]
        dhcp_more_subnet_names = ['s4', 's5']
        dhcp_more_ranges = [
            [
                (base_ipv4 + '4.10', base_ipv4 + '4.20'),
                (base_ipv4 + '4.21', base_ipv4 + '4.40'),
                (base_ipv4 + '4.41', base_ipv4 + '4.60')
            ],
            [
                (base_ipv4 + '5.10', base_ipv4 + '5.20')
            ]
        ]

        # Create svc
        self.execute_cli_create_cmd(
            self.ms_node,
            '{0}/{1}'.format(base_path, dhcp_svc_name),
            'dhcp-service',
            'service_name={0} nameservers={1} '
            'ntpservers={2} domainsearch={3}'.format(
                dhcp_svc_name, dhcp_name_srv, dhcp_ntp_srv, dhcp_search
                )
            )

        # Create subnets & ranges
        for sub_idx, sub_name in enumerate(dhcp_subnet_names):
            sub_path = '{0}/{1}/subnets/{2}'.format(
                base_path, dhcp_svc_name, sub_name
                )
            self.execute_cli_create_cmd(
                self.ms_node, sub_path, 'dhcp-subnet',
                'network_name=' + self.networks[sub_idx]
                )
            sub_range = dhcp_ranges[sub_idx]
            for idx, item in enumerate(sub_range):
                range_start, range_end = item
                self.execute_cli_create_cmd(
                    self.ms_node,
                    '{0}/ranges/r{1}'.format(sub_path, idx),
                    'dhcp-range',
                    'start={0} end={1}'.format(range_start, range_end)
                    )

        # Add inherit
        self.execute_cli_inherit_cmd(
            self.ms_node,
            '{0}/services/{1}'.format(self.node_urls[0], dhcp_svc_name),
            '{0}/{1}'.format(base_path, dhcp_svc_name),
            'primary=false'
            )

        self._create_and_run_plan()

        # 1.1 Update 2x ranges in subnet 1
        sub_path = '{0}/{1}/subnets/s1'.format(base_path, dhcp_svc_name)
        for idx, item in enumerate(dhcp_range_updates_to_subnet1):
            range_start, range_end = item
            self.execute_cli_update_cmd(
                self.ms_node,
                '{0}/ranges/r{1}'.format(sub_path, idx),
                'start={0} end={1}'.format(range_start, range_end)
                )

        # 2.1 Add extra ranges
        for sub_idx, sub_name in enumerate(dhcp_subnet_names):
            sub_path = '{0}/{1}/subnets/{2}'.format(
                base_path, dhcp_svc_name, sub_name
                )
            for idx, item in enumerate(dhcp_range_additions[sub_idx]):
                range_start, range_end = item
                self.execute_cli_create_cmd(
                    self.ms_node,
                    '{0}/ranges/r{1}'.format(sub_path, idx + 3),
                    'dhcp-range',
                    'start={0} end={1}'.format(range_start, range_end)
                    )

        # 3.1 4.1 Create (more) subnets & ranges
        for sub_idx, sub_name in enumerate(dhcp_more_subnet_names):
            sub_path = '{0}/{1}/subnets/{2}'.format(
                base_path, dhcp_svc_name, sub_name
                )
            self.execute_cli_create_cmd(
                self.ms_node, sub_path, 'dhcp-subnet',
                'network_name=' + self.networks[sub_idx + 3]
                )
            sub_range = dhcp_more_ranges[sub_idx]
            for idx, item in enumerate(sub_range):
                range_start, range_end = item
                self.execute_cli_create_cmd(
                    self.ms_node,
                    '{0}/ranges/r{1}'.format(sub_path, idx),
                    'dhcp-range',
                    'start={0} end={1}'.format(range_start, range_end)
                    )

        # 5.1 Add 2nd server and make it primary. Relegate existing to 2nd-ary
        self.execute_cli_inherit_cmd(
            self.ms_node,
            '{0}/services/{1}'.format(self.node_urls[1], dhcp_svc_name),
            '{0}/{1}'.format(base_path, dhcp_svc_name),
            'primary=true'
            )
        # 6.1
        self.execute_cli_update_cmd(
            self.ms_node,
            '{0}/services/{1}'.format(self.node_urls[0], dhcp_svc_name),
            'primary=false'
            )
        # 7.1
        self._create_and_run_plan()

        # 8.1
        expected_ranges = dhcp_range_updates_to_subnet1
        expected_ranges.append(dhcp_ranges[0][2])
        for range_list in dhcp_ranges[1:]:
            expected_ranges.extend(range_list)
        for range_list in dhcp_more_ranges:
            expected_ranges.extend(range_list)
        for range_list in dhcp_range_additions:
            expected_ranges.extend(range_list)
        self.datadriven_verification_check_one_node(
            0, self.subnets, [expected_ranges], 'secondary', 4,
            dhcp_ntp_srv, dhcp_name_srv
            )
        self.datadriven_verification_check_one_node(
            1, self.subnets, [expected_ranges], 'primary', 4,
            dhcp_ntp_srv, dhcp_name_srv
            )

    @attr('all', 'revert', 'story8265', 'story8265_tc16')
    def test_16_p_dhcp_1_node_update_subn_and_rnge_and_srvs_expan(self):
        """
        @tms_id: litpcds_8265_tc16
        @tms_requirements_id: LITPCDS-8265
        @tms_title: Test that dhcp v6 service can have ranges modified, have
        new ranges added, and have new subnets added
        @tms_description: To ensure that it is possible to update existing
        ranges, add ranges to an existing subnet, add new subnets on a dhcp
        service deployed on a single node, and to also expand the service to
        run on two nodes.
        @tms_test_steps:
            @step: Create five network items with two eths on each network
            @result: Items created.
            @step: Create a dhcp6-service item with valid values in property
            service_name
            @result: Item created.
            @step: Create three dhcp6 subnets on the dhcp6-service
            @result: Items created.
            @step: Create three dhcpd6 ranges below the first subnet, two
            ranges below the second subnet, and a single range below the third
            subnet.
            @result: Items created.
            @step: Inherit the dhcp6-service onto node 1 as non primary
            @result: Item inherited
            @step: Create and run plan.
            @result: Plan executed successfully.
            @step:Update two of the existing ranges below the first subnet to
            use new values.
            @result: Items updated
            @step:Create two new ranges below the first subnet
            @result: Items created
            @step: Create three new ranges below the second subnet.
            @result: Items created
            @step: Create two new subnets.
            @result: Items created
            @step: Create three ranges below the first new subnet and one
            range below the second new subnet.
            @result: Four ranges created
            @step: Inherit the service to node1 as non-primary
            @result: Items inherited.
            @step: Create and run plan.
            @result: Plan executed successfully.
            @step: Verify that the service is running, serving the expected
            ranges, and that the nameservers, search and ntpservers
            properties have been applied, set to primary on node 2, and
            failover information added.
            @result: Service verified to be running in expected state
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        self.create_n_networks_n_interfaces(5, version=6)

        base_path = '/software/services'
        dhcp_svc_name = 'dhcp6'

        dhcp_subnet_names = ['s1', 's2', 's3']
        dhcp_ranges = [
            [
                (self.ipv6_networks[0] + '21', self.ipv6_networks[0] + '29'),
                (self.ipv6_networks[0] + '31', self.ipv6_networks[0] + '39'),
                (self.ipv6_networks[0] + '41', self.ipv6_networks[0] + '49')
            ],
            [
                (self.ipv6_networks[1] + '21', self.ipv6_networks[1] + '29'),
                (self.ipv6_networks[1] + '31', self.ipv6_networks[1] + '39')
            ],
            [
                (self.ipv6_networks[2] + '21', self.ipv6_networks[2] + '29')
            ],
        ]
        dhcp_range_updates_to_subnet1 = [
                (self.ipv6_networks[0] + '22', self.ipv6_networks[0] + '28'),
                (self.ipv6_networks[0] + '32', self.ipv6_networks[0] + '38'),
            ]
        dhcp_range_additions = [
            [
                (self.ipv6_networks[0] + '51', self.ipv6_networks[0] + '59'),
                (self.ipv6_networks[0] + '61', self.ipv6_networks[0] + '69'),
            ],
            [
                (self.ipv6_networks[1] + '51', self.ipv6_networks[1] + '59'),
                (self.ipv6_networks[1] + '61', self.ipv6_networks[1] + '69'),
                (self.ipv6_networks[1] + '71', self.ipv6_networks[1] + '79')
            ],
            [
                # Intentionally empty..
            ]
        ]
        dhcp_more_subnet_names = ['s4', 's5']
        dhcp_more_ranges = [
            [
                (self.ipv6_networks[3] + '21', self.ipv6_networks[3] + '29'),
                (self.ipv6_networks[3] + '31', self.ipv6_networks[3] + '39'),
                (self.ipv6_networks[3] + '41', self.ipv6_networks[3] + '49')
            ],
            [
                (self.ipv6_networks[4] + '21', self.ipv6_networks[4] + '29'),
            ]
        ]

        # Create svc
        self.execute_cli_create_cmd(
            self.ms_node,
            '{0}/{1}'.format(base_path, dhcp_svc_name),
            'dhcp6-service',
            'service_name={0}'.format(dhcp_svc_name)
            )

        # Create subnets & ranges
        for sub_idx, sub_name in enumerate(dhcp_subnet_names):
            sub_path = '{0}/{1}/subnets/{2}'.format(
                base_path, dhcp_svc_name, sub_name
                )
            self.execute_cli_create_cmd(
                self.ms_node, sub_path, 'dhcp6-subnet',
                'network_name=' + self.networks[sub_idx]
                )
            sub_range = dhcp_ranges[sub_idx]
            for idx, item in enumerate(sub_range):
                range_start, range_end = item
                self.execute_cli_create_cmd(
                    self.ms_node,
                    '{0}/ranges/r{1}'.format(sub_path, idx),
                    'dhcp6-range',
                    'start={0} end={1}'.format(range_start, range_end)
                    )

        # Add inherit
        self.execute_cli_inherit_cmd(
            self.ms_node,
            '{0}/services/{1}'.format(self.node_urls[0], dhcp_svc_name),
            '{0}/{1}'.format(base_path, dhcp_svc_name),
            'primary=false'
            )

        self._create_and_run_plan()

        # 1.1 Update 2x ranges in subnet 1
        sub_path = '{0}/{1}/subnets/s1'.format(base_path, dhcp_svc_name)
        for idx, item in enumerate(dhcp_range_updates_to_subnet1):
            range_start, range_end = item
            self.execute_cli_update_cmd(
                self.ms_node,
                '{0}/ranges/r{1}'.format(sub_path, idx),
                'start={0} end={1}'.format(range_start, range_end)
                )

        # 2.1 Add extra ranges
        for sub_idx, sub_name in enumerate(dhcp_subnet_names):
            sub_path = '{0}/{1}/subnets/{2}'.format(
                base_path, dhcp_svc_name, sub_name
                )
            for idx, item in enumerate(dhcp_range_additions[sub_idx]):
                range_start, range_end = item
                self.execute_cli_create_cmd(
                    self.ms_node,
                    '{0}/ranges/r{1}'.format(sub_path, idx + 3),
                    'dhcp6-range',
                    'start={0} end={1}'.format(range_start, range_end)
                    )

        # 3.1 4.1 Create (more) subnets & ranges
        for sub_idx, sub_name in enumerate(dhcp_more_subnet_names):
            sub_path = '{0}/{1}/subnets/{2}'.format(
                base_path, dhcp_svc_name, sub_name
                )
            self.execute_cli_create_cmd(
                self.ms_node, sub_path, 'dhcp6-subnet',
                'network_name=' + self.networks[sub_idx + 3]
                )
            sub_range = dhcp_more_ranges[sub_idx]
            for idx, item in enumerate(sub_range):
                range_start, range_end = item
                self.execute_cli_create_cmd(
                    self.ms_node,
                    '{0}/ranges/r{1}'.format(sub_path, idx),
                    'dhcp6-range',
                    'start={0} end={1}'.format(range_start, range_end)
                    )

        # 5.1 Add 2nd server and make it primary. Relegate existing to 2nd-ary
        self.execute_cli_inherit_cmd(
            self.ms_node,
            '{0}/services/{1}'.format(self.node_urls[1], dhcp_svc_name),
            '{0}/{1}'.format(base_path, dhcp_svc_name),
            'primary=true'
            )
        # 6.1
        self.execute_cli_update_cmd(
            self.ms_node,
            '{0}/services/{1}'.format(self.node_urls[0], dhcp_svc_name),
            'primary=false'
            )
        # 7.1
        self._create_and_run_plan()

        # 8.1
        # dhcp_range_updates_to_subnet1 updates the first two of
        # the three ranges in dhcp_ranges[0]..
        expected_ranges = dhcp_range_updates_to_subnet1
        expected_ranges.append(dhcp_ranges[0][2])
        for range_list in dhcp_ranges[1:]:
            expected_ranges.extend(range_list)
        for range_list in dhcp_more_ranges:
            expected_ranges.extend(range_list)
        for range_list in dhcp_range_additions:
            expected_ranges.extend(range_list)
        self.datadriven_verification_check_one_node(
            0, self.subnets, [expected_ranges], 1, 6
            )
        self.datadriven_verification_check_one_node(
            1, self.subnets, [expected_ranges], 255, 6
            )

    @attr('all', 'revert', 'story8265', 'story8265_tc17')
    def test_17_p_dhcp_two_node_update_range_and_srvs_contraction(self):
        """
        @tms_id: litpcds_8265_tc17
        @tms_requirements_id: LITPCDS-8265
        @tms_title: Update ranges to an existing range via its inherited object
        @tms_description: To ensure that it is possible to update ranges to an
        existing range via its inherited object, while simultaneously
        contracting the service to be deployed only on a single node.
        @tms_test_steps:
            @step: Create five network items with two eths on each network
            @result: Items created.
            @step: Create a dhcp4-service
            @result: Item created.
            @step: Create five ranges below the first subnet
            @result: Item created.
            @step: Create five ranges below the second subnet
            @result: Item created.
            @step: Create a single range below the third subnet
            @result: Item created.
            @step: Create three ranges below the fourth subnet
            @result: Item created.
            @step: Create two ranges below the firth subnet
            @result: Item created.
            @step: Inherit the dhcp4-service onto node1 as non-primary and
            node2 as primary
            @result: Items inherited
            @step: Create and run plan.
            @result: Plan executed successfully.
            @step:Update two of the existing ranges below the first subnet to
            use new values.
            @result: Items updated
            @step: Remove the service under node 2.
            @result: Service on node 2 removed
            @step: Create and run plan.
            @result: Plan created and run successfully
            @step: Verify that the service is running
            @result: Service verified to be running
            @step: Verify that the service is serving the expected ranges
            @result: Service verified to be serving expected ranges
            @step: Verify that properties (nameservers, search and
            ntpservers) have been applied successfully
            @result: Properties verified to have been applied
            @step: Remove failover & primary/seconday information.
            @result: failover & primary/seconday information removed
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        # 1.0 CREATE CONFIGURATION FOR SUBSEQUENT TEST.
        self.create_n_networks_n_interfaces(5)

        base_path = '/software/services'
        base_ipv4 = self.base
        dhcp_svc_name = 'dhcp4'
        dhcp_ntp_srv = '192.168.0.251'
        dhcp_name_srv = '192.168.0.252'
        dhcp_search = 'example.com'

        dhcp_subnet_names = ['s1', 's2', 's3', 's4', 's5']
        dhcp_ranges = [
            [
                (base_ipv4 + '1.200', base_ipv4 + '1.219'),
                (base_ipv4 + '1.221', base_ipv4 + '1.229'),
                (base_ipv4 + '1.141', base_ipv4 + '1.150'),
                (base_ipv4 + '1.151', base_ipv4 + '1.154'),
                (base_ipv4 + '1.156', base_ipv4 + '1.159')
            ],
            [
                (base_ipv4 + '2.100', base_ipv4 + '2.120'),
                (base_ipv4 + '2.121', base_ipv4 + '2.140'),
                (base_ipv4 + '2.141', base_ipv4 + '2.145'),
                (base_ipv4 + '2.151', base_ipv4 + '2.155'),
                (base_ipv4 + '2.161', base_ipv4 + '2.165')
            ],
            [
                (base_ipv4 + '3.100', base_ipv4 + '3.120')
            ],
            [
                (base_ipv4 + '4.10', base_ipv4 + '4.20'),
                (base_ipv4 + '4.21', base_ipv4 + '4.40'),
                (base_ipv4 + '4.41', base_ipv4 + '4.60')
            ],
            [
                (base_ipv4 + '5.10', base_ipv4 + '5.20')
            ]
        ]

        # 0.1 Create svc
        self.execute_cli_create_cmd(
            self.ms_node,
            '{0}/{1}'.format(base_path, dhcp_svc_name),
            'dhcp-service',
            'service_name={0} nameservers={1} '
            'ntpservers={2} domainsearch={3}'.format(
                dhcp_svc_name, dhcp_name_srv, dhcp_ntp_srv, dhcp_search
                )
            )

        # 0.2 Create subnets & ranges
        for sub_idx, sub_name in enumerate(dhcp_subnet_names):
            sub_path = '{0}/{1}/subnets/{2}'.format(
                base_path, dhcp_svc_name, sub_name
                )
            self.execute_cli_create_cmd(
                self.ms_node, sub_path, 'dhcp-subnet',
                'network_name=' + self.networks[sub_idx]
                )
            sub_range = dhcp_ranges[sub_idx]
            for idx, item in enumerate(sub_range):
                range_start, range_end = item
                self.execute_cli_create_cmd(
                    self.ms_node,
                    '{0}/ranges/r{1}'.format(sub_path, idx),
                    'dhcp-range',
                    'start={0} end={1}'.format(range_start, range_end)
                    )

        # 0.3 Add inherit
        self.execute_cli_inherit_cmd(
            self.ms_node,
            '{0}/services/{1}'.format(self.node_urls[0], dhcp_svc_name),
            '{0}/{1}'.format(base_path, dhcp_svc_name),
            'primary=false'
            )

        self.execute_cli_inherit_cmd(
            self.ms_node,
            '{0}/services/{1}'.format(self.node_urls[1], dhcp_svc_name),
            '{0}/{1}'.format(base_path, dhcp_svc_name),
            'primary=true'
            )

        self._create_and_run_plan()

        # 1.1 UPDATE THE RANGES UNDER THE DESIRED NODE
        dhcp_range_updates_to_subnet1 = [
            (base_ipv4 + '1.231', base_ipv4 + '1.235'),
            (base_ipv4 + '1.236', base_ipv4 + '1.245')
            ]

        # Update 2x ranges in subnet 1
        sub_path = '{0}/{1}/subnets/s1'.format(self.primary_node_url
                                               + '/services',
                                               dhcp_svc_name)
        for idx, item in enumerate(dhcp_range_updates_to_subnet1):
            range_start, range_end = item
            self.execute_cli_update_cmd(
                self.ms_node,
                '{0}/ranges/r{1}'.format(sub_path, idx),
                'start={0} end={1}'.format(range_start, range_end)
                )

        # 2.1 CONTRACTING SERVICE FROM NODE 2
        self.execute_cli_remove_cmd(self.ms_node,
                                    self.secondary_node_url
                                    + "/services/{0}".format(dhcp_svc_name))

        # 3.1 CREATE PLAN
        self._create_and_run_plan(12)

        # 4.1 CHECK CONFIG FOR NODE 1
        expected_ranges = dhcp_ranges
        expected_ranges[0].pop(0)
        expected_ranges[0].pop(0)
        expected_ranges[0].extend(dhcp_range_updates_to_subnet1)
        std_err = self.datadriven_verification_check_one_node(
            0, self.subnets, expected_ranges, None, 4,
            dhcp_ntp_srv, dhcp_name_srv
            )

        self.assertEqual([], std_err)

        # 4.2 CHECK PROCESS IS RUNNING ON NODE 1
        cmd = "/bin/ps aux | /bin/grep 'd[h]cpd'"
        _, _, rc = self.run_command(self.nodes_names[0], cmd, su_root=True)
        self.assertEqual(0, rc)

        # 4.3 CHECK PROCESS IS NOT RUNNING ON NODE 2
        _, _, rc = self.run_command(self.nodes_names[1], cmd, su_root=True)
        self.assertNotEqual(0, rc)

        # 4.4 CHECK DHCP SERVER IS SET UP TO START ON BOOT FOR NODE 1
        cmd = "/sbin/chkconfig | /bin/grep \"dhcpd \""
        stdout, _, _ = self.run_command(self.nodes_names[0], cmd, su_root=True)
        self.assertTrue(self.count_text_in_list("on", stdout))

        # 4.5 CHECK DHCP SERVER IS NOT SET UP TO START ON BOOT FOR NODE 2
        stdout, _, _ = self.run_command(self.nodes_names[1], cmd, su_root=True)
        self.assertFalse(self.count_text_in_list("on", stdout))

    @attr('all', 'revert', 'story8265', 'story8265_tc18')
    def test_18_p_dhcp6_two_node_update_range_and_srvs_contraction(self):
        """
        @tms_id: litpcds_8265_tc18
        @tms_requirements_id: LITPCDS-8265
        @tms_title: Update ranges to an existing range via its inherited object
        @tms_description: To ensure that it is possible to update ranges to an
        existing range via its inherited object, while simultaneously
        contracting the service to be deployed only on a single node.
        @tms_test_steps:
            @step:Below the nodes inherited object. Update two of the existing
            ranges below the first subnet to use new values.
            @result: Ranges updated successfully
            @step: Remove the service under node 1.
            @result: Service removed
            @step: Create and run plan.
            @result: Plan created and run successfully
            @step: Verify that the service is running
            @result: Service verified to be running
            @step: Verify that the service is serving the expected ranges
            @result: Service verified to be serving expected ranges
            @step: Verify that properties (nameservers, search and
            ntpservers) have been applied successfully
            @result: Properties verified to have been applied
            @step: Remove failover & primary/seconday information.
            @result: failover & primary/seconday information removed
        @tms_test_precondition: NA
        @tms_execution_type: Automated
        """
        self.create_n_networks_n_interfaces(5, version=6)

        base_path = '/software/services'
        dhcp_svc_name = 'dhcp6'

        dhcp_subnet_names = ['s1', 's2', 's3', 's4', 's5']
        dhcp_ranges = [
            [
                (self.ipv6_networks[0] + '22', self.ipv6_networks[0] + '28'),
                (self.ipv6_networks[0] + '32', self.ipv6_networks[0] + '38'),
                (self.ipv6_networks[0] + '41', self.ipv6_networks[0] + '49'),
                (self.ipv6_networks[0] + '51', self.ipv6_networks[0] + '59'),
                (self.ipv6_networks[0] + '61', self.ipv6_networks[0] + '69')
            ],
            [
                (self.ipv6_networks[1] + '21', self.ipv6_networks[1] + '29'),
                (self.ipv6_networks[1] + '31', self.ipv6_networks[1] + '39'),
                (self.ipv6_networks[1] + '51', self.ipv6_networks[1] + '59'),
                (self.ipv6_networks[1] + '61', self.ipv6_networks[1] + '69'),
                (self.ipv6_networks[1] + '71', self.ipv6_networks[1] + '79')
            ],
            [
                (self.ipv6_networks[2] + '21', self.ipv6_networks[2] + '29')
            ],
            [
                (self.ipv6_networks[3] + '21', self.ipv6_networks[3] + '29'),
                (self.ipv6_networks[3] + '31', self.ipv6_networks[3] + '39'),
                (self.ipv6_networks[3] + '41', self.ipv6_networks[3] + '49')
            ],
            [
                (self.ipv6_networks[4] + '21', self.ipv6_networks[4] + '29'),
            ]
        ]

        # 0.1 Create svc
        self.execute_cli_create_cmd(
            self.ms_node,
            '{0}/{1}'.format(base_path, dhcp_svc_name),
            'dhcp6-service',
            'service_name={0}'.format(dhcp_svc_name)
            )

        # 0.2 Create subnets & ranges
        for sub_idx, sub_name in enumerate(dhcp_subnet_names):
            sub_path = '{0}/{1}/subnets/{2}'.format(
                base_path, dhcp_svc_name, sub_name
                )
            self.execute_cli_create_cmd(
                self.ms_node, sub_path, 'dhcp6-subnet',
                'network_name=' + self.networks[sub_idx]
                )
            sub_range = dhcp_ranges[sub_idx]
            for idx, item in enumerate(sub_range):
                range_start, range_end = item
                self.execute_cli_create_cmd(
                    self.ms_node,
                    '{0}/ranges/r{1}'.format(sub_path, idx),
                    'dhcp6-range',
                    'start={0} end={1}'.format(range_start, range_end)
                    )

        # 0.3 Add inherit
        self.execute_cli_inherit_cmd(
            self.ms_node,
            '{0}/services/{1}'.format(self.node_urls[0], dhcp_svc_name),
            '{0}/{1}'.format(base_path, dhcp_svc_name),
            'primary=true'
            )

        self.execute_cli_inherit_cmd(
            self.ms_node,
            '{0}/services/{1}'.format(self.node_urls[1], dhcp_svc_name),
            '{0}/{1}'.format(base_path, dhcp_svc_name),
            'primary=false'
            )

        self._create_and_run_plan()

        dhcp_range_updates_to_subnet1 = [
                (self.ipv6_networks[0] + '29', self.ipv6_networks[0] + '30'),
                (self.ipv6_networks[0] + '39', self.ipv6_networks[0] + '40'),
            ]

        # 1.1 Update 2x ranges in subnet 1
        sub_path = '{0}/{1}/subnets/s1'.format(self.secondary_node_url
                                               + '/services',
                                               dhcp_svc_name)
        for idx, item in enumerate(dhcp_range_updates_to_subnet1):
            range_start, range_end = item
            self.execute_cli_update_cmd(
                self.ms_node,
                '{0}/ranges/r{1}'.format(sub_path, idx),
                'start={0} end={1}'.format(range_start, range_end)
                )

        # 2.1 CONTRACTING SERVICE FROM NODE 1
        self.execute_cli_remove_cmd(self.ms_node,
                                    self.primary_node_url
                                    + "/services/{0}".format(dhcp_svc_name))
        # 3.1
        self._create_and_run_plan()

        expected_ranges = dhcp_ranges
        expected_ranges[0].pop(0)
        expected_ranges[0].pop(0)
        expected_ranges[0].extend(dhcp_range_updates_to_subnet1)
        std_err = self.datadriven_verification_check_one_node(
            1, self.subnets, expected_ranges, 255, 6
            )
        self.assertEqual([], std_err)

        # 4.1 CHECK PROCESS IS RUNNING ON NODE 2
        cmd = "/bin/ps aux | /bin/grep 'd[h]cpd -6'"
        _, _, rc = self.run_command(self.nodes_names[1], cmd, su_root=True)
        self.assertEqual(0, rc)

        # 4.2 CHECK PROCESS IS NOT RUNNING ON NODE 1
        _, _, rc = self.run_command(self.nodes_names[0], cmd, su_root=True)
        self.assertNotEqual(0, rc)

        # 4.3 CHECK DHCP SERVER IS SET UP TO START ON BOOT FOR NODE 2
        cmd = "/sbin/chkconfig | /bin/grep dhcpd6"
        stdout, _, _ = self.run_command(self.nodes_names[1], cmd, su_root=True)
        self.assertTrue(self.count_text_in_list("on", stdout))

        # 4.4 CHECK DHCP SERVER IS NOT SET UP TO START ON BOOT FOR NODE 1
        stdout, _, _ = self.run_command(self.nodes_names[0], cmd, su_root=True)
        self.assertFalse(self.count_text_in_list("on", stdout))
