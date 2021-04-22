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

export default function WorkflowRuns(props) {

  const [workflowRuns, setWorkflowRuns] = useState('');
  const [loading, setLoading] = useState('');
  const [total, setTotal] = useState('');
  const [currentPage, setCurrentPage] = useState('');
  const currentPageRef = useRef(currentPage);
  currentPageRef.current = currentPage;
  
  useEffect(() => {
    if (!workflowRuns) {
        setCurrentPage(1)
        getWorkflowRuns(props.workflow.id, 0);
    }

    const refreshWorkflowRunsInterval = setInterval(() => {
      refreshWorkflowRuns(props.workflow.id, (currentPageRef.current - 1)*10)
    }, 3000);

    return () => {
      clearInterval(refreshWorkflowRunsInterval);
    };

  }, []);

  const getWorkflowRuns = async (workflowId, offset) => {
    setLoading(true)
    const response = await workflowsService.getWorkflowRuns(workflowId, offset);
    if(response){
      setWorkflowRuns(response.workflowRuns);
      setTotal(response.total)
    }
    setLoading(false)
  };

  const refreshWorkflowRuns = async (workflowId, offset) => {
    const response = await workflowsService.getWorkflowRuns(workflowId, offset);
    if(response){
      setWorkflowRuns(response.workflowRuns);
      setTotal(response.total);
    }
  };

  const handleTableChange = (event) => {
    setCurrentPage(event.current)
    getWorkflowRuns(props.workflow.id, (event.current - 1)*10)
  }

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
        dataSource={workflowRuns}
        // loading={loading}
        size={"small"}
        // expandable={{
        //     expandedRowRender: notebookJobRun => parseNotebookLogs(notebookJobRun.logsJSON),
        //     expandRowByClick: true,
        //     expandIconColumnIndex: -1
        // }}
        pagination={{
          current: currentPage,
          pageSize: 10,
          total: total ? total : 0
        }}
        onChange={(event) => handleTableChange(event)}
      />
    </div>
  );
}
