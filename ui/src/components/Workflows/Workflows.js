import React, { useState, useEffect, useRef } from "react";
import style from "./style.module.scss";
import Moment from 'react-moment';
import _ from "lodash";
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
    Switch,
    Tabs
  } from "antd";
import { EditOutlined, PlayCircleOutlined, UnorderedListOutlined, StopOutlined, FileTextOutlined, DeleteOutlined, CopyOutlined} from '@ant-design/icons';
import { Badge } from "reactstrap";
import WorkflowRuns from "./WorkflowRuns"
import SelectSchedule from "components/Schedule/selectSchedule"

import workflowsService from "services/workflows";
import notebookService from "services/notebooks";

const { TabPane } = Tabs;
const { Option } = Select;

export default function Workflows(props) {
    const [workflows, setWorkflows] = useState([]);
    const [loading, setLoading] = useState(false);
    const [notebooksLight, setNotebooksLight] = useState([])
    const [total, setTotal] = useState('');
    const [currentPage, setCurrentPage] = useState(1);

    const [selectedWorkflow, setSelectedWorkflow] = useState('');
    const [selectedSchedule, setSelectedSchedule] = useState(null);
    const [selectedNotebooks, setSelectedNotebooks] = useState([]);

    const [isRunLogsDrawerVisible, setIsRunLogsDrawerVisible] = useState(false);
    const [isWorkflowModalVisible, setIsWorkflowModalVisible] = useState(false);

    const [newWorkflowName, setNewWorkflowName] = useState('');
    const [triggerWorkflow, setTriggerWorkflow] = useState(false);
    const [triggerWorkflowStatus, setTriggerWorkflowStatus] = useState("always");

    const currentPageRef = useRef(currentPage);
    currentPageRef.current = currentPage;

    const getWorkflows = async (offset) => {
      setLoading(true)
      const response = await workflowsService.getWorkflows(offset);
      if(response){
        setWorkflows(response.workflows);
        setTotal(response.Total)
      }
      setLoading(false)
      if(!offset) setCurrentPage(1)
    };

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
      const refreshWorkflowsInterval = setInterval(() => {
        refreshWorkflows((currentPageRef.current - 1)*10)
      }, 3000);

      return () => {
        clearInterval(refreshWorkflowsInterval);
      };
    }, []);

    const refreshWorkflows = async (offset) => {
      const response = await workflowsService.getWorkflows(offset);
      if(response){
        setWorkflows(response.workflows);
        setTotal(response.total);
      }
    };

    const handleTableChange = (event) => {
      setCurrentPage(event.current)
      getWorkflows((event.current - 1)*10)
    }

    const getNotebooksLight = async () => {
      if (_.isEmpty(notebooksLight)){
        const response = await notebookService.getNotebooksLight();
        if(response){
          setNotebooksLight(response);
        }
      }
    }

    const addWorkflow = () => {
      getNotebooksLight()
      setIsWorkflowModalVisible(true)
      setSelectedWorkflow('')
    }

    const editWorkflow = workflow => {
      getNotebooksLight()
      setIsWorkflowModalVisible(true)
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
          schedule: selectedSchedule,
          triggerWorkflowId: triggerWorkflow ? triggerWorkflow.id : null,
          triggerWorkflowStatus: triggerWorkflowStatus
        }
        const response = await workflowsService.setWorkflows(data);
        if(response){
          setIsWorkflowModalVisible(false)
          settingIntialValues()
        }
      }
      else{
        message.error('Please fill values');
      }
    }

    const handleCancel = () => {
      setIsWorkflowModalVisible(false)
      settingIntialValues()
    }

    const settingIntialValues = () => {
      setSelectedWorkflow("")
      setNewWorkflowName(false)
      setSelectedNotebooks([])
      setSelectedSchedule(null)
      setTriggerWorkflow(false)
      setTriggerWorkflowStatus("always")
    }

    const showNotebooksOfWorkflow = workflow => {
      const notebookNames = notebooksLight.filter(notebook => workflow.notebooks.find(x => x==notebook.id)).map(notebook => notebook.path.substring(1))
      return <span>{notebookNames.join(", ")}</span>
    }

    const columns = [
      {
        title: "Workflow",
        dataIndex: "name",
        key: "workflow",
        render: text => {
          return (
            <span>
              {text}
            </span>
          );
        }
      },
      {
        title: "Triggers On",
        children: [
          {
            title: 'Workflow',
            dataIndex: "triggerWorkflow",
            key: "triggerWorkflow",
            render: (text, record) => {
              return (
                <span>
                  {text ? text.name + " " : ""}
                  {text ?         
                    <Badge
                      color="primary"
                      className={`m-1 ${style.badge}`}
                      pill
                      key={record.id}
                    >{record.triggerWorkflowStatus}</Badge> : null
                  }
                </span>
              );
            }
          },
          {
            title: 'Schedule',
            dataIndex: "schedule",
            key: "schedule",
            render: (text, record) => {
              return (
                <span>
                  {text ? text.name: ""}
                </span>
              );
            }
          }
        ],
      },
      {
        title: "Last run",
        dataIndex: "lastRun",
        key: "lastRun",
        sorter: (a, b) => {
          return Math.abs(
            new Date(a.lastRun) - new Date(b.lastRun)
          );
        },
        defaultSortOrder: "descend",
        render: text => {
          return (
            <span>
            {text ? <Moment format="DD-MM-YYYY hh:mm:ss">{text}</Moment> : null}
            </span>
          );
        }
      },
      {
        title: "Actions",
        dataIndex: "",
        key: "",
        // width: "10%",
        render: (text, record) => {
          return (
            <div className={style.actions}>
              {/* { notebook.lastRun && (notebook.lastRun.status === "RUNNING" ||  notebook.lastRun.status === "PENDING")
                ?
                <Tooltip title={"Stop Notebook"}> 
                  <StopOutlined onClick={() => stopNotebook(notebook)} />
                </Tooltip>
                :
                <Tooltip title={"Run Notebook"}> 
                  <PlayCircleOutlined onClick={() => runNotebook(notebook)} />
                </Tooltip>
              }
              */}
              <Tooltip title={"Edit Workflow"}>
                <EditOutlined onClick={() => editWorkflow(record)} />
              </Tooltip>
              <Tooltip title={"View Runs"}>
                <UnorderedListOutlined onClick={() => openRunLogs(record)} />
              </Tooltip>
            </div>
          );
        }
    }
    ]

    const workflowOptionElements = workflows.map(workflow => 
      <Option value={workflow.id} workflow={workflow} key={workflow.id}> {workflow.name} </Option>
    )

    const statuses = ["success", "failure", "always"]
    const statusOptionElements = statuses.map(status => 
        <Option value={status} key={status}> {status} </Option>
      )

    const notebooksLightElement = notebooksLight && notebooksLight.map(notebook => 
        <Option value={notebook.id} key={notebook.id} name={notebook.path.substring(1)}> {notebook.path.substring(1)} </Option>
      )

    const editCreateWorkflowElement = <Modal 
              title={true ? "Add Workflow" : "EditWorkflow"}
              visible={true}
              onOk={saveWorkflow}
              onCancel={handleCancel}
              okText="Save"
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
                          <Form.Item label="Workflow Name">
                            <Select placeholder="Select Workflow" value={triggerWorkflow ? triggerWorkflow.id : ""} onChange={(value, option) => setTriggerWorkflow(option.workflow)}>
                              {workflowOptionElements}
                            </Select>
                          </Form.Item>
                          <Form.Item label="Workflow Status">
                            <Select onChange={(value) => setTriggerWorkflowStatus(value)} value={triggerWorkflowStatus} defaultValue="always">
                              {statusOptionElements}
                            </Select>
                          </Form.Item>
                        </TabPane>
                      </Tabs>
                  </Form.Item>
                </Form>
            </Modal>

    return (
        <div>
            <Button 
              onClick={()=>addWorkflow()}
              type="primary"
              >
              Add Workflow
            </Button>
            { isWorkflowModalVisible ? editCreateWorkflowElement : null }
            <Table
                rowKey={"id"}
                scroll={{ x: "100%" }}
                columns={columns}
                dataSource={workflows}
                // showHeader={false}
                loading={loading}
                size={"small"}
                expandable={{
                    expandedRowRender: record => showNotebooksOfWorkflow(record),
                    expandRowByClick: true,
                    expandIconColumnIndex: -1
                }}
                pagination={{
                  current: currentPage,
                  pageSize: 10,
                  total: total ? total : 0
                }}
                onChange={(event) => handleTableChange(event)}
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