/*
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
under the License.
*/

import React from "react";
import { render } from "@testing-library/react";
import { service, login } from "../serviceTest";
import DetailTablesPage from "./detailsTablePage";

it("renders the DetailTablesPage", () => {
  const entity = "router";
  const routerName = "A";

  login(() => {
    expect(service.management.connection.is_connected()).toBe(true);

    const props = {
      entity,
      locationState: {
        currentRecord: {
          name: routerName,
          routerId: service.utilities.idFromName(routerName, "_topo")
        }
      },
      details: true,
      service,
      schema: service.schema,
      lastUpdated: (date) => {},
    };

    const { getByTestId } = render(<DetailTablesPage {...props} />);
    const header = getByTestId(`detail-for-${routerName}`);
    expect(header).toBeInTheDocument();
  });
});
