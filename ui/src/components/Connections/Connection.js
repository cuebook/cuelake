import React, { useState, useEffect, useRef } from "react";
import { Table, Button, Form, Input, message, Tooltip, Drawer } from "antd";
import style from "./style.module.scss";
import { search } from "services/general.js";
import { Link } from "react-router-dom";
import connectionService from "services/connection.js";
import AddConnection from "./AddConnection.js";
import { EditOutlined, DeleteOutlined } from '@ant-design/icons';

const { Search } = Input;
const ButtonGroup = Button.Group;

export default function Connection() {
  const [connections, setConnections] = useState([]);
  const [selectedConnection, setSelectedConnection] = useState('');
  const [isConnectionDrawerVisible, setIsConnectionDrawerVisible] = useState('');

  useEffect(() => {
    if (!connections.length) {
        fetchConnections();
    }
  }, []);

  const fetchConnections = async () => {
    const response = await connectionService.getConnections();
    setConnections(response.data)
  }

  const deleteConnection = async (connection) => {
    const response = await connectionService.deleteConnection(connection.id);
    if(response.success){
        fetchConnections()
    }
    else{
        message.error(response.message)
    }
  }

  const editConnection = async () => {
    // TODO
  }

  const closeConnectionDrawer = () => {
    setIsConnectionDrawerVisible(false)
  }

  const openAddConnectionForm = () => {
    setIsConnectionDrawerVisible(true)
  }

  const onAddConnectionSuccess = async () => {
    closeConnectionDrawer();
    fetchConnections();
  }


    const columns = [
      {
        title: "Name",
        dataIndex: "name",
        key: "name"
      },
      {
        title: "Connection Type",
        dataIndex: "connectionType",
        key: "connectionType",
        render: (connectionType) => (
            <>
            <div className={style.connectionLogoTable} style={{backgroundImage: `url(${require("assets/img/" + connectionType + ".svg")})`}}>
            </div>
            {connectionType}
            </>
        )

      },
      {
        title: "",
        dataIndex: "",
        key: "",
        render: (text, connection) => (
         <div className={style.actions}>
            <Tooltip title={"Edit Connection"}>
              <EditOutlined onClick={() => editConnection(connection)} />
            </Tooltip>
            <Tooltip title={"Delete Connection"}>
              <DeleteOutlined onClick={() => deleteConnection(connection)} />
            </Tooltip>
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
                New Connection
            </Button>
        </div>
        <Table
            rowKey={"id"}
            scroll={{ x: "100%" }}
            columns={columns}
            dataSource={connections}
            pagination={false}
        />
        <Drawer
          title={"Add Connection"}
          width={720}
          onClose={closeConnectionDrawer}
          visible={isConnectionDrawerVisible}
        >
          { isConnectionDrawerVisible 
            ? 
            <AddConnection onAddConnectionSuccess={onAddConnectionSuccess} />
            :
            null
          }
      </Drawer>
    </div>
    );
  }
