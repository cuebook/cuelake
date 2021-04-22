import React from "react";
import Workflows from "components/Workflows/Workflows";

export default function WorkflowsMain() {
  return (
    <>
      <div className="flex flex-wrap">
        <div className="w-full lg:w-12/12 px-4 mt-4">
          <Workflows />
        </div>
      </div>
    </>
  );
}
