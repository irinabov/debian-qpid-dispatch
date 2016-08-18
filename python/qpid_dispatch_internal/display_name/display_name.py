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

"""
DisplayNameService provides the mapping needed to associate an un-friendly user identifier to a more friendly
user nick name.
Maintains a dict (profile_dict) of ssl profile names to SSLProfile objects. The SSLProfile objects are built using
the file name which contains a mapping of user identifiers to user names.
"""
import traceback
from traceback import format_exc

from ..router.message import Message

from ..dispatch import IoAdapter, LogAdapter, LOG_INFO, LOG_ERROR, LOG_TRACE, LOG_STACK_LIMIT
import json

class SSLProfile(object):
    def __init__(self, profile_name, profile_file):
        super(SSLProfile, self).__init__()
        self.profile_name = profile_name
        self.profile_file = profile_file
        self.cache = {}
        with open(profile_file) as json_data:
            d = json.load(json_data)
            for key in d.keys():
                self.cache[key] = d[key]

class DisplayNameService(object):

    def __init__(self, address):
        super(DisplayNameService, self).__init__()
        # profile_dict will be a mapping from ssl_profile_name to the SSLProfile object
        self.profile_dict = {}
        self.io_adapter = None
        self.log_adapter = LogAdapter("DISPLAYNAME")
        if address:
            self._activate(address)

    def log(self, level, text):
        info = traceback.extract_stack(limit=2)[0] # Caller frame info
        self.log_adapter.log(level, text, info[0], info[1])

    def _activate(self, address):
        self.log(LOG_INFO, "Activating DisplayNameService on %s" % address)
        self.io_adapter = [IoAdapter(self.receive, address)]

    def add(self, profile_name, profile_file_location):
        ssl_profile = SSLProfile(profile_name, profile_file_location)
        self.profile_dict[profile_name] = ssl_profile
        self.log(LOG_INFO, "Added profile name %s, profile file location %s to DisplayNameService" % (profile_name, profile_file_location))

    def remove(self, profile_name):
        try:
            del self.profile_dict[profile_name]
        except KeyError:
            pass

    def reload_all(self):
        for profile_name in self.profile_dict.keys():
            self.add(profile_name, self.profile_dict[profile_name].profile_file)

    def reload(self, profile_name=None):
        if profile_name:
            self.add(profile_name, self.profile_dict[profile_name].profile_file)
        else:
            self.reload_all()

    def query(self, profile_name, user_id):
        self.log(LOG_TRACE, "Received query for profile name %s, user id %s to DisplayNameService" %
                 (profile_name, user_id))
        ssl_profile = self.profile_dict.get(profile_name)
        if ssl_profile:
            profile_cache = self.profile_dict.get(profile_name).cache
            user_name = profile_cache.get(user_id)
            body = {'user_name': user_name if user_name else user_id}
        else:
            body = {'user_name': user_id}

        return body

    def receive(self, message, unused_link_id, unused_cost):
        """
        This is the IOAdapter's callback function. Will be invoked when the IOAdapter receives a request.
        Will only accept QUERY requests.
        Matches the passed in profilename and userid to user name. If a matching user name is not found, returns the
        passed in userid as the user name.
        :param message:
        :param unused_link_id:
        :param unused_cost
        """
        body = {}

        try:
            opcode = message.body.get('opcode')
            profile_name = message.body.get('profilename')
            user_id = message.body.get('userid')
            if opcode == 'QUERY' and profile_name and user_id:
                body = self.query(profile_name, user_id)
        except Exception:
            self.log(LOG_ERROR, "Exception in raw message processing: body=%r\n%s" %
                     (message.body, format_exc(LOG_STACK_LIMIT)))

        response = Message(address=message.reply_to,
                           body=body,
                           correlation_id=message.correlation_id)

        self.io_adapter[0].send(response)
