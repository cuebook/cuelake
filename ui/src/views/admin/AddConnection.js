import React from "react";

// components

import AddConnection from "components/Connections/AddConnection.js";

export default function ConnectionFunction() {
  return (
    <>
      <div className="flex flex-wrap mt-4 mh-full">
        <div className="w-full mb-12 px-4">
          <AddConnection />
        </div>
      </div>
    </>
  );
}
