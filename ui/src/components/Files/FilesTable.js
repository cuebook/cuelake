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


const { TabPane } = Tabs;
const { Option } = Select;

export default function FilesTable(props) {
    const [files, setFiles] = useState([]);
    const [loading, setLoading] = useState(false);
    const [uploading, setUploading] = useState(false);
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

    const uploadFile = async (file) => {
        setUploading(true)
        const response = await filesService.uploadFile(file, file.name)
        setUploading(false)
        refreshFiles()
    }

    const columns = [
      {
        title: "File",
        dataIndex: "Key",
        key: "Key",
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
        render: text => {
          return (
            <span>
              {text}
            </span>
          );
        }
      },
      {
        title: "Size",
        dataIndex: "Size",
        key: "Size",
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
      maxCount: 1,
      beforeUpload: (file) => {
        uploadFile(file)
        return false;
      },
      fileList: [],
      status: "uploading",
      onChange: () => {
        return {
            file: {
               uid: 'uid',      // unique identifier, negative is recommend, to prevent interference with internal generated id
               name: 'xx.png',   // file name
               status: 'uploading', // options：uploading, done, error, removed. Intercepted file by beforeUpload don't have status field.
               response: '{"status": "success"}', // response from server
               linkProps: '{"download": "image"}', // additional html props of file link
               xhr: 'XMLHttpRequest{ ... }', // XMLHttpRequest Header
            }
        }
      }
    };


    return <div>
        <div className={`d-flex flex-column justify-content-center text-right mb-2`}>
            <Upload {...uploadProps} files>
                <Button 
                    icon={<UploadOutlined />}
                    type="primary"
                    loading={uploading}
                >
                    Upload File
                </Button>
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
        />
    </div>
}