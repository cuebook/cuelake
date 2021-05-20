import React from "react";

// components

import NotebookView from "components/Notebooks/NotebookView";

export default function NotebookViewFunction() {
  return (
    <>
      <div className="flex flex-wrap mh-full">
        <div className="w-full">
          <NotebookView />
        </div>
      </div>
    </>
  );
}
