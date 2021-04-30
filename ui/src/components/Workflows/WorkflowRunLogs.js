import React, { useState, useEffect, useRef } from "react";
import style from "./style.module.scss";
import Moment from 'react-moment';
import {
    Table,
    Button,
    Modal,
    Input,
    Select,
    Icon,
    Tooltip,
    Popover,
    Form,
    message,
    Drawer,
    Row,
    Col,
    Switch
  } from "antd";

import workflowsService from "services/workflows.js";

export default function WorkflowRunLogs(props) {
  const [workflowRunLogs, setWorkflowRunLogs] = useState('');
  const [loading, setLoading] = useState('');
  const [total, setTotal] = useState('');
  
  useEffect(() => {
    if (!workflowRunLogs) {
        getWorkflowRunLogs(props.match.params.id);
    }
  }, []);

  const getWorkflowRunLogs = async (workflowRunId) => {
    setLoading(true)
    const response = await workflowsService.getWorkflowRunLogs(workflowRunId);
    if(response){
      setWorkflowRunLogs(response.workflowRunLogs);
      setTotal(response.total)
    }
    setLoading(false)
  };

  const columns = [
    {
      title: "Run Status",
      dataIndex: "status",
      key: "status",
      width: "15%",
      render: text => {
        return (
          <span>
            {text}
          </span>
        );
      }
    },
    {
      title: "Start Time",
      dataIndex: "startTimestamp",
      key: "startTimestamp",
      width: "30%",
      render: text => {
        return (
          <span>
            <Moment format="DD-MM-YYYY hh:mm:ss">{text}</Moment>
          </span>
        );
      }
    },
    {
      title: "Duration",
      dataIndex: "endTimestamp",
      key: "duration",
      width: "30%",
      render: (text, record) => {
        // const date = new Date(record.endTimestamp) - new Date(record.startTimestamp) 
        return (
          <span>
            <Moment duration={record.startTimestamp}
                                date={record.endTimestamp}
                        />
          </span>
        );
      }
    },
    {
        title: "Actions",
        dataIndex: "",
        key: "",
        width: "10%",
        render: (text, record) => {
          return (
            <a href={"workflows/workflowRun/" + record.id}>Logs</a>
          );
        }
    }
  ]


  return (
    <div className={style.runLogTable}>
      <Table
        rowKey={"id"}
        scroll={{ x: "100%" }}
        columns={columns}
        dataSource={workflowRunLogs}
        // loading={loading}
        size={"small"}
      />
    </div>
  );
}
