import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter, Route, Switch, Redirect } from "react-router-dom";
import 'react-notifications-component/dist/theme.css'

import "@fortawesome/fontawesome-free/css/all.min.css";
import "assets/styles/tailwind.css";
import 'antd/dist/antd.css';

// layouts
import Admin from "layouts/Admin.js";
import EmbedAdmin from "layouts/EmbedAdmin.js";

ReactDOM.render(
  <BrowserRouter  basename={'/'}>
    <Switch>
      {/* add routes with layouts */}
      {/* <Route path="/auth" component={Auth} /> */}
      <Route path="/api/redirect/cuelake/" component={EmbedAdmin} />
      <Route path="/" component={Admin} />
      
      {/* add redirect for first page */}
      {/* <Redirect from="/api/redirect/*" to="/api/redirect/cuelake/" /> */}
      <Redirect from="*" to="/" />
    </Switch>
  </BrowserRouter>,
  document.getElementById("root")
);
