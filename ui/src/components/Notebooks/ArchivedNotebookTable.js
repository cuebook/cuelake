import React, { useState, useEffect } from "react";
import _ from "lodash";
import notebookService from "services/notebooks.js";
import style from "./style.module.scss";
import {
  Table,
  Tooltip,
  message,
} from "antd";
import { UndoOutlined, DeleteOutlined, LoadingOutlined, BackwardFilled } from '@ant-design/icons';

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
    }, 3000);

    return () => {
      clearInterval(refreshNotebookInterval);
    };
  }, []);

  const getNotebooks = async () => {
    setLoading(true)
    const response = await notebookService.getArchivedNotebooks();
    if(response){
      setNotebooks(response);
    }
    setLoading(false)
  };

  const refreshNotebooks = async () => {
    const response = await notebookService.getArchivedNotebooks();
    if(response){
      setNotebooks(response);
    }
  };

  const unarchiveNotebook = async (notebook) => {
    setUnarchivingNotebook(notebook.id)
    const response = await notebookService.unarchiveNotebook(notebook.id, notebook.path.split("/")[2])
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
    const response = await notebookService.deleteNotebook(notebook.id)
    if(response.success){
      message.success("Notebook " + notebook.name.substring(1) + " deleted successfully");
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
            {unarchivingNotebook && unarchivingNotebook == notebook.id ? 
            <LoadingOutlined />
            : 
            <Tooltip title={"Unarchive Notebook"}>
              <UndoOutlined onClick={() => unarchiveNotebook(notebook)} />
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
        <a className={style.notebookLinkText} onClick={() => props.hideArchivedNotebooksTable() }><BackwardFilled />  Notebooks</a>
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