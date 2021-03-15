import React from "react";
import { Switch, Route, Redirect } from "react-router-dom";

// components

import AdminNavbar from "components/Navbars/AdminNavbar.js";
import Sidebar from "components/Sidebar/Sidebar.js";
import HeaderStats from "components/Headers/HeaderStats.js";
import FooterAdmin from "components/Footers/FooterAdmin.js";

// views

import Dashboard from "views/admin/Dashboard.js";
import Settings from "views/admin/Settings.js";
import Notebooks from "views/admin/Notebooks.js";

export default function Admin() {
  return (
    <>
      <Sidebar />
      <div className="relative md:ml-64 bg-gray-200">
        <AdminNavbar />
        {/* Header */}
        <HeaderStats />
        <div className="px-0 md:px-0 mx-auto w-full">
          <Switch>
            <Route path="/notebooks" exact component={Notebooks} />
            <Route path="/settings" exact component={Settings} />
            <Redirect from="/" to="/notebooks" />
          </Switch>
          <FooterAdmin />
        </div>
      </div>
    </>
  );
}
