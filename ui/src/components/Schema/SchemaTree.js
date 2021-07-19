import React, { useState, useEffect, useContext } from 'react';
import TimeAgo from 'react-timeago';
import style from "./style.module.scss";
import { Tree } from 'antd';
import Moment from 'react-moment';
import { DatabaseOutlined, TableOutlined, BorderlessTableOutlined } from '@ant-design/icons';
import { GlobalContext } from "layouts/GlobalContext"
import notebookService from "services/notebooks.js";
import { formatBytes } from "utils";


const { DirectoryTree } = Tree;

export default function SchemaTree() {
    const { metastoreTables, setMetastoreTables } = useContext(GlobalContext)
    const [columns, setColumns] = useState({});
    const [loading, setLoading] = useState(false);

    const getMetastoreTables = async () => {
        const response = await notebookService.getMetastoreTables();
        if(response.success){
            console.log(response.data)
            setMetastoreTables(response.data)
        }
        console.log(metastoreTables)
    }

    useEffect(() => {
        if (!metastoreTables.length){
            setLoading(true)
            getMetastoreTables()
            setLoading(false)
        }
    }, []);

    const getTreeData = () => {
        return Object.keys(metastoreTables).map(database=>{
            return {
                title: database,
                key: database,
                icon: <DatabaseOutlined />,
                children: [
                    {
                        title: "TABLES",
                        key: "TABLES",
                        children: metastoreTables[database].tables.map(table=>{
                            const last_updated = new Date(Number(table.last_updated)*1000).toISOString()
                            return {
                                title: <div style={{display: "inline-block"}}><div style={{float: "left"}}>{table.TBL_NAME + " - "}</div><div style={{fontSize: "10px", float:"right"}}><TimeAgo date={last_updated}/></div></div>,
                                key: table.TBL_ID,
                                icon: <TableOutlined />,
                                children: [
                                    {
                                        title: <>Last Updated: <Moment format="DD-MM-YYYY hh:mm:ss">{last_updated}</Moment> </>,
                                        key: table.TBL_ID + " Last Updated",
                                        icon: null
                                    },
                                    {
                                        title: "Size: " + formatBytes(table.totalSize,2),
                                        key: table.TBL_ID + " Size",
                                    },
                                    // {
                                    //     title: "Columns",
                                    //     key: table.TBL_ID + " Columns",
                                    //     children: columns[table.TBL_ID].map((column, index)=>{
                                    //         return {
                                    //             key: column.CD_ID + "_" + index,
                                    //             title: column.COLUMN_NAME + "  (" + column.TYPE_NAME + ")",
                                    //             type: column.COLUMN_NAME,
                                    //             isLeaf: true
                                    //         }
                                    //     })
                                    // }
                                ] 
                            }
                        })
                    },
                    {
                        title: "VIEWS",
                        key: "VIEWS",
                        children: metastoreTables[database].views.map(table=>{
                            const last_updated = new Date(Number(table.last_updated)*1000).toISOString()
                            return {
                                title: <div style={{display: "inline-block"}}><div style={{float: "left"}}>{table.TBL_NAME + " - "}</div><div style={{fontSize: "10px", float:"right"}}><TimeAgo date={last_updated}/></div></div>,
                                key: table.TBL_ID,
                                icon: <BorderlessTableOutlined />,
                                children: [
                                    {
                                        title: "Definition: " + table.VIEW_ORIGINAL_TEXT,
                                        key: table.TBL_ID + " Size",
                                    },
                                    {
                                        title: <>Last Updated: <Moment format="DD-MM-YYYY hh:mm:ss">{last_updated}</Moment> </>,
                                        key: table.TBL_ID + " Last Updated",
                                    },
                                    // {
                                    //     title: "Columns",
                                    //     key: table.TBL_ID + " Columns",
                                    //     children: columns[table.TBL_ID].map((column, index)=>{
                                    //         return {
                                    //             key: column.CD_ID + "_" + index,
                                    //             title: column.COLUMN_NAME + "  (" + column.TYPE_NAME + ")",
                                    //             type: column.COLUMN_NAME,
                                    //             isLeaf: true
                                    //         }
                                    //     })
                                    // }
                                ]
                            }
                        })
                    }
                ]
            }
            
        })
    }
    console.log(metastoreTables)
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
