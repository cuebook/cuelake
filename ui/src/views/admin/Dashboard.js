import React from "react";

// components

import Dashboard from "components/Dashboard/dashboard.js";

export default function DashboardFunction() {
  return (
    <>
      <div className="flex flex-wrap mh-full">
        <div className="w-full mb-12 px-4">
          <Dashboard />
        </div>
      </div>
    </>
  );
}
