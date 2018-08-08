#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import unittest2 as unittest
from system_test import TestCase, Qdrouterd, main_module
from system_tests_drain_support import DrainMessagesHandler, DrainOneMessageHandler
from system_tests_drain_support import DrainNoMessagesHandler, DrainNoMoreMessagesHandler


class DrainSupportTest(TestCase):

    @classmethod
    def setUpClass(cls):
        """Start a router and a messenger"""
        super(DrainSupportTest, cls).setUpClass()
        name = "test-router"
        config = Qdrouterd.Config([
            ('router', {'mode': 'standalone', 'id': 'QDR'}),

            # Setting the linkCapacity to 10 will allow the sender to send a burst of 10 messages
            ('listener', {'port': cls.tester.get_port(), 'linkCapacity': 10}),

        ])

        cls.router = cls.tester.qdrouterd(name, config)
        cls.router.wait_ready()
        cls.address = cls.router.addresses[0]

    def test_drain_support_1_all_messages(self):
        drain_support = DrainMessagesHandler(self.address)
        drain_support.run()
        self.assertEqual(drain_support.error, None)

    def test_drain_support_2_one_message(self):
        drain_support = DrainOneMessageHandler(self.address)
        drain_support.run()
        self.assertEqual(drain_support.error, None)

    def test_drain_support_3_no_messages(self):
        drain_support = DrainNoMessagesHandler(self.address)
        drain_support.run()
        self.assertEqual(drain_support.error, None)

    def test_drain_support_4_no_more_messages(self):
        drain_support = DrainNoMoreMessagesHandler(self.address)
        drain_support.run()
        self.assertEqual(drain_support.error, None)


if __name__ == '__main__':
    unittest.main(main_module())
