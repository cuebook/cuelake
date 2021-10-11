import React from "react";

// components

import AddWorkspace from "components/Workspaces/addWorkspace.js";

export default function ConnectionFunction() {
  return (
    <>
      <div className="flex flex-wrap mh-full">
        <div className="w-full px-4">
          <AddWorkspace />
        </div>
      </div>
    </>
  );
}
