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
# under the License
#

from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import os
import errno
import re
import unittest
from subprocess import PIPE
import subprocess
from system_test import main_module, SkipIfNeeded, TestCase
from system_test import Qdrouterd, TIMEOUT, AsyncTestSender, AsyncTestReceiver
try:
    import queue as Queue   # 3.x
except ImportError:
    import Queue as Queue   # 2.7

from threading import Thread
from threading import Event
import uuid

from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container

class ConsolePreReq(object):
    @staticmethod
    def is_cmd(name):
        ''' determine if a command is present and executes on the system '''
        try:
            devnull = open(os.devnull, "w")
            subprocess.Popen([name], stdout=devnull, stderr=devnull).communicate()
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                return False
        return True

    @staticmethod
    def should_skip():
        try:
            found_npm = ConsolePreReq.is_cmd('npm')

            return not found_npm
        except OSError:
            return True

class ConsoleTest(TestCase):
    """Run npm console tests"""

    @classmethod
    def setUpClass(cls):
        super(ConsoleTest, cls).setUpClass()

        def router(name, mode, extra):
            config = [
                ('router', {'mode': mode, 'id': name}),
                ('listener', {'role': 'normal', 'port': cls.tester.get_port()})
            ]

            if extra:
                config.extend(extra)
            config = Qdrouterd.Config(config)
            cls.routers.append(cls.tester.qdrouterd(name, config, wait=True))
            return cls.routers[-1]

        cls.routers = []

        interrouter_port = cls.tester.get_port()
        cls.http_port = cls.tester.get_port()
        cls.sender_port = cls.tester.get_port()
        cls.receiver_port = cls.tester.get_port()

        router('A', 'interior',
               [('listener', {'role': 'inter-router', 'port': interrouter_port}),
                ('listener', {'role': 'normal', 'port': cls.sender_port}),
                ('listener', {'role': 'normal', 'port': cls.http_port, 'http': True})])
        cls.INT_A = cls.routers[0]
        cls.INT_A.listener = cls.INT_A.addresses[0]

        router('B', 'interior',
               [('connector', {'name': 'connectorToA', 'role': 'inter-router',
                    'port': interrouter_port}),
                ('listener', {'role': 'normal', 'port': cls.receiver_port})])
        cls.INT_B = cls.routers[1]
        cls.INT_B.listener = cls.INT_B.addresses[0]

        cls.INT_A.wait_router_connected('B')
        cls.INT_B.wait_router_connected('A')

    def run_console_test(self):
        address = "toB"
        # create a slow receiver so that we get delayedDeliveries
        receiver = AsyncSlowReceiver(self.INT_B.listener, address)
        sender = AsyncStopableSender(self.INT_A.listener, address)

        pret = 0

        out = ''
        prg = ['npm',  'test', '--', '--watchAll=false', '--coverage']

        p = self.popen(prg, 
            cwd=os.path.join(os.environ.get('BUILD_DIR'), 'console'),
            env=dict(os.environ, TEST_PORT="%d" % self.http_port),
            stdout=PIPE, 
            expect=None)
        out = p.communicate()[0]
        pret = p.returncode

        # write the output
        with open('run_console_test.out', 'w') as popenfile:
            popenfile.write('returncode was %s\n' % p.returncode)
            popenfile.write('out was:\n')
            popenfile.writelines(str(out))

        sender.stop()
        receiver.stop()

        assert pret == 0, \
            "console test exit status %d, output:\n%s" % (pret, out)
        return out

    # If we are unable to run the npm command. Skip the test
    @SkipIfNeeded(ConsolePreReq.should_skip(), 'Test skipped: npm command not found')
    def test_console(self):
        self.run_console_test()

class AsyncStopableSender(AsyncTestSender):
    def __init__(self, hostport, address):
        super(AsyncStopableSender, self).__init__(hostport, address, 999999999)
        self._stop_thread = False
        self.sent = 0

    def _main(self):
        self._container.start()
        while self._container.process():
            if self._stop_thread:
                if self._conn:
                    self._conn.close()
                    self._conn = None

    def on_sendable(self, event):
        self._sender.send(Message(body="message %d" % self.sent))
        self.sent += 1

    def stop(self, timeout=TIMEOUT):
        self._stop_thread = True
        self._container.wakeup()
        self._thread.join(timeout=TIMEOUT)
        if self._thread.is_alive():
            raise Exception("AsyncStopableSender did not exit")

# Based on gsim's slow_recv.py
class TimedFlow(MessagingHandler):
    def __init__(self, receiver, credit):
        super(TimedFlow, self).__init__()
        self.receiver = receiver
        self.credit = credit

    def on_timer_task(self, event):
        self.receiver.flow(self.credit)

class AsyncSlowReceiver(AsyncTestReceiver):
    def __init__(self, hostport, target):
        super(AsyncSlowReceiver, self).__init__(hostport, target, msg_args={"prefetch": 0})

    def on_link_opened(self, event):
        super(AsyncSlowReceiver, self).on_link_opened(event)
        self.request_batch(event)

    def request_batch(self, event):
        event.container.schedule(1, TimedFlow(event.receiver, 10))

    def check_empty(self, receiver):
        return not receiver.credit and not receiver.queued

    def on_link_flow(self, event):
        if self.check_empty(event.receiver):
            self.request_batch(event)

    def on_message(self, event):
        print (event.message.body)
        if self.check_empty(event.receiver):
            self.request_batch(event)

if __name__ == '__main__':
    unittest.main(main_module())