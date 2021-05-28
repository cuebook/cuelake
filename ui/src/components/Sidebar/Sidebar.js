/*eslint-disable*/
import React from "react";
import { Link } from "react-router-dom";
import style from "./style.module.scss";

export default function Sidebar(props) {
  let urlPrefix = ""
  if(props.isEmbedPage){
    urlPrefix = "/api/redirect/cuelake"
  }
  
  const menuItems = [
    {
      "label": "Notebooks",
      "path": "/notebook",
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
      "label": "Files",
      "path": "/files",
      "icon": "fa-folder"
    },
    {
      "label": "Schedules",
      "path": "/schedules",
      "icon": "fa-calendar"
    },
    {
      "label": "Spark UI",
      "path": "/spark",
      "icon": "fa-star"
    },
    {
      "label": "Settings",
      "path": "/settings",
      "icon": "fa-wrench"
    }
  ]

  let menuElements = []

  menuItems.forEach(menuItem => {
    menuElements.push(
      <li className="items-center" key={menuItem.path}>
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
            className={`md:flex md:flex-col md:items-stretch md:opacity-100 md:relative md:mt-2 md:shadow-none shadow absolute top-0 left-0 right-0 z-40 overflow-y-auto overflow-x-hidden h-auto items-center flex-1 rounded`}
          >
            { props.isEmbedPage ?
              null
            :
              <hr className="my-4 md:min-w-full" />
            }
            {/* Heading */}

            <ul className="md:flex-col md:min-w-full flex flex-col list-none">
              { menuElements }
            </ul>
          </div>
        </div>
      </nav>
    </>
  );
}
