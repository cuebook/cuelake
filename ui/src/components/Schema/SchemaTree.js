import React, { useEffect, useContext } from 'react';
import TimeAgo from 'react-timeago';
import style from "./style.module.scss";
import { Tree } from 'antd';
import Moment from 'react-moment';
import { DatabaseOutlined, TableOutlined, BorderlessTableOutlined } from '@ant-design/icons';
import { GlobalContext } from "layouts/GlobalContext"
import notebookService from "services/notebooks.js";
import { formatBytes } from "utils";

export default function SchemaTree() {
    const { metastoreTables, setMetastoreTables } = useContext(GlobalContext)

    const getMetastoreTables = async () => {
        const response = await notebookService.getMetastoreTables();
        if(response.success){
            setMetastoreTables(getTreeData(response.data))
        }
    }

    useEffect(() => {
        if (!metastoreTables.length){
            getMetastoreTables()
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    function updateTreeData(list, key, children) {
        return list.map((node) => {
          if (node.key === key) {
            return { ...node, children };
          }
          if (node.children) {
            return { ...node, children: updateTreeData(node.children, key, children) };
          }
          return node;
        });
    }

    const onLoadData = async ({ key, children }) => {
        if (children) {
            return;
        }
        else{
            let tableId = parseInt(key.split("-")[0])
            if(tableId){
                let response = await notebookService.getMetastoreColumns(tableId)
                let columnMap = response.data.map(column => {
                    return {
                        title: <><span>{column.name}</span><span className={style.columnType}>({column.type})</span></>,
                        key: column.name + "_" + column.tableId,
                        isLeaf: true
                    }
                });
                setMetastoreTables((origin) =>
                  updateTreeData(origin, key, columnMap)
                )
            }
        }
    }

    const getTreeData = (data) => {
        return Object.keys(data).map(database=>{
            return {
                title: database,
                key: database,
                icon: <DatabaseOutlined />,
                children: [
                    {
                        title: "TABLES",
                        key: database + "_TABLES",
                        children: data[database].tables.map(table=>{
                            const last_updated = new Date(Number(table.last_updated)*1000).toISOString()
                            return {
                                title: <div style={{display: "inline-block"}}><div style={{float: "left"}}>{table.table + " - "}</div><div style={{fontSize: "10px", float:"right"}}><TimeAgo date={last_updated}/></div></div>,
                                key: table.id,
                                icon: <TableOutlined />,
                                children: [
                                    {
                                        title: <>Last Updated: <Moment format="DD-MM-YYYY hh:mm:ss">{last_updated}</Moment> </>,
                                        key: table.id + "-Last Updated",
                                        icon: null,
                                        isLeaf: true
                                    },
                                    {
                                        title: "Size: " + formatBytes(table.size, 2),
                                        key: table.id + "-Size",
                                        isLeaf: true
                                    },
                                    {
                                        title: "Columns",
                                        key: table.id + "-Columns",
                                    }
                                ] 
                            }
                        })
                    },
                    {
                        title: "VIEWS",
                        key: database + "_VIEWS",
                        children: data[database].views.map(table=>{
                            const last_updated = new Date(Number(table.last_updated)*1000).toISOString()
                            return {
                                title: <div style={{display: "inline-block"}}><div style={{float: "left"}}>{table.table + " - "}</div><div style={{fontSize: "10px", float:"right"}}><TimeAgo date={last_updated}/></div></div>,
                                key: table.id,
                                icon: <BorderlessTableOutlined />,
                                children: [
                                    {
                                        title: "Definition: " + table.VIEW_ORIGINAL_TEXT,
                                        key: table.id + "-Size",
                                        isLeaf: true
                                    },
                                    {
                                        title: <>Last Updated: <Moment format="DD-MM-YYYY hh:mm:ss">{last_updated}</Moment> </>,
                                        key: table.id + "-Last Updated",
                                        isLeaf: true
                                    },
                                    {
                                        title: "Columns",
                                        key: table.id + "-Columns",
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
    { metastoreTables.length ?
      <Tree
        defaultExpandedKeys={['default', 'default_TABLES']}
        showLine={{showLeafIcon: false}}
        showIcon={true}
        treeData={metastoreTables}
        loadData={onLoadData}
        multiple
        selectable={false}
      />
      :
      null
    }
    </div>
    );
};
