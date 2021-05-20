import React from "react";
import FilesTable from "components/Files/FilesTable";

export default function Files() {
  return (
    <>
      <div className="flex flex-wrap mh-full">
        <div className="w-full mb-12 px-4">
          <FilesTable />
        </div>
      </div>
    </>
  );
}
