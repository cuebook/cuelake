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
    Icon,
    Tooltip,
    Form,
    message,
    Drawer,
    Row,
    Col,
    Switch,
    Tabs,
    Menu, 
    Popconfirm,
    Dropdown,
    Upload
  } from "antd";
import { UploadOutlined, MoreOutlined, EditOutlined, PlayCircleOutlined, UnorderedListOutlined, StopOutlined, FileTextOutlined, DeleteOutlined, CopyOutlined, CloseOutlined} from '@ant-design/icons';
import { Badge } from "reactstrap";
import filesService from "services/files";
import { formatBytes } from "utils";
import apiService from "services/api";

const { TabPane } = Tabs;
const { Option } = Select;

export default function FilesTable(props) {
    const [files, setFiles] = useState([]);
    const [uploadFiles, setUploadFiles] = useState([])
    const [loading, setLoading] = useState(false);
    const [componentDidMount, setComponentDidMount] = useState(false)

    useEffect(() => {
        if (!componentDidMount){ refreshFiles(); setComponentDidMount(true)}
        const refreshFilesInterval = setInterval(refreshFiles, 10000);
        return () => {
          clearInterval(refreshFilesInterval);
        };
    }, []);

    const deleteFile = async (file) => {
        const response = await filesService.deleteFile(file.Key)
        refreshFiles()
    }

    const refreshFiles = async () => {
        setLoading(true)
        const response = await filesService.getFiles(0);
        if(response){
          setFiles(response);
        }
        setLoading(false)
    }

    const columns = [
      {
        title: "File",
        dataIndex: "Key",
        key: "Key",
        sorter:(a,b)=>{return a.Key.localeCompare(b.Key)},
        render: text => {
          return (
            <span>
              {text}
            </span>
          );
        }
      },
      {
        title: "Last Modified",
        dataIndex: "LastModified",
        key: "LastModified",
        sorter:(a,b)=>{return a.LastModified.localeCompare(b.LastModified)},
        render: text => {
          return (
            <span>
              <TimeAgo date={text} />
            </span>
          );
        }
      },
      {
        title: "Size",
        dataIndex: "Size",
        key: "Size",
        sorter:(a,b)=>a.Size - b.Size,
        render: text => {
          return (
            <span>
              {formatBytes(text,2)}
            </span>
          );
        }
      },
      {
        title: "Actions",
        dataIndex: "Key",
        key: "actions",
        render: (text, file) => {
          return (
            <div className={style.actions}>
              <Popconfirm
                  title={"Are you sure to delete "+ file.Key +"?"}
                  onConfirm={() => deleteFile(file)}
                  okText="Yes"
                  cancelText="No"
              >
              <Tooltip title={"Delete File"}>
              <DeleteOutlined />
              </Tooltip>
              </Popconfirm>
            </div>
          );
        }
      }
    ]

    const uploadProps = {
      name: 'file',
      action: apiService.base_url + "files/file",
      headers: {
        authorization: 'authorization-text',
      },
      fileList: uploadFiles,
      onChange(info, fileList) {
        setUploadFiles(fileList)
        if (info.file.status !== 'uploading') {
        }
        if (info.file.status === 'done') {
          message.success(`${info.file.name} file uploaded successfully`);
          refreshFiles()
        } else if (info.file.status === 'error') {
          message.error(`${info.file.name} file upload failed.`);
        }
      },
    };

    return <div>
        <div className={`d-flex flex-column justify-content-center text-right mb-2`}>
            <Upload {...uploadProps}>
              <Button type="primary" icon={<UploadOutlined />}>Upload File</Button>
            </Upload>
        </div>
        <Table
            rowKey={"id"}
            scroll={{ x: "100%" }}
            columns={columns}
            dataSource={files}
            // showHeader={false}
            loading={loading}
            size={"small"}
            pagination={{
              pageSize: 25
            }}
        />
    </div>
}