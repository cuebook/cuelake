import React, { useContext } from "react";
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
import Files from "views/admin/Files.js";
import SchedulesView from "views/admin/Schedules.js";
import WorkflowsMain from "views/admin/WorkflowsMain.js";
import WorkflowRunLogs from "views/admin/WorkflowRunLogs.js";

// contexts
import { GlobalContextProvider } from "./GlobalContext";

export default function Admin() {
  return (
    <>
      <GlobalContextProvider>
        <Sidebar />
        <ReactNotification />
        <div className="relative md:ml-64 bg-gray-200">
          <AdminNavbar />
          {/* Header */}
          <HeaderStats />
          <div className="px-0 md:px-0 mx-auto w-full" style={{minHeight: "calc(100vh - 0px)", padding: "1rem 0rem 0 0rem"}}>
            <Switch>
              <Route path="/notebooks" exact component={Notebooks} />
              <Route path="/notebook/:notebookId" exact component={NotebookView} />
              <Route path="/settings" exact component={Settings} />
              <Route path="/connections" exact component={Connections} />
              <Route path="/schedules" exact component={SchedulesView} />
              <Route path="/workflows" exact component={WorkflowsMain} />
              <Route path="/files" exact component={Files} />
              <Route path="/workflows/workflowRun/:id" exact component={WorkflowRunLogs} />
              <Redirect from="/" to="/notebooks" />
            </Switch>
          </div>
        </div>
      </GlobalContextProvider>
    </>
  );
}
