#ifndef __dispatch_private_h__
#define __dispatch_private_h__
/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

//
// The following declarations are for types that are shared between modules yet are
// not in the public API.
//
typedef struct qd_server_t           qd_server_t;
typedef struct qd_container_t        qd_container_t;
typedef struct qd_waypoint_t         qd_waypoint_t;
typedef struct qd_lrp_container_t    qd_lrp_container_t;
typedef struct qd_lrp_t              qd_lrp_t;
typedef struct qd_router_link_t      qd_router_link_t;
typedef struct qd_router_node_t      qd_router_node_t;
typedef struct qd_router_ref_t       qd_router_ref_t;
typedef struct qd_router_link_ref_t  qd_router_link_ref_t;
typedef struct qd_router_lrp_ref_t   qd_router_lrp_ref_t;
typedef struct qd_router_conn_t      qd_router_conn_t;
typedef struct qd_config_phase_t     qd_config_phase_t;
typedef struct qd_config_address_t   qd_config_address_t;

#include <qpid/dispatch/container.h>
#include <qpid/dispatch/router.h>
#include <qpid/dispatch/connection_manager.h>
#include "policy.h"
#include "server_private.h"
#include "router_private.h"

struct qd_dispatch_t {
    qd_server_t             *server;
    qd_container_t          *container;
    qd_router_t             *router;
    void                    *agent;
    qd_connection_manager_t *connection_manager;
    qd_policy_t             *policy;
    void                    *dl_handle;

    int    thread_count;
    char  *sasl_config_path;
    char  *sasl_config_name;
    char  *router_area;
    char  *router_id;
    qd_router_mode_t  router_mode;
};

/**
 * Configure the AMQP container from a configuration entity.
 *
 * @param qd The dispatch handle returned by qd_dispatch
 * @param entity The configuration entity.
 */
qd_error_t qd_dispatch_configure_container(qd_dispatch_t *qd, qd_entity_t *entity);

/**
 * Configure the router node from a configuration entity.
 * If this is not called, the router will run in ENDPOINT mode.
 *
 * @param qd The dispatch handle returned by qd_dispatch.
 * @param entity The configuration entity.
 */
qd_error_t qd_dispatch_configure_router(qd_dispatch_t *qd, qd_entity_t *entity);

/**
 * Prepare Dispatch for operation.  This must be called prior to
 * calling qd_server_run or qd_server_start.
 *
 * @param qd The dispatch handle returned by qd_dispatch
 */
qd_error_t qd_dispatch_prepare(qd_dispatch_t *qd);

/**
 * Configure an address, must be called after qd_dispatch_prepare
 */
qd_error_t qd_dispatch_configure_address(qd_dispatch_t *qd, qd_entity_t *entity);

/**
 * Configure a waypoint, must be called after qd_dispatch_prepare
 */
qd_error_t qd_dispatch_configure_waypoint(qd_dispatch_t *qd, qd_entity_t *entity);

/**
 * Configure a link-route-pattern, must be called after qd_dispatch_prepare
 */
qd_error_t qd_dispatch_configure_lrp(qd_dispatch_t *qd, qd_entity_t *entity);

/**
 * Configure a route, must be called after qd_dispatch_prepare
 */
qd_error_t qd_dispatch_configure_route(qd_dispatch_t *qd, qd_entity_t *entity);

/**
 * Configure security policy, must be called after qd_dispatch_prepare
 */
qd_error_t qd_dispatch_configure_policy(qd_dispatch_t *qd, qd_entity_t *entity);

/**
 * Configure security policy manager, must be called after qd_dispatch_prepare
 */
qd_error_t qd_dispatch_register_policy_manager(qd_dispatch_t *qd, qd_entity_t *entity);

/**
 * Configure display name service, must be called after qd_dispatch_prepare
 */
qd_error_t qd_dispatch_register_display_name_service(qd_dispatch_t *qd, void *object);

/**
 * \brief Configure the logging module from the
 *        parsed configuration file.  This must be called after the
 *        call to qd_dispatch_prepare completes.
 *
 * @param qd The dispatch handle returned by qd_dispatch
 */
qd_error_t qd_dispatch_configure_logging(qd_dispatch_t *qd);

/** Register a managed entity implementation with the management agent.
 * NOTE: impl must be unregistered before it is freed.
 */
void qd_dispatch_register_entity(qd_dispatch_t *qd, const char *type, void *impl);

/** Unregister a managed entity implementation */
void qd_dispatch_unregister_entity(qd_dispatch_t *qd, void *impl);

/** Set the agent */
void qd_dispatch_set_agent(qd_dispatch_t *qd, void *agent);

/**
 * Set a new router id, freeing the prior id string
 * TAKES OWNERSHIP OF THE POINTER PASSED TO IT
 */
void qd_dispatch_set_router_id(qd_dispatch_t *qd, char *_id);

/**
 * Set a new router area, freeing the prior area string
 * TAKES OWNERSHIP OF THE POINTER PASSED TO IT
 */
void qd_dispatch_set_router_area(qd_dispatch_t *qd, char *_area);

#endif
