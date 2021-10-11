import React, { useState, useEffect, useRef } from "react";
import style from "./style.module.scss";
import TimeAgo from 'react-timeago';
import _ from "lodash";
import {
    Table,
    Button,
    Modal,
    Input,
    Select,
    Tooltip,
    Form,
    message,
    Drawer,
    Tabs,
    Menu, 
    Dropdown,
    Popconfirm,
  } from "antd";
import { MoreOutlined, EditOutlined, PlayCircleOutlined, UnorderedListOutlined, StopOutlined, DeleteOutlined, CloseOutlined} from '@ant-design/icons';
import { Badge } from "reactstrap";
import WorkflowRuns from "./WorkflowRuns"
import SelectSchedule from "components/Schedule/selectSchedule"

import workflowsService from "services/workflows";
import notebookService from "services/notebooks";
import { timehumanize } from 'services/general';
import { STATUS_ALWAYS, STATUS_ERROR, STATUS_SUCCESS, STATUS_RUNNING, STATUS_RECEIVED } from "./constants"

var moment = require("moment");

const { TabPane } = Tabs;
const { Option } = Select;

export default function Workflows(props) {

    const [limit] = useState(25);
    const [sortedInfo, setSortedInfo] = useState({})
    const [sortOrder, setSortOrder] = useState('')
    const [sortColumn, setSortColumn] = useState('');
    const [workflows, setWorkflows] = useState([]);
    const [loading, setLoading] = useState(false);
    const [notebooksLight, setNotebooksLight] = useState([])
    const [totalWokflows, setTotal] = useState('');
    const [currentPage, setCurrentPage] = useState('');
    const [selectedWorkflow, setSelectedWorkflow] = useState('');
    const [selectedSchedule, setSelectedSchedule] = useState(null);
    const [selectedNotebooks, setSelectedNotebooks] = useState([]);
    const [isRunLogsDrawerVisible, setIsRunLogsDrawerVisible] = useState(false);
    const [isEditCreateWorkflow, setIsEditCreateWorkflow] = useState(false);
    const [newWorkflowName, setNewWorkflowName] = useState('');
    const [triggerWorkflow, setTriggerWorkflow] = useState(false);
    const [triggerWorkflowStatus, setTriggerWorkflowStatus] = useState(STATUS_ALWAYS);
    const [assignTriggerWorkflowForId, setAssignTriggerWorkflowForId] = useState(false)         // stores id of parent workflow 
    const [assignSchedule, setAssignSchedule] = useState(false)
    const [componentDidMount, setComponentDidMount] = useState(false)
    const sortOrderRef = useRef(sortOrder);
    sortOrderRef.current = sortOrder;
    const sortColumnRef = useRef(sortColumn);
    sortColumnRef.current = sortColumn;
    const currentPageRef = useRef(currentPage);
    currentPageRef.current = currentPage;

    const getWorkflows = async (offset) => {
      setLoading(true)
      let workspaceId = parseInt(localStorage.getItem("workspaceId"))
      const response = await workflowsService.getWorkflows(workspaceId, offset, limit, sortColumnRef.current, sortOrderRef.current);
      if(response){
        setWorkflows(response.workflows);
        setTotal(response.total)
      }
      setLoading(false)
      if(!offset) setCurrentPage(1)
    };

    const refreshWorkflows = async (sortColumn = sortColumnRef.current, sortOrder = sortOrderRef.current, currentPage = currentPageRef.current) => {
      if(currentPageRef.current){
      let workspaceId = parseInt(localStorage.getItem("workspaceId"))
      const response = await workflowsService.getWorkflows(workspaceId, (currentPage - 1)*limit, limit, sortColumn, sortOrder);
      if(response){
        setWorkflows(response.workflows);
        setTotal(response.total)
      }
    };
  }

    const openRunLogs = workflow => {
        setSelectedWorkflow(workflow)
        setIsRunLogsDrawerVisible(true)
    }

    const closeWorkflowRunsDrawer = () => {
        setIsRunLogsDrawerVisible(false)
        setSelectedWorkflow('')
    }
    
    useEffect(() => {
      getNotebooksLight()
      getWorkflows(0)
      if (!componentDidMount){ refreshWorkflows(); setComponentDidMount(true)}
      const refreshWorkflowsInterval = setInterval(refreshWorkflows, 3000);

      return () => {
        clearInterval(refreshWorkflowsInterval);
      };
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const handleTableChange = (event, filter, sorter) => {
      setSortedInfo(sorter)
      setSortColumn(sorter.columnKey)
      setSortOrder(sorter.order)
      setCurrentPage(event.current)
      refreshWorkflows(sorter.columnKey, sorter.order, event.current)

    }

    const getNotebooksLight = async () => {
      let WorkspaceId = parseInt(localStorage.getItem("workspaceId"))
      if (_.isEmpty(notebooksLight)){
        const response = await notebookService.getNotebooksLight(WorkspaceId);
        if(response){
          setNotebooksLight(response);
        }
      }
    }

    const addWorkflow = () => {
      getNotebooksLight()
      setIsEditCreateWorkflow(true)
      setSelectedWorkflow('')
    }

    const editWorkflow = workflow => {
      getNotebooksLight()
      setIsEditCreateWorkflow(true)
      setSelectedWorkflow(workflow)
      setSelectedNotebooks(workflow.notebooks)

      if (workflow.schedule){
        setSelectedSchedule(workflow.schedule.id)
      }

      setNewWorkflowName(workflow.name)
      setTriggerWorkflow(workflow.triggerWorkflow)
      setTriggerWorkflowStatus(workflow.triggerWorkflowStatus)
    }

    const saveWorkflow = async () => {
      if(!_.isEmpty(newWorkflowName)){
        const data = {
          id: selectedWorkflow.id,
          name: newWorkflowName,
          notebookIds: selectedNotebooks,
          scheduleId: selectedSchedule,
          triggerWorkflowId: triggerWorkflow ? triggerWorkflow.id : null,
          triggerWorkflowStatus: triggerWorkflowStatus
        }
        let WorkspaceId = parseInt(localStorage.getItem("workspaceId"))
        const response = await workflowsService.setWorkflows(data, WorkspaceId);
        if(response){
          setIsEditCreateWorkflow(false)
          settingInitialValues()
        }
      }
      else{
        message.error('Please fill values');
      }
      refreshWorkflows()
    }

    const handleCancel = () => {
      setIsEditCreateWorkflow(false)
      settingInitialValues()
    }

    const settingInitialValues = () => {
      setSelectedWorkflow("")
      setNewWorkflowName('')
      setSelectedNotebooks([])
      setSelectedSchedule(null)
      setTriggerWorkflow(false)
      setTriggerWorkflowStatus(STATUS_ALWAYS)
      setAssignSchedule(false)
      setAssignTriggerWorkflowForId(false)
    }

    const showNotebooksOfWorkflow = workflow => {
      // Parent workflow removed from assign Workflow
      const notebookNames = notebooksLight.filter(notebook => workflow.notebooks.find(x => x===notebook.id)).map(notebook => notebook.path.substring(1))
      return <span><b>Notebooks: </b>{notebookNames.join(", ")}</span>
    }

    const runWorkflow = async workflow => {
      await workflowsService.runWorkflow(workflow.id);
      refreshWorkflows()
    }

    const stopWorkflow = async workflow => {
      await workflowsService.stopWorkflow(workflow.lastRun.workflowRunId);
      refreshWorkflows()
    }

    const deleteWorkflow = async workflow => {
      await workflowsService.deleteWorkflow(workflow.id);
      refreshWorkflows()
    }

    const columns = [
      {
        title: "Workflow",
        dataIndex: "name",
        key: "name",
      sorter: ()=>{},
      sortOrder: sortedInfo.columnKey === 'name' && sortedInfo.order,
      ellipsis: true,
        render: text => {
          return (
            <span>
              {text}
            </span>
          );
        }
      },
      {
        title: 'Trigger Workflow',
        dataIndex: "triggerWorkflow",
        key: "triggerWorkflow",
        sorter: ()=>{},
        sortOrder: sortedInfo.columnKey === 'triggerWorkflow' && sortedInfo.order,
        ellipsis: true,
        render: (text, workflow) => {
          if (workflow.triggerWorkflow){
              return (
                <span className={style.triggerWorkflow}>
                  {text ? text.name + " " : ""}
                  {text ?         
                    <Badge
                      color="primary"
                      className={`m-1 ${style.badge}`}
                      pill
                      key={workflow.id}
                    >{workflow.triggerWorkflowStatus}</Badge> : null
                  }
                  <Tooltip title={"Unassign Workflow"}> 
                    <span className={style.icon} onClick={()=>updateAssignedTriggerWorkflow(workflow.id)}><CloseOutlined /></span>
                  </Tooltip>
                </span>
              );

          }
          else {
            if (assignTriggerWorkflowForId && assignTriggerWorkflowForId === workflow.id){
              return <Modal
                        title={"Assign Trigger Workflow"}
                        visible={true}
                        onOk={()=>updateAssignedTriggerWorkflow(workflow.id)}
                        onCancel={settingInitialValues}
                        okText="Save"
                        bodyStyle={{ paddingBottom: 80 }}
                      >
                        {selectTriggerWorkflowElement}
                      </Modal>
            } else {
              return <a href={() => false} className={style.linkText} onClick={()=>setAssignTriggerWorkflowForId(workflow.id)}>Assign Workflow</a>
            }
          }
        }
      },
      {
        title: 'Schedule',
        dataIndex: "schedule",
        key: "schedule",
        sorter: ()=>{},
        sortOrder: sortedInfo.columnKey === 'schedule' && sortedInfo.order,
        ellipsis: true,
        render: (text, workflow) => {
          if (workflow.schedule){
              return (
                <span className={style.scheduleText}>
                  {text ? text.name + " " : ""}
                  <Tooltip title={"Unassign Workflow"}> 
                    <span className={style.icon} onClick={()=>updateAssignedSchedule(workflow.id, null)}><CloseOutlined /></span>
                  </Tooltip>
                </span>
              );

          }
          else {
            if (assignSchedule && assignSchedule === workflow.id){
              return <SelectSchedule onChange={(value)=>{updateAssignedSchedule(workflow.id, value)}} />
            } else {
              return <a href={() => false} className={style.linkText} onClick={()=>setAssignSchedule(workflow.id)}>Assign Schedule</a>
            }
          }          
        }
      },
      {
        title: "Last run",
        dataIndex: "lastRun",
        key: "lastRunTime",
        align:"left",
        sorter: ()=>{},
        sortOrder: sortedInfo.columnKey === 'lastRunTime' && sortedInfo.order,
        ellipsis: true,
        defaultSortOrder: "descend",
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
        if(diff){
          diff = timehumanize(diff.split(" "))
        }
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
            <div>
              {item} 
           </div>
          );
        }
      },
      {
        title: "Last run status",
        dataIndex: "lastRun",
        key: "lastRunStatus",
        sortOrder: sortedInfo.columnKey === 'lastRunStatus' && sortedInfo.order,
        ellipsis: true,
        render: lastRun => {
          return (
            <span>
              {lastRun ? lastRun.status : null}
            </span>
          );
        }
      },
      {
        title: "",
        dataIndex: "",
        key: "",
        // width: "10%",
        render: (text, workflow) => {
          const menu = (<Menu>
              <Menu.Item key="1">
                <Popconfirm
                    title={"Are you sure to delete "+ workflow.name +"?"}
                    onConfirm={() => deleteWorkflow(workflow)}
                    okText="Yes"
                    cancelText="No"
                >
                <DeleteOutlined />
                  Delete Workflow
                </Popconfirm>
              </Menu.Item>
              <Menu.Divider />
              <Menu.Item key="2" onClick={() => openRunLogs(workflow)} >
                <UnorderedListOutlined />
                View Runs
              </Menu.Item>
            </Menu>
          )

          return (
            <div className={style.actions}>
              { workflow.lastRun && (workflow.lastRun.status === STATUS_RUNNING ||  workflow.lastRun.status === STATUS_RECEIVED)
                ?
                <Tooltip title={"Stop Workflow"}> 
                  <StopOutlined onClick={() => stopWorkflow(workflow)} />
                </Tooltip>
                :
                <Tooltip title={"Run Workflow"}> 
                  <PlayCircleOutlined onClick={() => runWorkflow(workflow)} />
                </Tooltip>
              }
             
              <Tooltip title={"Edit Workflow"}>
                <EditOutlined onClick={() => editWorkflow(workflow)} />
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
    ]

    const updateAssignedTriggerWorkflow = async (workflowId) => {
      const data = {
        triggerWorkflowId: triggerWorkflow ? triggerWorkflow.id : null,
        triggerWorkflowStatus: triggerWorkflowStatus
      }

      const response = await workflowsService.updateTriggerWorkflow(workflowId, data);
      if (response){settingInitialValues() }
      refreshWorkflows()
    }

    const updateAssignedSchedule = async (workflowId, scheduleId) => {
      const data = {
          scheduleId: scheduleId
      }
      const response = await workflowsService.updateWorkflowSchedule(workflowId, data);
      if (response){settingInitialValues() }
      refreshWorkflows()
    }
    const workflowOptionElements = workflows.filter(workflow=>!((selectedWorkflow && workflow.id === selectedWorkflow.id) || (workflow.id === assignTriggerWorkflowForId))).map(workflow => 
      <Option value={workflow.id} workflow={workflow} key={workflow.id}> {workflow.name} </Option>
    )

    const statuses = [STATUS_SUCCESS, STATUS_ERROR, STATUS_ALWAYS]
    const statusOptionElements = statuses.map(status => 
        <Option value={status} key={status}> {status} </Option>
      )

    const notebooksLightElement = notebooksLight && notebooksLight.map(notebook => 
        <Option value={notebook.id} key={notebook.id} name={notebook.path.substring(1)}> {notebook.path.substring(1)} </Option>
      )

    const selectTriggerWorkflowElement = <><Form.Item label="Workflow Name">
                            <Select placeholder="Select Workflow" value={triggerWorkflow ? triggerWorkflow.id : ""} onChange={(value, option) => setTriggerWorkflow(option.workflow)}>
                              {workflowOptionElements}
                            </Select>
                          </Form.Item>
                          <Form.Item label="Workflow Status">
                            <Select onChange={(value) => setTriggerWorkflowStatus(value)} value={triggerWorkflowStatus}>
                              {statusOptionElements}
                            </Select>
                          </Form.Item></>


    const editCreateWorkflowElement = <Drawer 
              title={true ? "New Workflow" : "EditWorkflow"}
              width={720}
              visible={true}
              onOk={saveWorkflow}
              onClose={handleCancel}
              okText="Save"
              bodyStyle={{ paddingBottom: 80 }}
              footer={
                          <div
                            style={{
                              textAlign: 'right',
                            }}
                          >
                            <Button onClick={handleCancel} style={{ marginRight: 8 }}>
                              Cancel
                            </Button>
                            <Button onClick={saveWorkflow} type="primary">
                              Save
                            </Button>
                          </div>
                        }
            >
                <Form layout={"vertical"}>
                  <Form.Item label="Name">
                    <Input onChange={(event) => setNewWorkflowName(event.target.value)} value={newWorkflowName} placeholder="Sample Workflow">
                    </Input>
                  </Form.Item>
                  <Form.Item label="Notebooks">
                    <Select
                      mode="multiple"
                      allowClear
                      // style={{ width: '100%' }}
                      filterOption={(input, option) => 
                            option.props.name.toLowerCase().indexOf(input.toLowerCase()) >= 0 
                            || option.props.value.toLowerCase().indexOf(input.toLowerCase()) >= 0
                          }
                      placeholder="Please select notebooks"
                      value = {selectedNotebooks}
                      onChange={values=>setSelectedNotebooks(values)}
                    >
                      {notebooksLightElement}
                    </Select>
                  </Form.Item>
                  <Form.Item label="TRIGGERS ON">
                    <Tabs defaultActiveKey="1">
                        <TabPane
                          tab={
                            <span>
                              Schedule
                            </span>
                          }
                          key="1"
                        >
                          <SelectSchedule onChange={(value)=>setSelectedSchedule(value)} schedule={selectedSchedule}/>
                        </TabPane>
                        <TabPane
                          tab={
                            <span>
                              Workflow
                            </span>
                          }
                          key="2"
                        >
                          {selectTriggerWorkflowElement}
                        </TabPane>
                      </Tabs>
                  </Form.Item>
                </Form>
            </Drawer>

    return (
          <div>
            <div className={`d-flex flex-column justify-content-center text-right mb-2`}>
              <Button 
                onClick={()=>addWorkflow()}
                type="primary"
                >
                New Workflow
              </Button>
            </div>
            { isEditCreateWorkflow ? editCreateWorkflowElement : null }
            <Table
                rowKey={"id"}
                scroll={{ x: "100%" }}
                columns={columns}
                onChange={handleTableChange}
                dataSource={workflows}
                // showHeader={false}
                loading={loading}
                size={"small"}
                expandable={{
                    expandedRowRender: record => showNotebooksOfWorkflow(record),
                }}
                pagination={{
                  current: currentPage,
                  pageSize: limit,
                  showSizeChanger: false,
                  total: workflows ? totalWokflows : 0
                }}
            />
            <Drawer
                title={(selectedWorkflow ? selectedWorkflow.name : "")}
                width={720}
                onClose={closeWorkflowRunsDrawer}
                visible={isRunLogsDrawerVisible}
                bodyStyle={{ paddingBottom: 80 }}
                footer={
                  <div
                    style={{
                      textAlign: 'right',
                    }}
                  >
                    <Button onClick={closeWorkflowRunsDrawer} style={{ marginRight: 8 }}>
                      Close
                    </Button>
                  </div>
                }
              >
                { isRunLogsDrawerVisible 
                  ? 
                  <WorkflowRuns workflow={selectedWorkflow}></WorkflowRuns>
                  :
                  null
                }
            </Drawer>

        </div>
        )
}