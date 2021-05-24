import React from "react";
import Logs from "components/Workflows/WorkflowRunLogs";

export default function WorkflowRunLogs(props) {
  return (
    <>
      <div className="flex flex-wrap">
        <div className="w-full lg:w-12/12 px-4">
          <Logs {...props}/>
        </div>
      </div>
    </>
  );
}
