import React, { useState, useEffect, useRef } from "react";
import { Button, Form, Input, message, Select, Table } from "antd";
import { useHistory } from "react-router-dom";
import style from "./style.module.scss";
import { MoreOutlined, PlayCircleOutlined, UnorderedListOutlined,
     StopOutlined, FileTextOutlined, DeleteOutlined, CopyOutlined,
      CloseOutlined } from '@ant-design/icons';

const { Option } = Select;

export default function SchedulesView() {


const history = useHistory();
useEffect(() =>{

})


const columns = [
    {
      title: "Schedule Name",
      dataIndex: "name",
      key: "name",
      width: "20%",
      render: text => {
        return (
          <span key={text}>
              <Input placeholder="Enter Schedules names">
              </Input>
            {/* {text.substring(1)} */}
          </span>
        );
      }
    },
    {
        title: "Schedule",
        dataIndex: "name",
        key: "name",
        width: "20%",
        render: text => {
          return (
            <span key={text}>
              {text.substring(1)}
            </span>
          );
        }
      },
      {
        title: "Assigned Notebook",
        dataIndex: "count",
        key: "count",
        width: "20%",

      },
      {
        title: "Action",
        dataIndex: "name",
        key: "name",
        width: "20%",
        render:() => <a>action</a>,
        
      },
];
const data = [
    {
      key: '1',
      name: 'John Brown',
      chinese: 98,
      count: 6,
      english: 70,
    }
  ];
  

return (
    <>

    <div className={`d-flex flex-column justify-content-center text-right mb-2`}>
          <Button
              key="createTag"
              type="primary"
            //   onClick={() => openNewNotebookDrawer()}
          >
              New Schedule
          </Button>
      </div>
    <Table
    rowKey={"id"}
    scroll={{ x: "100%" }}
    columns={columns}
    dataSource={data}
    // loading={loading}
    size={"small"}
    
    />

    </>
)

}