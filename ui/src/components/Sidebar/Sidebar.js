/*eslint-disable*/
import React, { useState, useEffect } from "react";
import { Select } from "antd";
import { Link } from "react-router-dom";
import style from "./style.module.scss";
import workspaceService from "services/workspace.js";

const { Option } = Select;  

export default function Sidebar(props) {
  const [workspaces, setWorkspaces] = useState(null);
  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState();

  useEffect(() => {
    if (workspaces === null) {
        fetchWorkspaces();
    }
  }, []);

  const fetchWorkspaces = async () => {
    const response = await workspaceService.getWorkspaces();
    setWorkspaces(response.data)
  }

  const setSelectedWorkspace = (workspaceId) => {
    let workspace = workspaces.find(w => w.id === workspaceId); 
    localStorage.setItem('workspaceId', workspace.id);
    localStorage.setItem('workspaceName', workspace.name);
    setSelectedWorkspaceId(workspace.id)
    switchWorkspaceServer(workspace.id)
  }

  const switchWorkspaceServer = async (workspaceId) => {
    const response = await workspaceService.switchWorkspaceServer(workspaceId);
    location.reload();
  }

  let urlPrefix = ""
  if(props.isEmbedPage){
    urlPrefix = "/api/redirect/cuelake"
  }

  let tempWorkspaceId = parseInt(localStorage.getItem("workspaceId"))
  if(tempWorkspaceId && tempWorkspaceId !== selectedWorkspaceId){
    setSelectedWorkspaceId(tempWorkspaceId)
  }
  
  const adminMenuItems = [
    {
      "label": "Dashboard",
      "path": "/dashboard",
      "icon": "fa-file"
    },
    {
      "label": "Schedules",
      "path": "/schedules",
      "icon": "fa-calendar"
    },
    {
      "label": "Settings",
      "path": "/settings",
      "icon": "fa-wrench"
    }
  ]

  const menuItems = [
    {
      "label": "Notebooks",
      "path": "/notebooks",
      "icon": "fa-file"
    },
    {
      "label": "Connections",
      "path": "/connections",
      "icon": "fa-database"
    },
    {
      "label": "Workflows",
      "path": "/workflows",
      "icon": "fa-tasks"
    },
    {
      "label": "Spark-UI",
      "path": "/spark",
      "icon": "fa-star"
    },
    {
      "label": "Interpreter",
      "path": "/interpreterSettings",
      "icon": "fa-wrench"
    }
  ]

  const generateMenuItem = (menuItem) => {
    return <li className="items-center" key={menuItem.path}>
        <Link
          className={
            `${style.navLink} text-xs uppercase py-3 font-bold block ` +
            (window.location.href.indexOf(urlPrefix + menuItem.path) !== -1
              ? "text-blue-500 hover:text-blue-600"
              : "text-gray-800 hover:text-gray-600")
          }
          to={urlPrefix + menuItem.path}
        >
          <i
            className={
              "fas " + menuItem.icon + " mr-2 text-sm " +
              (window.location.href.indexOf(urlPrefix + menuItem.path) !== -1
                ? "opacity-75"
                : "text-gray-400")
            }
          ></i>{" "}
          <span className={props.isEmbedPage ? style.embedLabel : ""}>
            {menuItem.label}
          </span>
        </Link>
      </li>
  }

  let menuElements = []
  menuItems.forEach(menuItem => {
    menuElements.push(
      generateMenuItem(menuItem)
    )
  })

  let adminMenuElements = []
  adminMenuItems.forEach(menuItem => {
    adminMenuElements.push(
      generateMenuItem(menuItem)
    )
  })

  let workspaceElements = []

  workspaces && workspaces.forEach(workspace => {
    workspaceElements.push(
      <Option value={workspace.id} key={workspace.id}>{workspace.name}</Option>
    )
  })

  return (
    <>
      <nav className={`md:left-0 
            md:block md:fixed md:top-0 md:bottom-0 md:overflow-y-auto md:flex-row 
            md:flex-no-wrap md:overflow-hidden shadow-xl bg-white flex flex-wrap items-center 
            justify-between relative z-10 py-4 px-6 
            ${props.isEmbedPage ? style.embedNavBar : "md:w-64"}`
        }>
        <div className="md:flex-col md:items-stretch md:min-h-full md:flex-no-wrap px-0 flex flex-wrap items-center justify-between w-full mx-auto">
          { 
          props.isEmbedPage 
          ?
          null 
          :
          <>
            {/* Brand */}
            <Link
              className="md:block text-left md:pb-1 text-gray-700 mr-0 inline-block whitespace-no-wrap text-sm uppercase font-bold p-0 px-0"
              to={urlPrefix + "/"}
            >
              <img src={require("assets/img/cuelake.png")} />
            </Link>
            </>
          }
          <div
            className={`md:flex md:flex-col md:items-stretch md:opacity-100 md:relative md:mt-2 md:shadow-none shadow absolute top-0 left-0 right-0 z-40 h-auto items-center flex-1 rounded`}
          >
            { props.isEmbedPage ?
              null
            :
              <hr className="my-4 md:min-w-full" />
            }
            {/* Admin Menu */}
            <ul className="md:flex-col md:min-w-full flex flex-col list-none">
              { adminMenuElements }
            </ul>
            {
              workspaces?.length ?
              <div className={style.subMenu}>
              {/* Workspace Selector */}
                <label style={{fontSize: '11px'}}>Workspace</label>
                <Select
                      style={{width: '100%'}}
                      showSearch
                      onChange={(value) => setSelectedWorkspace(value)}
                      filterOption={(input, option) => option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0 }
                      value={selectedWorkspaceId}
                    >
                    {workspaceElements}
                </Select>
                {/* Menu */}
                <ul className="md:flex-col md:min-w-full flex flex-col list-none">
                  { menuElements }
                </ul> 
              </div>
              : 
              <label style={{fontSize: '14px'}}>Create a workspace server first</label>
            }
          </div>
        </div>
      </nav>
    </>
  );
}
