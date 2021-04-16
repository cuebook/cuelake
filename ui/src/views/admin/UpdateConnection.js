import React from "react";

// components

import UpdateConnection from "components/Connections/UpdateConnection.js";

export default function ConnectionFunction() {
  return (
    <>
      <div className="flex flex-wrap mt-4 mh-full">
        <div className="w-full mb-12 px-4">
          <UpdateConnection />
        </div>
      </div>
    </>
  );
}
