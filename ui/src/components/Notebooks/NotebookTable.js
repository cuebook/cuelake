import React, { useState, useEffect, useRef } from "react";
import notebookService from "services/notebooks.js";
import style from "./style.module.scss";
import { useHistory } from "react-router-dom";
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
import { EditOutlined, PlayCircleOutlined, UnorderedListOutlined, StopOutlined} from '@ant-design/icons';
import NotebookRunLogs from "./NotebookRunLogs.js"

const { Option } = Select;

export default function NotebookTable() {
  const [notebooks, setNotebooks] = useState('');
  const [schedules, setSchedules] = useState('');
  const [timezones, setTimezones] = useState('');
  const [loading, setLoading] = useState('');
  const [currentPage, setCurrentPage] = useState('');
  const [selectedNotebook, setSelectedNotebook] = useState('');
  const [runLogNotebook, setRunLogNotebook] = useState('');
  const [cronTabSchedule, setCronTabSchedule] = useState('');
  const [selectedTimezone, setSelectedTimezone] = useState('');
  const [isAddScheduleModalVisible, setIsAddScheduleModalVisible] = useState('');
  const [isRunLogsDrawerVisible, setIsRunLogsDrawerVisible] = useState('');
  const history = useHistory();
  const currentPageRef = useRef(currentPage);
  currentPageRef.current = currentPage;

  useEffect(() => {
    if (!notebooks) {
        getNotebooks(0);
    }
    if (!schedules) {
      getSchedules();
    }
    if (!timezones) {
      getTimezones();
    }

    const refreshNotebookInterval = setInterval(() => {
      refreshNotebooks((currentPageRef.current - 1)*10)
    }, 3000);

    return () => {
      clearInterval(refreshNotebookInterval);
    };
  }, []);

  const getNotebooks = async (offset) => {
    setLoading(true)
    const response = await notebookService.getNotebooks(offset);
    setNotebooks(response);
    setLoading(false)
    if(!offset) setCurrentPage(1)
  };

  const refreshNotebooks = async (offset) => {
    const response = await notebookService.getNotebooks(offset);
    setNotebooks(response);
  };

  const getSchedules = async () => {
    const response = await notebookService.getSchedules();
    setSchedules(response);
  };

  const getTimezones = async () => {
    const response = await notebookService.getTimezones();
    setTimezones(response);
  }

  const showScheduleDropDown = (notebookId) => {
    setSelectedNotebook(notebookId)
  }

  const saveSchedule = async (event) => {
    if(cronTabSchedule, selectedTimezone){
      const response = await notebookService.addSchedule(cronTabSchedule, selectedTimezone);
      if(response.success){
        setCronTabSchedule("")
        setSelectedTimezone("")
        setIsAddScheduleModalVisible(false)
        getSchedules()
      }
      else{
        message.error(response.message);
      }
    }
    else{
      message.error('Please fill values');
    }
  }

  const addNotebookSchedule = async (selectedSchedule) => {
    if(selectedSchedule && selectedNotebook && selectedSchedule !== -1){
      const response = await notebookService.addNotebookSchedule(selectedNotebook, selectedSchedule);
      if(response.success){
        message.success(response.message)
      }
      else{
        message.error(response.message)
      }
      setSelectedNotebook(null)
      getNotebooks((currentPage - 1)*10)
    }
    else{
      alert('Schedule not selected')
    }
  }

  const handleScheduleChange = (event) => {
    if(event === "Add Schedule"){
      setIsAddScheduleModalVisible(true)
      setSelectedNotebook(false)
    }
    else{
      addNotebookSchedule(event)
    }
  }

  const handleTableChange = (event) => {
    setCurrentPage(event.current)
    getNotebooks((event.current - 1)*10)
  }

  const navigateToNotebook = (record) => {
    history.push("/notebook/" + record.id);
  }

  const openRunLogs = (notebook) => {
    setRunLogNotebook(notebook)
    setIsRunLogsDrawerVisible(true)
  }

  const closeRunLogsDrawer = () => {
    setIsRunLogsDrawerVisible(false)
  }

  const runNotebook = async (notebook) => {
    const response = await notebookService.runNotebook(notebook.id)
    if(response.success)
      message.success("Notebook " + notebook.name.substring(1) + " ran successfully")
    else{
      message.error(response.message)
    }
  }

  const stopNotebook = async (notebook) => {
    const response = await notebookService.stopNotebook(notebook.id)
    if(response.success)
      message.success("Notebook " + notebook.name.substring(1) + " stopped successfully")
    else{
      message.error(response.message)
    }
  }

  const onNotebookToggleChange = async (event, notebook) => {
    const response = await notebookService.toggleNotebookSchedule(event, notebook.id)
    if(response.success){
      refreshNotebooks((currentPage - 1)*10)
    }
    else{
      message.error(response.message)
    }
  }

  const handleCancel = () => {
    setIsAddScheduleModalVisible(false)
  }

  let scheduleOptionsElement = []
  if(schedules){
    scheduleOptionsElement.push(<Option value={"Add Schedule"} key={"0"}>Add Schedule</Option>)
    schedules.forEach(schedule => {
      scheduleOptionsElement.push(<Option value={schedule.id} key={schedule.id}>{schedule.schedule}</Option>)
    })
  }

  let timezoneElements = []
  if(timezones){
    timezones.forEach(tz => {
      timezoneElements.push(<Option value={tz} key={tz}>{tz}</Option>)
    })
  }

  const columns = [
    {
      title: "Notebook",
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
      title: "Schedule",
      dataIndex: "schedule",
      key: "schedule",
      width: "20%",
      render: (schedule, notebook) => {
        if(schedule && selectedNotebook != notebook.id){
          return (
            <>
            { notebook.isScheduled ?
            <Switch size="small" checked={notebook.isActive} onChange={(event) => onNotebookToggleChange(event, notebook)} />
            :
            null
          }
            <div className={style.scheduleText} onClick={()=>showScheduleDropDown(notebook.id)}>
              <span>{schedule}</span>
              <span className={style.icon}><EditOutlined /></span>
            </div>
            </>
          )
        }
        else{
          return (
            <>
              { 
                selectedNotebook == notebook.id ?
                <Select defaultValue="Select Cron Schedule" style={{ width: 250 }} onChange={handleScheduleChange}>
                  {scheduleOptionsElement}
                </Select>
                :
                <a className={style.linkText} onClick={()=>showScheduleDropDown(notebook.id)}>Add Schedule</a>
              }
            </>
          );
        }
      }
    },
    {
      title: "Last Run",
      dataIndex: "paragraphs",
      key: "paragraphs",
      width: "25%",
      render: (text, notebook) => {
        const lastRunStatusChildElements = []
        if(notebook && notebook.paragraphs){
          const paragraphPercent = 100/(notebook.paragraphs.length)
          notebook.paragraphs.forEach(paragraph => {
            let paragraphClassName = ""
            if(paragraph.status === "FINISHED" || paragraph.status === "READY") paragraphClassName = "bg-green-500";
            else if(paragraph.status === "ERROR") paragraphClassName = "bg-red-500";
            else if(paragraph.status === "RUNNING") paragraphClassName = "bg-blue-400";
            else if(paragraph.status === "ABORT") paragraphClassName = "bg-yellow-500";
            let content = 
              <div className={style.tooltip}>
                {paragraph.started ? <p>Start Time: {paragraph.started}</p> : null}
                {paragraph.finished ? <p>End Time: {paragraph.finished}</p> : null}
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
        }
        return (
          <div className="overflow-hidden h-2 mt-2 mb-2 text-xs flex rounded-sm bg-blue-200 w-full">
            {lastRunStatusChildElements}
          </div>
        );
      }
    },
    {
      title: "",
      dataIndex: "",
      key: "",
      width: "10%",
      render: (notebook, text) => {
        return (
          <div className={style.actions}>
            { notebook.isRunning 
              ?
              <Tooltip title={"Stop Notebook"}> 
                <StopOutlined onClick={() => stopNotebook(notebook)} />
              </Tooltip>
              :
              <Tooltip title={"Run Notebook"}> 
                <PlayCircleOutlined onClick={() => runNotebook(notebook)} />
              </Tooltip>
            }
            <Tooltip title={"Edit Notebook"}>
              <EditOutlined onClick={() => navigateToNotebook(notebook)} />
            </Tooltip>
            <Tooltip title={"View Run Logs"}>
              <UnorderedListOutlined onClick={() => openRunLogs(notebook)} />
            </Tooltip>
          </div>
        );
      }
    }
  ];

  return (

    <>
      <Table
        rowKey={"id"}
        scroll={{ x: "100%" }}
        columns={columns}
        dataSource={notebooks.notebooks}
        loading={loading}
        pagination={{
          current: currentPage,
          pageSize: 10,
          total: notebooks ? notebooks.count : 0
        }}
        onChange={(event) => handleTableChange(event)}
      />
      <Modal 
        title="Add Schedule" 
        visible={isAddScheduleModalVisible}
        onOk={saveSchedule}
        onCancel={handleCancel}
        okText="Save"
      >
          <Form layout={"vertical"}>
            <Form.Item label="Crontab Schedule (m/h/dM/MY/d)">
              <Input placeholder="* * * * *" onChange={(event) => setCronTabSchedule(event.target.value)}/>
            </Form.Item>
            <Form.Item label="Timezone">
              <Select onChange={(value) => setSelectedTimezone(value)}>
                {timezoneElements}
              </Select>
            </Form.Item>
          </Form>
      </Modal>
      <Drawer
          title={(runLogNotebook ? runLogNotebook.name.substring(1) : "")}
          width={720}
          onClose={closeRunLogsDrawer}
          visible={isRunLogsDrawerVisible}
          bodyStyle={{ paddingBottom: 80 }}
          footer={
            <div
              style={{
                textAlign: 'right',
              }}
            >
              <Button onClick={closeRunLogsDrawer} style={{ marginRight: 8 }}>
                Close
              </Button>
            </div>
          }
        >
          { isRunLogsDrawerVisible 
            ? 
            <NotebookRunLogs notebook={runLogNotebook}></NotebookRunLogs>
            :
            null
          }
      </Drawer>
    </>
  );
}
