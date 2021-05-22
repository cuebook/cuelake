import React, { useState, useEffect, useRef } from "react";
import TimeAgo from 'react-timeago';
import _ from "lodash";
import notebookService from "services/notebooks.js";
import style from "./style.module.scss";
import { useHistory } from "react-router-dom";
import {search} from "services/general.js"
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
import { MoreOutlined, PlayCircleOutlined, UnorderedListOutlined, StopOutlined, FileTextOutlined, DeleteOutlined, CopyOutlined, CloseOutlined, EditOutlined } from '@ant-design/icons';
import NotebookRunLogs from "./NotebookRunLogs.js"
import AddNotebook from "./AddNotebook.js"
import EditNotebook from "./EditNotebook.js"
import SelectSchedule from "components/Schedule/selectSchedule"
import { RUNNING, ABORT, FINISHED, ERROR, PENDING } from "./constants";
import { timehumanize } from 'services/general';

var moment = require("moment");
const { Option } = Select;
const {Search} = Input

export default function NotebookTable() {

  const [sortedInfo , setSortedInfo] = useState({});
  const [limit, setLimit] = useState(25);
  const [isAsc, setAsc] = useState()
  const [searchText, setSearchText] = useState('');
  const [onSort, setOnSort] = useState("");
  const [filterNotebook, setFilterNotebook] = useState([]);
  const [allNotebooks, setAllNotebooks] = useState([]);
  const [notebooks, setNotebooks] = useState([]);
  const [podsDriver, setpodsDriver] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState('');
  const [selectedNotebook, setSelectedNotebook] = useState('');
  const [scheduleName, setScheduleName] = useState('');
  const [runLogNotebook, setRunLogNotebook] = useState('');
  const [isRunLogsDrawerVisible, setIsRunLogsDrawerVisible] = useState(false);
  const [isNewNotebookDrawerVisible, setIsNewNotebookDrawerVisible] = useState(false);
  const [editNotebookDrawerId, setEditNotebookDrawer] = useState(null);
  const history = useHistory();
  const currentPageRef = useRef(currentPage);
  currentPageRef.current = currentPage;
  
  useEffect(() => {
    if (!notebooks.length) {
        getNotebooks(0);
    }

    const refreshNotebookInterval = setInterval(() => {
      refreshNotebooks((currentPageRef.current - 1)*25)
    }, 3000);

    const refreshPodStatus = setInterval(() => {
      refreshDriverStatus()
    }, 3000);

    return () => {
      clearInterval(refreshNotebookInterval);
      clearInterval(refreshPodStatus);
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

  const getAllNotebook = async (offset, value, columnToSort , sortOrder) => {
    if(_.isEmpty(searchText) && _.isEmpty(value) && _.isEmpty(columnToSort)){
      setSearchText(value)
      setOnSort(columnToSort)
      setAsc(sortOrder)
      return
    }
    setLoading(true)
    const response = await notebookService.getAllNotebooks(offset, limit, value, columnToSort, sortOrder );
    if(response){
      setFilterNotebook(response);
    }
    else{
      setFilterNotebook([0])
    }
    setLoading(false)
  };

  const refreshNotebooks = async (offset) => {
    const response = await notebookService.getNotebooks(offset);
    if(response){
      setNotebooks(response);
    }
  };

  const refreshDriverStatus = async () => {
    const response = await notebookService.getDriverAndExecutorStatus();
    if(response){
      setpodsDriver(response)
    }
  };
  const showScheduleDropDown = (notebookId) => {
    setSelectedNotebook(notebookId)
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
      getNotebooks((currentPage - 1)*25)
    }
    else{
      alert('Schedule not selected')
    }
  }

  const handleTableChange = (event, filter, sorter) => {
    setSortedInfo(sorter)
    setOnSort(sorter.columnKey)
    setAsc(sorter.order)
    setCurrentPage(event.current)
    setLimit(event.current*25)
    if (sorter.column){

      getAllNotebook((event.current - 1)*25, searchText, sorter.columnKey, sorter.order)
    }
    if(event){
      getNotebooks((event.current - 1)*25)
  }
}

  const navigateToNotebook = (record) => {
    if(history.location.pathname.indexOf("api/redirect") !== -1)
      history.push("/api/redirect/cuelake/notebook/" + record.id);
    else
      history.push("/notebook/" + record.id);
  } 

  const openRunLogs = (notebook) => {
    setRunLogNotebook(notebook)
    setIsRunLogsDrawerVisible(true)
  }

  const closeRunLogsDrawer = () => {
    setIsRunLogsDrawerVisible(false)
  }

  const unassignSchedule = async (notebookId) => {
    const response = await notebookService.unassignSchedule(notebookId);
    if(response.success){
      refreshNotebooks((currentPage - 1)*25)
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
      refreshNotebooks((currentPage - 1)*25)
    }
    else{
      message.error(response.message)
    }
  }

  const archiveNotebook = async (notebook) => {
    const response = await notebookService.archiveNotebook(notebook.id, notebook.name.substring(1))
    if(response.success){
      message.success("Notebook " + notebook.name.substring(1) + " moved to archive")
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
      refreshNotebooks((currentPage - 1)*25)
    }
    else{
      message.error(response.message)
    }
  }

  const onNotebookToggleChange = async (event, notebook) => {
    const response = await notebookService.toggleNotebookSchedule(event, notebook.id)
    if(response.success){
      refreshNotebooks((currentPage - 1)*25)
    }
    else{
      message.error(response.message)
    }
  }

  const closeNewNotebookDrawer = () => {
    setIsNewNotebookDrawerVisible(false)
  }

  const openNewNotebookDrawer = () => {
    setIsNewNotebookDrawerVisible(true)
  }

  const closeEditNotebookDrawer = () => {
    setEditNotebookDrawer(null)
  }

  const openEditNotebookDrawer = notebookObjId => {
    setEditNotebookDrawer(notebookObjId)
  }

  const onAddNotebookSuccess = () => {
    refreshNotebooks((currentPage - 1)*25)
    closeNewNotebookDrawer()
    closeEditNotebookDrawer()
  }


 const search = value => {
  setSearchText(value)
   if (_.isEmpty(value) ){
     setFilterNotebook([])
     return
   }
    getAllNotebook(0, value, onSort, isAsc)
  };

  const columns = [
    {
      title: "Notebook",
      dataIndex: "name",
      key: "name",
      width: "20%",
      sorter: ()=>{},
      sortOrder: sortedInfo.columnKey === 'name' && sortedInfo.order,
      ellipsis: true,

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
      sorter: ()=>{},
      sortOrder: sortedInfo.columnKey === 'schedule' && sortedInfo.order,
      ellipsis: true,
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
                <SelectSchedule onChange={addNotebookSchedule} />
                :
                <a className={style.linkText} onClick={()=>showScheduleDropDown(notebook.id)}>Assign Schedule</a>
              }
            </>
          );
        }
      }
    },

    {
      title: "Workflow",
      dataIndex: "assignedWorkflow",
      key: "assignedWorkflow",
      assign:"left",

      sorter: ()=>{},
      sortOrder: sortedInfo.columnKey === 'assignedWorkflow' && sortedInfo.order,
      ellipsis: true,
      // width: "10%",
      render: (text,record) => {
        var listIndividuals = record && record.lastRun && record.lastRun.assignedWorkflow && record.lastRun.assignedWorkflow.map(e => {
          return (
            <span
              style={{
                whiteSpace: "initial",
                marginRight: "5px",
                background: "#f4f5f6",
                borderRadius: "4px",
                padding: "1px 5px"
              }}
              key={e}
            >
              {e}
            </span>
          );
        });
        return (
          <div>
            {listIndividuals}
          </div>
        )
      }
    },
    {
      title: "Latest Run",
      dataIndex: "lastRun",
      key: "lastRun1",
      width: "10%",
      sorter: ()=>{},
      sortOrder: sortedInfo.columnKey === 'lastRun1' && sortedInfo.order,
      ellipsis: true,
      render: lastRun => {
        let timeDiff;
        if (lastRun && lastRun.startTimestamp && lastRun.endTimestamp){
          timeDiff = Math.round((new Date(lastRun.endTimestamp) - new Date(lastRun.startTimestamp))/1000)

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
          {lastRun ? <TimeAgo date={lastRun.startTimestamp} /> : null}
            <div style={{fontSize:"12px"}}> 
            {diff}
            </div>
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
      title: "Latest Run Status",
      dataIndex: "lastRun",
      key: "lastRun2",
      width: "15%",

      sorter: ()=>{},
      sortOrder: sortedInfo.columnKey === 'lastRun2' && sortedInfo.order,
      ellipsis: true,
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
            if(paragraph.status === FINISHED) paragraphClassName = "bg-green-500";
            else if(paragraph.status === ERROR) paragraphClassName = "bg-red-500";
            else if(paragraph.status === RUNNING) paragraphClassName = "bg-blue-400";
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
      render: (notebook, text) => {
        const menu = (<Menu>
            <Menu.Item key="0" onClick={() => cloneNotebook(notebook)} >
              <CopyOutlined />
              Clone Notebook
            </Menu.Item>
            <Menu.Divider />
            <Menu.Item key="1" onClick={() => archiveNotebook(notebook)} >
              <i className="fa fa-archive"></i>{"  "}
              Archive Notebook
            </Menu.Item>
            <Menu.Divider />
            <Menu.Item key="2">
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
            <Menu.Item key="3" onClick={() => openRunLogs(notebook)} >
              <UnorderedListOutlined />
              View Run Logs
            </Menu.Item>
          </Menu>
        )
        return (
          <div className={style.actions}>
            { notebook.notebookObjId ?
            <Tooltip title={"Edit"}>
                <EditOutlined onClick={() => openEditNotebookDrawer(notebook.notebookObjId)} />
            </Tooltip>
            :
            null              
            }
            { notebook.lastRun && (notebook.lastRun.status === RUNNING ||  notebook.lastRun.status === PENDING)
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

  let runningDrivers = podsDriver.runningDrivers
  let pendingDrivers = podsDriver.pendingDrivers
  let runningExecutors = podsDriver.runningExecutors
  let pendingExecutors = podsDriver.pendingExecutors
  let drivers = []
  _.times(runningDrivers, (i) => {
    drivers.push(<i className="fas fa-circle ml-2 icon-driver-1 red" style={{color:"green",fontSize:"12px"}}  key={i}></i>);
  });
  _.times(pendingDrivers, (i) => {
    drivers.push(<i className="fas fa-circle ml-2 icon-driver-2 " style={{color:"orange",fontSize:"12px"}}key={i} ></i>);
  });

  let executors = []

  _.times(runningExecutors, (i) => {
    executors.push(<i className="fas fa-circle ml-2 icon-driver-1 red" style={{color:"green",fontSize:"12px"}} key={i}></i>);
  });
  _.times(pendingExecutors, (i) => {
    executors.push(<i className="fas fa-circle ml-2 icon-driver-2 " style={{color:"orange",fontSize:"12px"}}key={i} ></i>);
  });
  return (
    <>

    <div className={style.flexContainer}  >

      <Button
          key="createTag"
          type="primary"
          onClick={() => openNewNotebookDrawer()}
      >
          New Notebook
      </Button>

      <div className={style.driversAndExecutoresStyle}>
      <div className={style.podStyle}>Drivers : {drivers.length > 0 ? drivers : 0 }</div>
      <div className={style.podStyle}>Executors : {executors.length > 0 ? executors : 0}</div>
      </div>
    <div className={style.actionBar}>

      <Search
            style={{ margin: "0 0 10px 0" , width:350}}
            placeholder="Search"
            enterButton="Search"
            
            onSearch={search}
            className="mr-2"
          />
      </div>

    </div>
      <Table
        rowKey={"id"}
        scroll={{ x: "100%" }}
        columns={columns}
        onChange={handleTableChange}
        dataSource={  filterNotebook.length == 0 ? notebooks.notebooks : filterNotebook.notebooks}
        loading={loading}
        size={"small"}
        pagination={{
          current: currentPage,
          pageSize:25,
          total:  filterNotebook.length != 0 ? filterNotebook.count :(notebooks ? notebooks.count : 0) 
        }}
      />
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
      <Drawer
          title={"Edit Notebook"}
          width={720}
          onClose={closeEditNotebookDrawer}
          visible={editNotebookDrawerId}
          bodyStyle={{ paddingBottom: 80 }}
        >
          { editNotebookDrawerId 
            ? 
            <EditNotebook onAddNotebookSuccess={onAddNotebookSuccess} notebookObjId={editNotebookDrawerId}></EditNotebook>
            :
            null
          }
      </Drawer>
    </>
  );
}
