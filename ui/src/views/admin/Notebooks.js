import React from "react";
import { Tabs } from "antd"
import NotebookTable from "components/Notebooks/NotebookTable.js";
import ArchivedNotebook from "components/Notebooks/ArchivedNotebookTable.js";

const { TabPane } = Tabs
// components

export default function NotebookTableFunction() {
  return (
    <>
      <div className="flex flex-wrap mt-4 mh-full">
        <div className="w-full mb-12 px-4">
		    <Tabs defaultActiveKey="1">
		      <TabPane tab="Notebooks" key="1">
		        <NotebookTable />
		      </TabPane>
		      <TabPane tab="Archive" key="2">
		        <ArchivedNotebook/>
		      </TabPane>
		    </Tabs>
        </div>
      </div>
    </>
  );
}
