import React, { useState, useEffect, useRef } from "react";
import style from "./style.module.scss";
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

import notebookService from "services/notebooks.js";

export default function NotebookRunLogs(props) {

  const [notebookLogs, setNotebookLogs] = useState('');
  const [loading, setLoading] = useState('');
  const [currentPage, setCurrentPage] = useState('');
  
  useEffect(() => {
    if (!notebookLogs) {
        setCurrentPage(1)
        getNotebookLogs(props.notebook.notebookJobId, 0);
    }
  }, []);

  const getNotebookLogs = async (notebookJobId, offset) => {
    setLoading(true)
    const response = await notebookService.getNotebookLogs(notebookJobId, offset);
    setNotebookLogs(response);
    setLoading(false)
  };

  const viewLog = async (notebookJobRun) => {
    
  };

  const handleTableChange = (event) => {
    setCurrentPage(event.current)
    getNotebookLogs(props.notebook.notebookJobId, (event.current - 1)*10)
  }


  const parseNotebookLogs = (logsJSON) => {
      let logElements = []
      if(logsJSON && logsJSON.paragraphs){
        logsJSON.paragraphs.forEach(paragraph => {
            logElements.push(<div key={paragraph.id}> 
                <p>{paragraph.text}</p>
                <p>{JSON.stringify(paragraph.results)}</p>
                <p>Date Started: {paragraph.dateStarted}</p>
                <p>Date Finished: {paragraph.dateFinished}</p>
                <p>Status: {paragraph.status}</p>
                <div className={style.divider}></div>
                </div>
            )
        })
      }
      let logElement = <div className={style.logsDiv}>{logElements}</div>
      return logElement
  }

  const columns = [
    {
      title: "Start Time",
      dataIndex: "startTimestamp",
      key: "startTimestamp",
      width: "40%",
      render: text => {
        return (
          <span>
            {text}
          </span>
        );
      }
    },
    {
        title: "Status",
        dataIndex: "status",
        key: "status",
        width: "40%",
        render: text => {
          return (
            <span>
              {text}
            </span>
          );
        }
    },
    {
        title: "",
        dataIndex: "",
        key: "",
        width: "20%",
        render: (text, notebookJobRun) => {
          return (
            <a onClick={() => viewLog(notebookJobRun)}>View Logs</a>
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
        dataSource={notebookLogs.runStatuses}
        loading={loading}
        size={"small"}
        expandable={{
            expandedRowRender: notebookJobRun => parseNotebookLogs(notebookJobRun.logsJSON),
            expandRowByClick: true,
            expandIconColumnIndex: -1
        }}
        pagination={{
          current: currentPage,
          pageSize: 10,
          total: notebookLogs ? notebookLogs.count : 0
        }}
        onChange={(event) => handleTableChange(event)}
      />
    </div>
  );
}
