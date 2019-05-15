<!---
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License
-->

# hawtio dispatch router plugin

dispatch-hawtio-console.war is a standalone [hawtio](http://hawt.io/) plugin that can be deployed in a server alongside the main hawtio-web application.

The project creates a war file that can be deployed in various application services and is also OSGi-ified so it deploys nicely into Apache Karaf.

## Docker

The fastest way to use the console is to run the [docker image](https://hub.docker.com/r/ernieallen/dispatch-console/). Follow the installation/run instruction on that page.

## Building
The dispatch-hawtio-console.war file is pre-built and can be installed alongside the hawtio.war on any system with a modern java installation. If you want to build the dispatch-hawtio-console.war from source:

- do a maven build of dispatch

    $ cd console/hawtio

    $ mvn clean install

The dispatch-hawtio-console-<version>-SNAPSHOT.war file should now be in the target directory.

## Apache Tomcat installation

Copy the dispatch-hawtio-console-<version>-SNAPSHOT.war file as the following name

    dispatch-hawtio-console.war
    
to the deploy directory of Apache Tomcat or similar Java web container. Ensure the hawtio.war file is present in the same directory. Point a browser at http://\<tomcat-host:port\>/hawtio
Dispatch Router should be available as a tab in the console.

## Connecting to a router

On the Dispatch Router's console page, select the Connect sub tab. Enter the address of a dispatch router. Enter the port of a websockets to tcp proxy and click the Connect button.

### Websockets to tcp proxy

The console communicates to a router using websockets. 
The router listens for tcp. Therefore a websockets/tcp proxy is required.

A popular python based proxy is [websockify](https://github.com/kanaka/websockify). To use it:

    $ yum install python-websockify

#### Manually running a python websockets/tcp proxy

    $ websockify 5673 0.0.0.0:20009 &
    
In the above, websockify is listening for ws traffic on port 5673 and will proxy it to 0.0.0.0:20009. One of the routers will need a listener on the proxied port. An example router .conf file entry is:

    listener {
        name: ProxyListener
        role: normal
        host: 0.0.0.0
        port: 20009
        saslMechanisms: ANONYMOUS
    }

#### Automatically running a proxy with a router

You can automatically start the proxy program when a router starts. Add the listener above and the following console section to a router's config file.

    console {
        listener: ProxyListener
        proxy:    wobsockify
        args:     $host:5673 $host:$port
    }
    
