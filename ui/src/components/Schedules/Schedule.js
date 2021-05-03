import React, { useState, useEffect } from "react";
import { Table, Button, Popconfirm, Input, message, Tooltip, Drawer } from "antd";
import style from "./style.module.scss";
import notebookService from "services/notebooks.js";
import ViewConnection from "components/Connections/ViewConnection.js"
import AddSchedule from "components/Schedules/AddSchedule.js"
import { EyeOutlined, DeleteOutlined , EditOutlined} from '@ant-design/icons';



export default function Schedule(){

const [schedules, setSchedules] = useState([]);
const [selectedConnection, setSelectedConnection] = useState('');
const [isAddConnectionDrawerVisible, setIsAddConnectionDrawerVisible] = useState('');
const [isViewConnectionDrawerVisible, setIsViewConnectionDrawerVisible] = useState('');

    useEffect(() => {
    if (!schedules.length) {
        fetchSchedules();
    }
  }, []);

  const fetchSchedules = async () => {
    const response = await notebookService.getSchedules();
    setSchedules(response)
  }

  const deleteConnection = async (connection) => {
    const response = await notebookService.deleteSchedule(connection.id);
    if(response.success){
        fetchSchedules()
    }
    else{
        message.error(response.message)
    }
  }

  const viewConnection = async (connection) => {
    setSelectedConnection(connection)
    setIsViewConnectionDrawerVisible(true)
  }

  const closeAddConnectionDrawer = () => {
    setIsAddConnectionDrawerVisible(false)
  }

  const closeViewConnectionDrawer = () => {
    setIsViewConnectionDrawerVisible(false)
  }

  const openAddConnectionForm = () => {
    setIsAddConnectionDrawerVisible(true)
  }

  const onAddConnectionSuccess = async () => {
    closeAddConnectionDrawer();
    fetchSchedules();
  }

  const columns = [
    {
      title: "Name",
      dataIndex: "name",
      key: "name"
    },
    {
      title: "Schedule",
      dataIndex: "schedule",
      key: "schedule",
    
    },

    {
        title: "Assigned Notebook",
        dataIndex: "",
        key: "",
      
      },
    {
      title: "",
      dataIndex: "",
      key: "",
      render: (text, schedule) => (
       <div className={style.actions}>
           
          <Tooltip title={"Edit Schedule"}>
            <EditOutlined onClick={() => viewConnection(schedule)} />
          </Tooltip>
          
          <Popconfirm
              title={"Are you sure to delete "+ schedule.name +"?"}
              onConfirm={() => deleteConnection(schedule)}
              // onCancel={cancel}
              okText="Yes"
              cancelText="No"
          >
              <Tooltip title={"Delete Connection"}>
                  <DeleteOutlined />
              </Tooltip>
          </Popconfirm>
        </div>
      )
    }
  ];



  return (
    <div>
        <div className={`d-flex flex-column justify-content-center text-right mb-2`}>
            <Button
                key="createTag"
                type="primary"
                onClick={() => openAddConnectionForm()}
            >
                New Schedule
            </Button>
        </div>
        <Table
            rowKey={"id"}
            scroll={{ x: "100%" }}
            columns={columns}
            dataSource={schedules}
            pagination={false}
        />
        <Drawer
          title={"Add Connection"}
          width={720}
          onClose={closeAddConnectionDrawer}
          visible={isAddConnectionDrawerVisible}
        >
          { isAddConnectionDrawerVisible 
            ? 
            <AddSchedule onAddConnectionSuccess={onAddConnectionSuccess} />
            :
            null
          }
        </Drawer> 
         <Drawer
          title={selectedConnection.name}
          width={720}
          onClose={closeViewConnectionDrawer}
          visible={isViewConnectionDrawerVisible}
        >
          { isViewConnectionDrawerVisible 
            ? 
            <ViewConnection connection={selectedConnection} />
            :
            null
          }
        </Drawer>
    </div>
    );



} 