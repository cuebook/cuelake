import React, { useState, useEffect, useContext } from 'react';
import TimeAgo from 'react-timeago';
import style from "./style.module.scss";
import { Tree } from 'antd';
import Moment from 'react-moment';
import { CarryOutOutlined, FormOutlined, DatabaseOutlined, TableOutlined, BorderlessTableOutlined } from '@ant-design/icons';
import { GlobalContext } from "layouts/GlobalContext"
import notebookService from "services/notebooks.js";
import { formatBytes } from "utils";


const { DirectoryTree } = Tree;

export default function SchemaTree(props) {
    const [databases, setDatabases] = useState([]);
    let {schemaData, updateSchemaData} = useContext(GlobalContext)

    const [columns, setColumns] = useState({});
    const [loading, setLoading] = useState(false);

    const getSchemas = async () => {
        const response = await notebookService.getSchemas();
        if(response.success){
            setColumns(response.data.columns)
            setDatabases(response.data.databases)
            updateSchemaData({databases: response.data.databases, columns: response.data.columns})
        }
    }

    useEffect(() => {
        if (!databases.length && !loading){
            if (!schemaData.databases){
                setLoading(true)
                getSchemas()
                setLoading(false)
            }
            else {
                setColumns(schemaData.columns)
                setDatabases(schemaData.databases)
            }
        }
    }, []);

    const getTreeData = () => {
        return databases.map(database=>{
            return {
                title: database.database,
                key: database.database,
                icon: <DatabaseOutlined />,
                children: [
                    {
                        title: "TABLES",
                        key: "TABLES",
                        children: database.tables.filter(table=>table.TBL_TYPE==="EXTERNAL_TABLE").map(table=>{
                            const transient_lastDdlTimeISO = new Date(Number(table.transient_lastDdlTime)*1000).toISOString()
                            return {
                                title: <div style={{display: "inline-block"}}><div style={{float: "left"}}>{table.TBL_NAME + " - "}</div><div style={{fontSize: "12px", float:"right"}}><TimeAgo date={transient_lastDdlTimeISO}/></div></div>,
                                key: table.TBL_ID,
                                icon: <TableOutlined />,
                                children: [
                                    {
                                        title: <>Last Updated: <Moment format="DD-MM-YYYY hh:mm:ss">{transient_lastDdlTimeISO}</Moment> </>,
                                        key: table.TBL_ID + " Last Updated",
                                        icon: null
                                    },
                                    {
                                        title: "Size: " + formatBytes(table.totalSize,2),
                                        key: table.TBL_ID + " Size",
                                    },
                                    {
                                        title: "Columns",
                                        key: table.TBL_ID + " Columns",
                                        children: columns[table.TBL_ID].map(column=>{
                                            return {
                                                title: column.COLUMN_NAME + "  (" + column.TYPE_NAME + ")",
                                                type: column.COLUMN_NAME,
                                                isLeaf: true
                                            }
                                        })
                                    }
                                ] 
                            }
                        })
                    },
                    {
                        title: "VIEWS",
                        key: "VIEWS",
                        children: database.tables.filter(table=>table.TBL_TYPE==="VIRTUAL_VIEW").map(table=>{
                            const transient_lastDdlTimeISO = new Date(Number(table.transient_lastDdlTime)*1000).toISOString()
                            return {
                                title: <div style={{display: "inline-block"}}><div style={{float: "left"}}>{table.TBL_NAME + " - "}</div><div style={{fontSize: "12px", float:"right"}}><TimeAgo date={transient_lastDdlTimeISO}/></div></div>,
                                key: table.TBL_ID,
                                icon: <BorderlessTableOutlined />,
                                children: [
                                    {
                                        title: "Definition: " + table.VIEW_ORIGINAL_TEXT,
                                        key: table.TBL_ID + " Size",
                                    },
                                    {
                                        title: <>Last Updated: <Moment format="DD-MM-YYYY hh:mm:ss">{transient_lastDdlTimeISO}</Moment> </>,
                                        key: table.TBL_ID + " Last Updated",
                                    },
                                    {
                                        title: "Columns",
                                        key: table.TBL_ID + " Columns",
                                        children: columns[table.TBL_ID].map(column=>{
                                            return {
                                                title: column.COLUMN_NAME + "  (" + column.TYPE_NAME + ")",
                                                type: column.COLUMN_NAME,
                                                isLeaf: true
                                            }
                                        })
                                    }
                                ]
                            }
                        })
                    }
                ]
            }
        })
    }

    return (
    <div>
      <Tree
        showLine={{showLeafIcon: true}}
        showIcon={true}
        treeData={getTreeData()}
        multiple
        defaultExpandedKeys={['default']}
        blockNode={true}
      />
    </div>
    );
};
