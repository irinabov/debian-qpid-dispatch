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

# Find libwebsockets include dirs and libraries.
#
# Sets the following variables:
#
#   LIBWEBSOCKETS_FOUND            - True if headers and requested libraries were found
#   LIBWEBSOCKETS_INCLUDE_DIRS     - LibWebSockets include directories
#   LIBWEBSOCKETS_LIBRARIES        - Link these to use libwebsockets
#   LIBWEBSOCKETS_VERSION_STRING   - The library version number
#
# This module reads hints about search locations from variables::
#   LIBWEBSOCKETS_LIBRARYDIR       - Preferred library directory e.g. <prefix>/lib
#   LIBWEBSOCKETS_ROOT             - Preferred installation prefix
#   CMAKE_INSTALL_PREFIX           - Install location for the current project.
#   LIBWEBSOCKETS_INCLUDEDIR       - Preferred include directory e.g. <prefix>/include

find_library(LIBWEBSOCKETS_LIBRARIES
  NAMES websockets libwebsockets
  HINTS "${LIBWEBSOCKETS_LIBRARYDIR}" "${LIBWEBSOCKETS_ROOT}" "${CMAKE_INSTALL_PREFIX}"
  )

find_path(LIBWEBSOCKETS_INCLUDE_DIRS
  NAMES libwebsockets.h
  HINTS "${LIBWEBSOCKETS_INCLUDEDIR}" "${LIBWEBSOCKETS_ROOT}/include" "${CMAKE_INSTALL_PREFIX}/include"
  PATHS "/usr/include"
  )

if(LIBWEBSOCKETS_INCLUDE_DIRS AND EXISTS "${LIBWEBSOCKETS_INCLUDE_DIRS}/lws_config.h")
  file(STRINGS "${LIBWEBSOCKETS_INCLUDE_DIRS}/lws_config.h" lws_version_str
    REGEX "^#define[ \t]+LWS_LIBRARY_VERSION[ \t]+\"[^\"]+\"")
  string(REGEX REPLACE "^#define[ \t]+LWS_LIBRARY_VERSION[ \t]+\"([^\"]+)\".*" "\\1"
    LIBWEBSOCKETS_VERSION_STRING "${lws_version_str}")
  unset(lws_version_str)
endif()

set(lws_required "2.1.0")
if (LIBWEBSOCKETS_VERSION_STRING AND (LIBWEBSOCKETS_VERSION_STRING VERSION_LESS lws_required))
  message(STATUS "Found libwebsockets version ${LIBWEBSOCKETS_VERSION_STRING} but need at least ${lws_required}")
else()
  include(FindPackageHandleStandardArgs)
  find_package_handle_standard_args(
    LIBWEBSOCKETS DEFAULT_MSG LIBWEBSOCKETS_VERSION_STRING LIBWEBSOCKETS_LIBRARIES LIBWEBSOCKETS_INCLUDE_DIRS)
endif()


if (LIBWEBSOCKETS_FOUND AND LIBWEBSOCKETS_VERSION_STRING)
  # This is a fix for DISPATCH-1513. libwebsockets versions 3.2.0 introduces a new flag called LWS_SERVER_OPTION_ALLOW_HTTP_ON_HTTPS_LISTENER
  # The new flag allows (as the flag says) HTTP pver HTTPS listeners. Since this flag is not available before lws 3.2.0 we need
  # to selectively comment out a test.
  set(TEST_OPTION_ALLOW_HTTP_ON_HTTPS_LISTENER "#")
  set(LWS_VERSION_WITH_SSL_FIX "3.2.0")
  if ((LIBWEBSOCKETS_VERSION_STRING STREQUAL LWS_VERSION_WITH_SSL_FIX) OR (LIBWEBSOCKETS_VERSION_STRING STRGREATER  LWS_VERSION_WITH_SSL_FIX))
    set(TEST_OPTION_ALLOW_HTTP_ON_HTTPS_LISTENER "")
  endif()
endif(LIBWEBSOCKETS_FOUND AND LIBWEBSOCKETS_VERSION_STRING)

if(NOT LIBWEBSOCKETS_FOUND)
  unset(LIBWEBSOCKETS_LIBRARIES)
  unset(LIBWEBSOCKETS_INCLUDE_DIRS)
  unset(LIBWEBSOCKETS_VERSION_STRING)
endif()
