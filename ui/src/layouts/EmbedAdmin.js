import React from "react";
import { Switch, Route, Redirect } from "react-router-dom";
import ReactNotification from 'react-notifications-component';

// components

import AdminNavbar from "components/Navbars/AdminNavbar.js";
import Sidebar from "components/Sidebar/Sidebar.js";
import HeaderStats from "components/Headers/HeaderStats.js";

// views
import Settings from "views/admin/Settings.js";
import Notebooks from "views/admin/Notebooks.js";
import NotebookView from "views/admin/NotebookView.js";
import Connections from "views/admin/Connections.js";
import WorkflowsMain from "views/admin/WorkflowsMain.js";
import WorkflowRunLogs from "views/admin/WorkflowRunLogs.js";

export default function Admin() {
  return (
    <>
      <ReactNotification />
      <div className="relative bg-gray-200" >
        <div className="px-0 md:px-0 py-2 mx-auto w-full" style={{height: "calc(100vh - 0px)", padding: "2rem 3rem"}}>
          <Switch>
            <Route path="/api/redirect/cuelake/notebooks"  exact component={Notebooks} />
            <Route path="/api/redirect/cuelake/notebook/:notebookId" exact component={NotebookView} />
            <Route path="/api/redirect/cuelake/settings" exact component={Settings} />
            <Route path="/api/redirect/cuelake/connections" exact component={Connections} />
            <Route path="/api/redirect/cuelake/workflows" exact component={WorkflowsMain} />
            <Route path="/api/redirect/cuelake/workflows/workflowRun/:id" exact component={WorkflowRunLogs} />
            <Redirect from="/" to="/api/redirect/cuelake/notebooks" />
          </Switch>
        </div>
      </div>
    </>
  );
}
