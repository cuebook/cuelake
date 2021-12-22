import React, { useState, useEffect } from "react";
import notebookService from "services/notebooks.js";
import style from "./style.module.scss";
import {
  Table,
  Tooltip,
  message,
} from "antd";
import { RetweetOutlined, DeleteOutlined, LoadingOutlined, BackwardFilled } from '@ant-design/icons';

export default function NotebookTable(props) {
  const [notebooks, setNotebooks] = useState([]);
  const [loading, setLoading] = useState([]);
  const [unarchivingNotebook, setUnarchivingNotebook] = useState(false);

  useEffect(() => {
    if (!notebooks.length) {
        getNotebooks();
    }

    const refreshNotebookInterval = setInterval(() => {
      refreshNotebooks()
    }, 5000);

    return () => {
      clearInterval(refreshNotebookInterval);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const getNotebooks = async () => {
    setLoading(true)
    let workspaceId = parseInt(localStorage.getItem("workspaceId"))
    const response = await notebookService.getArchivedNotebooks(workspaceId);
    if(response){
      setNotebooks(response);
    }
    setLoading(false)
  };

  const refreshNotebooks = async () => {
    let workspaceId = parseInt(localStorage.getItem("workspaceId"))
    const response = await notebookService.getArchivedNotebooks(workspaceId);
    if(response){
      setNotebooks(response);
    }
  };

  const unarchiveNotebook = async (notebook) => {
    setUnarchivingNotebook(notebook.id)
    let workspaceId = parseInt(localStorage.getItem("workspaceId"))
    const response = await notebookService.unarchiveNotebook(notebook.id, notebook.path.split("/")[2], workspaceId)
    if(response.success){
      message.success("Notebook " + notebook.path.split("/")[2] + " removed from archive")
      refreshNotebooks()
    }
    else{
      message.error(response.message)
    setUnarchivingNotebook(false)
    }
  }

  const deleteNotebook = async (notebook) => {
    let workspaceId = parseInt(localStorage.getItem("workspaceId"))
    const response = await notebookService.deleteNotebook(notebook.id, workspaceId)
    if(response.success){
      message.success("Notebook " + notebook.path.split("/")[2] + " deleted successfully");
      refreshNotebooks()
    }
    else{
      message.error(response.message)
    }
  }

  const columns = [
    {
      title: "Archived Notebooks",
      dataIndex: "path",
      key: "path",
      width: "20%",
      render: text => {
        return (
          <span key={text}>
            {text.split("/")[2]}
          </span>
        );
      }
    },
    {
      title: "",
      dataIndex: "id",
      key: "id",
      width: "20%",
      render: (text, notebook) => {
        return (
          <div className={style.actions}>
            {unarchivingNotebook && unarchivingNotebook === notebook.id ? 
            <LoadingOutlined />
            : 
            <Tooltip title={"Unarchive Notebook"}>
              <RetweetOutlined onClick={() => unarchiveNotebook(notebook)} />
            </Tooltip>
              }
            <Tooltip title={"Delete Notebook"}>
              <DeleteOutlined onClick={() => deleteNotebook(notebook)} />
            </Tooltip>
          </div>          
        );
      }
    }
  ]

  return (
      <>
        <a href={() => false} className={style.notebookLinkText} onClick={() => props.hideArchivedNotebooksTable() }><BackwardFilled />  Notebooks</a>
        <Table
          rowKey={"id"}
          scroll={{ x: "100%" }}
          columns={columns}
          dataSource={notebooks}
          loading={loading}
          size={"small"}
          // onChange={(event) => handleTableChange(event)}
        />
      </>
    )

}