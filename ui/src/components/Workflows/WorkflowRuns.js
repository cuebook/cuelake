import React, { useState, useEffect, useRef } from "react";
import style from "./style.module.scss";
import TimeAgo from 'react-timeago';
import {
    Table,
  } from "antd";

import workflowsService from "services/workflows.js";
import { timehumanize } from 'services/general';
var moment = require("moment");

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
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
      render: text => {
        return (
          <span>
            {text}
          </span>
        );
      }
    },
    {
      title: "Last Run",
      dataIndex: "startTimestamp",
      key: "startTimestamp",
      render: text => {
        return (
          <span>
            <TimeAgo date={text} />
          </span>
        );
      }
    },
    {
      title: "Duration",
      dataIndex: "endTimestamp",
      key: "duration",
      align:"center",
      render:(text, record) => {

        let timeDiff;
        if (record && record.startTimestamp && record.endTimestamp){
          timeDiff = Math.round((new Date(record.endTimestamp) - new Date(record.startTimestamp))/1000)

        }
        let diff;
        if (timeDiff){
          diff =  moment.duration(timeDiff, "second").format("h [h] m [min] s [sec]", {
            trim: "both"
        });
        if(diff){
          diff = timehumanize(diff.split(" "))
        }
        }
      
          let item = (
            <div> 
              <div> 
                {diff}
              </div>
            </div>
          )
          return (
            <div>
              {item} 
              </div>
            
          );
        }
    },
  ]

  return (
    <div className={style.runLogTable}>
      <Table
        rowKey={"id"}
        scroll={{ x: "100%" }}
        columns={columns}
        dataSource={workflowRuns}
        loading={loading}
        size={"small"}
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
