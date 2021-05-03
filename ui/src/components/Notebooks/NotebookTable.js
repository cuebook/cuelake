import React, { useState, useEffect, useRef } from "react";
import TimeAgo from 'react-timeago';
import notebookService from "services/notebooks.js";
import style from "./style.module.scss";
import { useHistory } from "react-router-dom";
import {
  Table,
  Button,
  Modal,
  Input,
  Select,
  Tooltip,
  Popover,
  Form,
  message,
  Drawer,
  Popconfirm,
  Switch,
  Menu, 
  Dropdown
} from "antd";
import { MoreOutlined, PlayCircleOutlined, UnorderedListOutlined, StopOutlined, FileTextOutlined, DeleteOutlined, CopyOutlined, CloseOutlined } from '@ant-design/icons';
import NotebookRunLogs from "./NotebookRunLogs.js"
import AddNotebook from "./AddNotebook.js"

const { Option } = Select;

export default function NotebookTable() {
  const [notebooks, setNotebooks] = useState([]);
  const [schedules, setSchedules] = useState([]);
  const [timezones, setTimezones] = useState('');
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState('');
  const [selectedNotebook, setSelectedNotebook] = useState('');
  const [scheduleName, setScheduleName] = useState('');
  const [runLogNotebook, setRunLogNotebook] = useState('');
  const [cronTabSchedule, setCronTabSchedule] = useState('');
  const [selectedTimezone, setSelectedTimezone] = useState('');
  const [isAddScheduleModalVisible, setIsAddScheduleModalVisible] = useState(false);
  const [isRunLogsDrawerVisible, setIsRunLogsDrawerVisible] = useState(false);
  const [isNewNotebookDrawerVisible, setIsNewNotebookDrawerVisible] = useState(false);
  const history = useHistory();
  const currentPageRef = useRef(currentPage);
  currentPageRef.current = currentPage;

  useEffect(() => {
    if (!notebooks.length) {
        getNotebooks(0);
    }
    if (!schedules.length) {
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
    if(response){
      setNotebooks(response);
    }
    setLoading(false)
    if(!offset) setCurrentPage(1)
  };

  const refreshNotebooks = async (offset) => {
    const response = await notebookService.getNotebooks(offset);
    if(response){
      setNotebooks(response);
    }
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
    if(cronTabSchedule, selectedTimezone, scheduleName){
      const response = await notebookService.addSchedule(cronTabSchedule, selectedTimezone, scheduleName);
      if(response.success){
        setCronTabSchedule("")
        setSelectedTimezone("")
        setScheduleName("")
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

  const unassignSchedule = async(notebookId) => {
    const response = await notebookService.unassignSchedule(notebookId);
    if(response.success){
      refreshNotebooks((currentPage - 1)*10)
    }
    else{
      message.error(response.message)
    }
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

  const cloneNotebook = async (notebook) => {
    const response = await notebookService.cloneNotebook(notebook.id, notebook.name.substring(1) + " Copy")
    if(response.success){
      message.success("Notebook " + notebook.name.substring(1) + " cloned successfully")
      refreshNotebooks((currentPage - 1)*10)
    }
    else{
      message.error(response.message)
    }
  }

  const deleteNotebook = async (notebook) => {
    const response = await notebookService.deleteNotebook(notebook.id)
    if(response.success){
      message.success("Notebook " + notebook.name.substring(1) + " deleted successfully");
      refreshNotebooks((currentPage - 1)*10)
    }
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

  const closeNewNotebookDrawer = () => {
    setIsNewNotebookDrawerVisible(false)
  }

  const openNewNotebookDrawer = () => {
    setIsNewNotebookDrawerVisible(true)
  }

  const onAddNotebookSuccess = () => {
    refreshNotebooks((currentPage - 1)*10)
    closeNewNotebookDrawer()
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
            <div className={style.scheduleText}>
              <span>{schedule}</span>
              <Tooltip title={"Unassign Schedule"}> 
                <span className={style.icon} onClick={()=>unassignSchedule(notebook.id)}><CloseOutlined /></span>
              </Tooltip>
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
                <a className={style.linkText} onClick={()=>showScheduleDropDown(notebook.id)}>Assign Schedule</a>
              }
            </>
          );
        }
      }
    },
    {
      title: "Latest Run",
      dataIndex: "lastRun",
      key: "lastRun",
      width: "10%",
      render: (lastRun) => {
        return (
          <span>
            {lastRun ? <TimeAgo date={lastRun.startTimestamp} /> : ""}
          </span>
        );
      }
    },
    {
      title: "Latest Run Status",
      dataIndex: "lastRun",
      key: "lastRun",
      width: "10%",
      render: (lastRun) => {
        return (
          <span>
            {lastRun ? lastRun.status : ""}
          </span>
        );
      }
    },
    {
      title: "Last Run",
      dataIndex: "lastRun",
      key: "lastRun",
      width: "15%",
      render: (lastRun, notebook) => {
        let lastRunStatusElement = null
        if(lastRun && lastRun.logsJSON && lastRun.logsJSON.paragraphs){
          let paragraphs = lastRun.logsJSON.paragraphs
          let lastRunStatusChildElements = []
          const paragraphPercent = 100/(paragraphs.length)
          paragraphs.forEach(paragraph => {
            let paragraphClassName = ""
            if(paragraph.status === "FINISHED") paragraphClassName = "bg-green-500";
            else if(paragraph.status === "ERROR") paragraphClassName = "bg-red-500";
            else if(paragraph.status === "RUNNING") paragraphClassName = "bg-blue-400";
            else if(paragraph.status === "ABORT") paragraphClassName = "bg-yellow-500";
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
      render: (notebook, text) => {
        const menu = (<Menu>
            <Menu.Item key="0" onClick={() => cloneNotebook(notebook)} >
              <CopyOutlined />
              Clone Notebook
            </Menu.Item>
            <Menu.Divider />
            <Menu.Item key="1">
              <Popconfirm
                  title={"Are you sure to delete "+ notebook.name.substring(1) +"?"}
                  onConfirm={() => deleteNotebook(notebook)}
                  okText="Yes"
                  cancelText="No"
              >
              <DeleteOutlined />
                Delete Notebook
              </Popconfirm>
            </Menu.Item>
            <Menu.Divider />
            <Menu.Item key="2" onClick={() => openRunLogs(notebook)} >
              <UnorderedListOutlined />
              View Run Logs
            </Menu.Item>
          </Menu>
        )
        return (
          <div className={style.actions}>
            { notebook.lastRun && (notebook.lastRun.status === "RUNNING" ||  notebook.lastRun.status === "PENDING")
              ?
              <Tooltip title={"Stop Notebook"}> 
                <StopOutlined onClick={() => stopNotebook(notebook)} />
              </Tooltip>
              :
              <Tooltip title={"Run Notebook"}> 
                <PlayCircleOutlined onClick={() => runNotebook(notebook)} />
              </Tooltip>
            }
            {/* 
            TODO
            Add edit functionality from UI
            <Tooltip title={"Edit Notebook"}>
              <EditOutlined onClick={() => navigateToNotebook(notebook)} />
            </Tooltip> */}
            <Tooltip title={"Notebook"}>
              <FileTextOutlined onClick={() => navigateToNotebook(notebook)} />
            </Tooltip>
            <Tooltip title={"More"}>
              <Dropdown overlay={menu} trigger={['click']}>
                <MoreOutlined />
              </Dropdown>
            </Tooltip>
          </div>
        );
      }
    }
  ];

  return (

    <>
      <div className={`d-flex flex-column justify-content-center text-right mb-2`}>
          <Button
              key="createTag"
              type="primary"
              onClick={() => openNewNotebookDrawer()}
          >
              New Notebook
          </Button>
      </div>
      <Table
        rowKey={"id"}
        scroll={{ x: "100%" }}
        columns={columns}
        dataSource={notebooks.notebooks}
        loading={loading}
        size={"small"}
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
            <Form.Item label="Schedule Name">
              <Input placeholder="Scheduler Name" onChange={(event) => setScheduleName(event.target.value)} />
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
      <Drawer
          title={"New Notebook"}
          width={720}
          onClose={closeNewNotebookDrawer}
          visible={isNewNotebookDrawerVisible}
          bodyStyle={{ paddingBottom: 80 }}
        >
          { isNewNotebookDrawerVisible 
            ? 
            <AddNotebook onAddNotebookSuccess={onAddNotebookSuccess}></AddNotebook>
            :
            null
          }
      </Drawer>
    </>
  );
}
