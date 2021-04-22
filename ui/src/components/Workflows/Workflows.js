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
import { EditOutlined, PlayCircleOutlined, UnorderedListOutlined, StopOutlined, FileTextOutlined, DeleteOutlined, CopyOutlined} from '@ant-design/icons';
import { Badge } from "reactstrap";
import WorkflowRuns from "./WorkflowRuns"
import workflowsService from "services/workflows";

export default function Workflows(props) {
    const [workflows, setWorkflows] = useState([]);
    const [loading, setLoading] = useState(false);
    const [total, setTotal] = useState('');
    const [currentPage, setCurrentPage] = useState(1);
    const [selectedWorkflow, setSelectedWorkflow] = useState('');
    const [isRunLogsDrawerVisible, setIsRunLogsDrawerVisible] = useState(false);
    const [isWorkflowModalVisible, setIsWorkflowModalVisible] = useState(false);

    const [cronTabSchedule, setCronTabSchedule] = useState('');
    const [selectedTimezone, setSelectedTimezone] = useState('');

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
      // if (!notebooks.length) {
      //     getNotebooks(0);
      // }
      // if (!schedules.length) {
      //   getSchedules();
      // }
      // if (!timezones) {
      //   getTimezones();
      // }

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

    const addWorkflow = () => {
      setIsWorkflowModalVisible(true)
      setSelectedWorkflow('')
    }

    const editWorkflow = workflow => {
      setIsWorkflowModalVisible(true)
      setSelectedWorkflow(workflow)
    }

    const saveWorkflow = (data) => {
      setIsWorkflowModalVisible(false)
      setSelectedWorkflow('')
    }

    const saveSchedule = async (event) => {
      if(cronTabSchedule, selectedTimezone){
        // const response = await notebookService.addSchedule(cronTabSchedule, selectedTimezone);
        // if(response.success){
        //   setCronTabSchedule("")
        //   setSelectedTimezone("")
        //   getSchedules()
        // }
        // else{
        //   message.error(response.message);
        // }
      }
      else{
        message.error('Please fill values');
      }
    }

    const handleCancel = () => {
      setIsWorkflowModalVisible(false)
      setSelectedWorkflow('')
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
        dataIndex: "dependsOnWorkflow",
        key: "dependsOn",
        render: (text, record) => {
          return (
            <span>
              {text ? text + " " : ""}
              {text ?         
                <Badge
                  color="primary"
                  className={`m-1 ${style.badge}`}
                  pill
                  key={record.id}
                >{record.dependsOnWorkflowStatus}</Badge> : null
              }
            </span>
          );
        }
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
              {/* 
              TODO
              Add edit functionality from UI
              <Tooltip title={"Edit Notebook"}>
                <EditOutlined onClick={() => navigateToNotebook(notebook)} />
              </Tooltip> */}
              <Tooltip title={"View Runs"}>
                <UnorderedListOutlined onClick={() => openRunLogs(record)} />
              </Tooltip>
            </div>
          );
        }
    }
    ]

    return (
        <div>
            <Button 
              onClick={()=>addWorkflow()}
              type="primary"
              >
              Add Workflow
            </Button>
            <Modal 
              title={true ? "Add Workflow" : "EditWorkflow"}
              visible={isWorkflowModalVisible}
              onOk={saveWorkflow}
              onCancel={handleCancel}
              okText="Save"
            >
                <Form layout={"vertical"}>
                  <Form.Item label="Crontab Schedule (m/h/dM/MY/d)">
                    <Input placeholder="* * * * *" onChange={(event) => setCronTabSchedule(event.target.value)}/>
                  </Form.Item>
                  <Form.Item label="Timezone">
                    <Select onChange={(value) => setSelectedTimezone(value)}>
                      {"timezoneElements"}
                    </Select>
                  </Form.Item>
                </Form>
            </Modal>
            <Table
                rowKey={"id"}
                scroll={{ x: "100%" }}
                columns={columns}
                dataSource={workflows}
                // showHeader={false}
                loading={loading}
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