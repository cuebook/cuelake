import React from "react";
import { Switch, Route, Redirect } from "react-router-dom";
import ReactNotification from 'react-notifications-component';

// components

import Sidebar from "components/Sidebar/Sidebar.js";

// views
import AlertSettings from "views/admin/Settings.js";
import ZeppelinInterpreterSettings from "views/admin/InterpreterSettings.js";
import Notebooks from "views/admin/Notebooks.js";
import NotebookView from "views/admin/NotebookView.js";
import Connections from "views/admin/Connections.js";
import SchedulesView from "views/admin/Schedules.js";
import WorkflowsMain from "views/admin/WorkflowsMain.js";
import SparkUI from "views/admin/sparkUI.js";
import Dashboard from "views/admin/Dashboard.js";
import AddWorkspace from "views/admin/AddWorkspace.js";

// contexts
import { GlobalContextProvider } from "./GlobalContext";

export default function Admin() {
  return (
    <>
      <GlobalContextProvider>
        <Sidebar />
        <ReactNotification />
        <div className="relative md:ml-64 bg-gray-200">
          {/* <AdminNavbar /> */}
          {/* Header */}
          {/* <HeaderStats /> */}
          <div className="px-0 md:px-0 mx-auto w-full" style={{minHeight: "calc(100vh - 0px)", padding: "1rem 0rem 0 0rem"}}>
            <Switch>
              <Route path="/dashboard" exact component={Dashboard} />
              <Route path="/workspace" exact component={AddWorkspace} />
              <Route path="/notebooks" exact component={Notebooks} />
              <Route path="/notebook/:notebookId" exact component={NotebookView} />
              <Route path="/settings" exact component={AlertSettings} />
              <Route path="/connections" exact component={Connections} />
              <Route path="/schedules" exact component={SchedulesView} />
              <Route path="/workflows" exact component={WorkflowsMain} />
              <Route path="/interpreterSettings" exact component={ZeppelinInterpreterSettings} />
              <Route path="/spark" exact component={SparkUI} />
              <Redirect from="/" to="/dashboard" />
            </Switch>
          </div>
        </div>
      </GlobalContextProvider>
    </>
  );
}
