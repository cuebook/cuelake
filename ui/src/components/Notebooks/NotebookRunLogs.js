import React, { useState, useEffect } from "react";
import style from "./style.module.scss";
import Moment from 'react-moment';
import Ansi from "ansi-to-react";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-python";
import "ace-builds/src-noconflict/mode-java";
import "ace-builds/src-noconflict/mode-scala";
import "ace-builds/src-noconflict/mode-mysql";
import "ace-builds/src-noconflict/theme-twilight";
import { CheckCircleOutlined, MinusCircleOutlined, CloseCircleOutlined, ClockCircleOutlined, LoadingOutlined } from '@ant-design/icons';

import {
    Table,
    Popover,
  } from "antd";

import notebookService from "services/notebooks.js";
import { RUNNING, ABORT, ERROR, SUCCESS, PENDING } from "./constants";
import { timehumanize } from 'services/general';
var moment = require("moment");

export default function NotebookRunLogs(props) {

  const [notebookLogs, setNotebookLogs] = useState('');
  const [loading, setLoading] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  
  useEffect(() => {
    if (!notebookLogs) {
        setCurrentPage(1)
        getNotebookLogs(props.notebook.id, 0);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
    getNotebookLogs(props.notebook.id, (event.current - 1)*10)
  }


  const getStatusElement = (status) => {
    if(status === "FINISHED")
    return <CheckCircleOutlined style={{color: "#48bb78"}} />
    else if(status === "ERROR")
    return <CloseCircleOutlined style={{color: "#f56565"}} />
    else if(status === "RUNNING")
    return <LoadingOutlined style={{color: "#4299e1"}} />
    else if(status === "ABORT")
    return <MinusCircleOutlined style={{color: "#ecc94b"}} />
    else if(status === "PENDING")
    return <ClockCircleOutlined style={{color: "#63b3ed"}} />
  }


  const parseNotebookLogs = (logsJSON) => {
      let logElements = []
      if(logsJSON && logsJSON.paragraphs){
        logsJSON.paragraphs.forEach(paragraph => {
          let resultElements = []
          if(paragraph.results && paragraph.results.msg){
            paragraph.results.msg.forEach((element, index) => {
              if(element.type === "TEXT"){
                resultElements.push(<Ansi key={paragraph.id + "text" + index}>{element.data}</Ansi>)
              } else if(element.type === "HTML"){
                resultElements.push(<div dangerouslySetInnerHTML={{__html: element.data}} key={paragraph.id + "html" + index}></div>)
              } else if(element.type === "IMG"){
                resultElements.push(<img alt={paragraph.id} style={{maxHeight: '300px'}} key={paragraph.id + "img" + index} src={`data:image/png;base64,${element.data}`}  />)
              } else{
                resultElements.push(<p key={paragraph.id + "data" + index}>{element.data}</p>)
              }
            })
          }
          logElements.push(
            <div key={paragraph.id} className={style.paragraph}>
              <div className={style.line}></div>
              <div className={style.status}>
                <p>Started: {paragraph.dateStarted}</p>
                <p>Finished: {paragraph.dateFinished}</p>
                <div className={style.icon}>
                  {getStatusElement(paragraph.status)}
                </div>
              </div>
              <div className={style.logs}>
                <AceEditor
                  mode={(paragraph.config && paragraph.config.editorSetting && paragraph.config.editorSetting.language) ? paragraph.config.editorSetting.language : 'python'}
                  theme="twilight"
                  name={paragraph.id + "_code"}
                  highlightActiveLine={false}
                  showGutter={false}
                  maxLines={10000}
                  setOptions={{
                      showLineNumbers: false,
                      readOnly: true,
                      value: paragraph.text,
                      tabSize: 2,
                  }}
                  style={{
                      width: "100%"
                  }}
                />
                <div className={style.result}>{resultElements}</div>
              </div>
            </div>
          ) 
        })
      }
      let logElement = <div className={style.logsDiv}>{logElements}</div>
      return logElement
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
      title: "Run Timestamp",
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
      dataIndex: "",
      key: "",
      width: "10%",
      // align:"center",
      render: (text ,record) => {
        let timeDiff;
        if (record && record.startTimestamp && record.endTimestamp){
          timeDiff = Math.round((new Date(record.endTimestamp) - new Date(record.startTimestamp))/1000)

        }
        let diff;
        if (timeDiff){
          diff =  moment.duration(timeDiff, "second").format("h [hrs] m [min] s [sec]", {
            trim: "both"
        });
        }
        if(diff){
          diff = timehumanize(diff.split(" "))
        }
        let item = (
          <div> 
            {diff}
          </div>
        )
        return (
          <span>
            {item} 
          </span>
        );
      }
    },
    {
      title: "Run Paragraph Status",
      dataIndex: "logsJSON",
      key: "logsJSON",
      width: "40%",
      render: (logsJSON, runStatus) => {
        let lastRunStatusElement = null
        if(logsJSON && logsJSON.paragraphs){
          let paragraphs = logsJSON.paragraphs
          let lastRunStatusChildElements = []
          const paragraphPercent = 100/(paragraphs.length)
          paragraphs.forEach(paragraph => {
            let paragraphClassName = ""
            let paragraphStatus = ""
            if(paragraph.hasOwnProperty('results')){
              if(paragraph["results"].hasOwnProperty("code")){
                paragraphStatus = paragraph["results"]["code"]
              }
            }
            if(paragraphStatus === SUCCESS) paragraphClassName = "bg-green-500";
            else if(paragraph.status === ERROR) paragraphClassName = "bg-red-500";
            else if(paragraph.status === RUNNING) paragraphClassName = "bg-blue-400";
            else if(paragraph.status === PENDING) paragraphClassName = "bg-blue-300";
            else if(paragraph.status === ABORT) paragraphClassName = "bg-yellow-500";
            let content = 
              <div className={style.tooltip}>
                {paragraph.title ? <p><b>{paragraph.title}</b></p> : null}
                {paragraph.dateStarted ? <p>Start Time: {paragraph.dateStarted}</p> : null}
                {paragraph.dateFinished ? <p>End Time: {paragraph.dateFinished}</p> : null}
                {paragraph.status ? <p>Status: {paragraph.status}</p> : null}
                {paragraph.progress ? <p>Progress: {paragraph.progress}</p> : null}
              </div>
            lastRunStatusChildElements.push(
              <Popover content={content} key={paragraph.id}>
                <div 
                  style={{width: paragraphPercent + "%"}} 
                  data-tip data-for={paragraph.id} 
                  className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center notebook-paragraph-progressbar-box ${paragraphClassName}`}>
                </div>
              </Popover>
            )
          })
          lastRunStatusElement = <div className="overflow-hidden h-2 mt-2 mb-2 text-xs flex rounded-sm bg-blue-200 w-full">
            {lastRunStatusChildElements}
          </div>
        }
        return (
          lastRunStatusElement
        );
      }
    },
    {
        title: "",
        dataIndex: "",
        key: "",
        width: "10%",
        render: (text, notebookJobRun) => {
          return (
            <a href={() => false} onClick={() => viewLog(notebookJobRun)}>Logs</a>
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
        dataSource={notebookLogs.notebookRunLogs}
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
