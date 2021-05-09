/*eslint-disable*/
import React from "react";
import { Link } from "react-router-dom";

export default function Sidebar(props) {
  const [collapseShow, setCollapseShow] = React.useState("hidden");
  let urlPrefix = ""
  if(props.isEmbedPage){
    urlPrefix = "/api/redirect/cuelake"
  }
  return (
    <>
      <nav className={`md:left-0 md:block md:fixed md:top-0 md:bottom-0 md:overflow-y-auto md:flex-row md:flex-no-wrap md:overflow-hidden shadow-xl bg-white flex flex-wrap items-center justify-between relative z-10 py-4 px-6 ${props.isEmbedPage ? "md:w-48" : "md:w-64"}`}>
        <div className="md:flex-col md:items-stretch md:min-h-full md:flex-no-wrap px-0 flex flex-wrap items-center justify-between w-full mx-auto">
          { 
          props.isEmbedPage 
          ?
          null 
          :
          <>
            {/* Toggler */}
            <button
              className="cursor-pointer text-black opacity-50 md:hidden px-3 py-1 text-xl leading-none bg-transparent rounded border border-solid border-transparent"
              type="button"
              onClick={() => setCollapseShow("bg-white m-2 py-3 px-6")}
            >
              <i className="fas fa-bars"></i>
            </button>
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
            className={
              "md:flex md:flex-col md:items-stretch md:opacity-100 md:relative md:mt-2 md:shadow-none shadow absolute top-0 left-0 right-0 z-40 overflow-y-auto overflow-x-hidden h-auto items-center flex-1 rounded " +
              collapseShow
            }
          >
            { props.isEmbedPage ?
              null
            :
              <hr className="my-4 md:min-w-full" />
            }
            {/* Heading */}

            <ul className="md:flex-col md:min-w-full flex flex-col list-none">
              <li className="items-center">
                <Link
                  className={
                    "text-xs uppercase py-3 font-bold block " +
                    (window.location.href.indexOf(urlPrefix + "/notebook") !== -1
                      ? "text-blue-500 hover:text-blue-600"
                      : "text-gray-800 hover:text-gray-600")
                  }
                  to={urlPrefix + "/notebook"}
                >
                  <i
                    className={
                      "fas fa-tv mr-2 text-sm " +
                      (window.location.href.indexOf(urlPrefix + "/notebook") !== -1
                        ? "opacity-75"
                        : "text-gray-400")
                    }
                  ></i>{" "}
                  Notebooks
                </Link>
              </li>
              <li className="items-center">
                <Link
                  className={
                    "text-xs uppercase py-3 font-bold block " +
                    (window.location.href.indexOf(urlPrefix + "/connections") !== -1
                      ? "text-blue-500 hover:text-blue-600"
                      : "text-gray-800 hover:text-gray-600")
                  }
                  to={urlPrefix + "/connections"}
                >
                  <i
                    className={
                      "fas fa-database mr-2 text-sm " +
                      (window.location.href.indexOf(urlPrefix + "/connections") !== -1
                        ? "opacity-75"
                        : "text-gray-400")
                    }
                  ></i>{" "}
                  Connections
                </Link>
              </li>
              <li className="items-center">
                <Link
                  className={
                    "text-xs uppercase py-3 font-bold block " +
                    (window.location.href.indexOf(urlPrefix + "/workflows") !== -1
                      ? "text-blue-500 hover:text-blue-600"
                      : "text-gray-800 hover:text-gray-600")
                  }
                  to={urlPrefix + "/workflows"}
                >
                  <i
                    className={
                      "fas fa-tasks mr-2 text-sm " +
                      (window.location.href.indexOf(urlPrefix + "/workflows") !== -1
                        ? "opacity-75"
                        : "text-gray-400")
                    }
                  ></i>{" "}
                  Workflows
                </Link>
              </li>
              <li className="items-center">
                <Link
                  className={
                    "text-xs uppercase py-3 font-bold block " +
                    (window.location.href.indexOf(urlPrefix + "/files") !== -1
                      ? "text-blue-500 hover:text-blue-600"
                      : "text-gray-800 hover:text-gray-600")
                  }
                  to={urlPrefix + "/files"}
                >
                  <i
                    className={
                      "fas fa-folder mr-2 text-sm " +
                      (window.location.href.indexOf(urlPrefix + "/files") !== -1
                        ? "opacity-75 fa-folder-open"
                        : "text-gray-400")
                    }
                  ></i>{" "}
                  Files
                </Link>
              </li>
              <li className="items-center">
                <Link
                  className={
                    "text-xs uppercase py-3 font-bold block " +
                    (window.location.href.indexOf(urlPrefix + "/schedules") !== -1
                      ? "text-blue-500 hover:text-blue-600"
                      : "text-gray-800 hover:text-gray-600")
                  }
                  to={urlPrefix + "/schedules"}
                >
                  <i
                    className={
                      "fas fa-calendar mr-2 text-sm " +
                      (window.location.href.indexOf(urlPrefix + "/schedules") !== -1
                        ? "opacity-75"
                        : "text-gray-400")
                    }
                  ></i>{" "}
                  Schedules
                </Link>
              </li>
              <li className="items-center">
                <Link
                  className={
                    "text-xs uppercase py-3 font-bold block " +
                    (window.location.href.indexOf(urlPrefix + "/settings") !== -1
                      ? "text-blue-500 hover:text-blue-600"
                      : "text-gray-800 hover:text-gray-600")
                  }
                  to={urlPrefix + "/settings"}
                >
                  <i
                    className={
                      "fas fa-wrench mr-2 text-sm " +
                      (window.location.href.indexOf(urlPrefix + "/settings") !== -1
                        ? "opacity-75"
                        : "text-gray-400")
                    }
                  ></i>{" "}
                  Settings
                </Link>
              </li>
            </ul>
          </div>
        </div>
      </nav>
    </>
  );
}
