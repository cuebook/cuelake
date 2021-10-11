import React, { useState, useEffect } from "react";
import style from "./style.module.scss";
import workspaceService from "services/workspace.js";
import {
  Button,
  Popconfirm,
} from "antd";
import {DeleteOutlined, StopOutlined, CheckOutlined} from '@ant-design/icons';

export default function Dashboard() {
  const [workspaces, setWorkspaces] = useState([]);

  useEffect(() => {
    if (!workspaces.length) {
        fetchWorkspaces();
    }
  }, []);

  const fetchWorkspaces = async () => {
    const response = await workspaceService.getWorkspaces();
    setWorkspaces(response.data)
  }

  function routeWorkspace(id){
    console.log("test")
  }
  
  const StopWorkspace = async (id) => {
    const response = await workspaceService.stopWorkspaceServer(id)
    if(response.success){
      fetchWorkspaces();
    }
  }

  const StartWorkspace = async (id) => {
    const response = await workspaceService.startWorkspaceServer(id)
    if(response.success){
      fetchWorkspaces();
    }
  }


  const deleteWorkspace = async (id) => {
    const response = await workspaceService.deleteWorkspaceServer(id)
    if(response.success){
      fetchWorkspaces();
    }
  }

  const cardWidget = (workspace) => {
   return <div className={style.cardWrapper}>
    <article className={style.card}>
      <div className={style.cardBody}>
        <div className={style.titleContent}>
          <h2 className={style.bodyTitle}>{workspace.name}</h2>
          {
            workspace.replica !== 0
            ?  <span className="fas fa-circle ml-2 icon-driver-1 red" style={{color:"green",fontSize:"12px",position:"absolute", left:"0px", top:"30px"}}></span>
            :  <span className="fas fa-circle ml-2 icon-driver-2" style={{color:"red",fontSize:"12px",position:"absolute", left:"0px", top:"30px"}}></span>
          }
          <div className={style.storageLogo} style={{backgroundImage: `url(${require("assets/img/" + workspace.workspaceConfig.storage + ".svg")})`}}></div>
        </div>
        <p className={style.bodySubTitle}>{workspace.description}</p>
        
        <div className={style.storage}>
          <p className={style.storageText}>Warehouse Location :</p> 
          <span >{workspace.workspaceConfig.warehouseLocation} </span>
        </div>
        <div className={style.buttons}>
          
            {
              
                workspace.replica !== 0
                ? 
                <Button
                className={style.cardButton} 
                icon={<StopOutlined />}
                type="primary"
                htmlType="submit"
                onClick={() => StopWorkspace(workspace.id)}
               >
                Stop Workspace
                </Button>
                :  <Button
                className={style.cardButton} 
                icon={<CheckOutlined />}
                type="primary"
                htmlType="submit"
                onClick={() => StartWorkspace(workspace.id)}
               >
                Start Workspace
                </Button>
            }
          <Button
                className={style.cardButton} 
                icon={<DeleteOutlined />}
                type="primary"
                htmlType="submit"
               >
                <Popconfirm
            title={"Are you sure to delete "+ workspace.name +"?"}
            onConfirm={() => deleteWorkspace(workspace.id)}
            okText="Yes"
            cancelText="No">
            
              Delete Workspace
          </Popconfirm>
            </Button>
          
        </div>
      </div>
    </article>
      <div className={style.bodyFooter}>
        <div className={style.section1}>
          <p className={style.footerText}>Spark Image Version</p>
          <span className={style.values}>{workspace.workspaceConfig.sparkImage}</span>
        </div>
        <div className={style.section2}>
          <p className={style.footerText}> Zeppelin Interpreter Image</p>
          <span>{workspace.workspaceConfig.sparkImage}</span>
        </div>
      </div>
    </div>
  }

  return (
    <div>
        <div className={`d-flex flex-column justify-content-center text-right mb-2`}>
            <Button
                key="createTag"
                type="primary"
                onClick={(e) => {e.preventDefault();
                    window.location.href='/workspace/add';}
                }
            >
                New Workspace
            </Button>
        </div>
                
        <div className={style.cardList} id="app-card-list">
        {
          workspaces.map((workspace, index) => {
            return <div key={workspace.id}>
              {cardWidget(workspace)}
            </div>
          })
        }
    </div>
  </div>
  );
}