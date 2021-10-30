import React from "react";
import { Switch, Route, Redirect } from "react-router-dom";
import ReactNotification from 'react-notifications-component';

// views
import Sidebar from "components/Sidebar/Sidebar.js";
import AlertSettings from "views/admin/Settings.js";
import ZeppelinInterpreterSettings from "views/admin/InterpreterSettings.js";
import Notebooks from "views/admin/Notebooks.js";
import NotebookView from "views/admin/NotebookView.js";
import Connections from "views/admin/Connections.js";
import SparkUI from "views/admin/sparkUI.js";
import WorkflowsMain from "views/admin/WorkflowsMain.js";
import SchedulesView from "views/admin/Schedules.js";
import Dashboard from "views/admin/Dashboard.js";
import { GlobalContextProvider } from "./GlobalContext";

export default function Admin() {
  return (
    <>
      <GlobalContextProvider>
        <Sidebar isEmbedPage={true} />
        <ReactNotification />
        <div className="relative md:ml-12 bg-gray-200" >
          <div className="px-0 md:px-0 py-2 mx-auto w-full" style={{minHeight: "calc(100vh - 0px)", padding: "1rem 0rem 0 0rem"}}>
            <Switch>
              <Route path="/api/redirect/cuelake/dashboard" exact component={Dashboard} />
              <Route path="/api/redirect/cuelake/notebooks"  exact component={Notebooks} />
              <Route path="/api/redirect/cuelake/notebook/:notebookId" exact component={NotebookView} />
              <Route path="/api/redirect/cuelake/settings" exact component={AlertSettings} />
              <Route path="/api/redirect/cuelake/connections" exact component={Connections} />
              <Route path="/api/redirect/cuelake/schedules" exact component={SchedulesView} />
              <Route path="/api/redirect/cuelake/workflows" exact component={WorkflowsMain} />
              <Route path="/interpreterSettings" exact component={ZeppelinInterpreterSettings} />
              <Route path="/api/redirect/cuelake/spark" exact component={SparkUI} />
              <Redirect from="/" to="/api/redirect/cuelake/dashboard" />
            </Switch>
          </div>
        </div>
      </GlobalContextProvider>
    </>
  );
}
