import React from "react";
import Workflows from "components/Workflows/Workflows";

export default function WorkflowsMain() {
  return (
    <>
      <div className="flex flex-wrap mh-full">
        <div className="w-full mb-12 px-4">
          <Workflows />
        </div>
      </div>
    </>
  );
}
