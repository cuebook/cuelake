import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import notebookService from "services/notebooks.js";
import ReactTooltip from "react-tooltip";

// components

import TableDropdown from "components/Dropdowns/TableDropdown.js";

export default function CardTable({ color }) {
  // let response = await (new NotebookService()).getNotebooks();
  const [notebooks, setNotebooks] = useState('');
  const [schedules, setSchedules] = useState('');
  const [selectedNotebook, setSelectedNotebook] = useState('');
  const [selectedSchedule, setSelectedSchedule] = useState('');

  useEffect(() => {
    if (!notebooks) {
        getNotebooks();
    }
    if (!schedules) {
      getSchedules();
    }
  }, []);

  const getNotebooks = async () => {
    const response = await notebookService.getNotebooks();
    setNotebooks(response);
  };

  const getSchedules = async () => {
    const response = await notebookService.getSchedules();
    setSchedules(response);
  };

  const openScheduleNoteBookForm = (notebook) => {
    setSelectedNotebook(notebook.id)
  }

  const selectSchedule = (event) => {
    setSelectedSchedule(event.target.value)
  }

  const addNotebookSchedule = async () => {
    if(selectedSchedule && selectedNotebook && selectedSchedule !== -1){
      await notebookService.addNotebookSchedule(selectedNotebook, selectedSchedule);
      setSelectedSchedule(-1)
      setSelectedNotebook(null)
      getNotebooks()
    }
    else{
      alert('Schedule not selected')
    }
  }

  const getLastRunStatusElement = (notebook) => {
      const lastRunStatusChildElements = []
      if(notebook && notebook.paragraphs){
        const paragraphPercent = 100/(notebook.paragraphs.length)
        notebook.paragraphs.forEach(paragraph => {
          let paragraphClassName = ""
          if(paragraph.status === "FINISHED" || paragraph.status === "READY") paragraphClassName = "bg-green-500";
          else if(paragraph.status === "ERROR") paragraphClassName = "bg-red-500";
          else if(paragraph.status === "RUNNING") paragraphClassName = "bg-green-400";
          else if(paragraph.status === "ABORT") paragraphClassName = "bg-yellow-500";
          lastRunStatusChildElements.push(
            <div key={paragraph.id} 
              style={{width: paragraphPercent + "%"}} 
              data-tip data-for={paragraph.id} 
              className={`shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center notebook-paragraph-progressbar-box ${paragraphClassName}`}>
              <ReactTooltip id={paragraph.id}>
                {paragraph.started ? <p>Start Time: {paragraph.started}</p> : null}
                {paragraph.finished ? <p>End Time: {paragraph.finished}</p> : null}
                {paragraph.status ? <p>Status: {paragraph.status}</p> : null}
                {paragraph.progress ? <p>Progress: {paragraph.progress}</p> : null}
              </ReactTooltip>
            </div>
          )
        })
      }
      let lastRunStatusElement = <div className="overflow-hidden h-2 mt-2 mb-2 text-xs flex rounded-sm bg-blue-200 w-full">
                                    {lastRunStatusChildElements}
                                  </div>
      return lastRunStatusElement
    }

  let scheduleSelectorElement = null
  if(schedules){
    let scheduleOptionsElement = [<option value={-1} key={0} disabled>Cron Schedule</option>]
    schedules.forEach(schedule => {
      scheduleOptionsElement.push(<option value={schedule.id} key={schedule.id}>{schedule.schedule}</option>)
    })
    scheduleSelectorElement = <div>
      <select 
        className="px-2 py-2 placeholder-gray-400 text-gray-700 bg-white rounded text-sm shadow focus:outline-none focus:shadow-outline ease-linear transition-all duration-150"
        onChange={(event => selectSchedule(event))} defaultValue={-1}>{scheduleOptionsElement}</select>
      <button
        onClick={addNotebookSchedule}
        className="bg-blue-500 text-white active:bg-blue-600 font-bold uppercase text-sm px-4 py-2 rounded shadow hover:shadow-md outline-none focus:outline-none ml-2 ease-linear transition-all duration-150"
      >
        Save
      </button>
    </div>
  }

  let notebookRows = []
  if(notebooks){
    notebooks.forEach(notebook => {
      let lastRunStatusElement = getLastRunStatusElement(notebook);
      let notebookRowElement = <tr key={notebook.name}>
                <th className="border-t-0 px-6 align-middle border-l-0 border-r-0 text-xs whitespace-no-wrap p-4 text-left flex items-center">
                  <span
                    className={
                      "font-bold " +
                      +(color === "light" ? "text-gray-700" : "text-white")
                    }
                  >
                    {notebook.name.substring(1)}
                  </span>
                </th>
                <td className="border-t-0 px-6 align-middle border-l-0 border-r-0 text-xs whitespace-no-wrap p-4">
                  {notebook.isScheduled ? "Scheduled for " + notebook.schedule 
                  : 
                  <>
                    { selectedNotebook === notebook.id 
                      ?
                      scheduleSelectorElement
                      :
                      <span onClick={(event) => openScheduleNoteBookForm(notebook)}>Add Schedule</span>
                    }
                  </>
                  }
                </td>
                <td className="border-t-0 px-6 align-middle border-l-0 border-r-0 text-xs whitespace-no-wrap p-4">
                  <div className="notebook-status-wrapper">
                    {lastRunStatusElement}
                  </div>
                </td>
                <td className="border-t-0 px-6 align-middle border-l-0 border-r-0 text-xs whitespace-no-wrap p-4 text-right">
                  <TableDropdown />
                </td>
              </tr>
      notebookRows.push(notebookRowElement)
    })
  }

  return (

    <>
      <div
        className={
          "relative flex flex-col min-w-0 break-words w-full mb-6 shadow-lg rounded " +
          (color === "light" ? "bg-white" : "bg-blue-900 text-white")
        }
      >
        <div className="block w-full overflow-x-auto">
          {/* Projects table */}
          <table className="items-center w-full bg-transparent border-collapse">
            <thead>
              <tr>
                <th
                  className={
                    "px-6 align-middle border border-solid py-3 text-xs uppercase border-l-0 border-r-0 whitespace-no-wrap font-semibold text-left " +
                    (color === "light"
                      ? "bg-gray-100 text-gray-600 border-gray-200"
                      : "bg-blue-800 text-blue-300 border-blue-700")
                  }
                >
                  Notebook
                </th>
                <th
                  className={
                    "px-6 align-middle border border-solid py-3 text-xs uppercase border-l-0 border-r-0 whitespace-no-wrap font-semibold text-left " +
                    (color === "light"
                      ? "bg-gray-100 text-gray-600 border-gray-200"
                      : "bg-blue-800 text-blue-300 border-blue-700")
                  }
                >
                  Schedule
                </th>
                <th
                  className={
                    "px-6 align-middle border border-solid py-3 text-xs uppercase border-l-0 border-r-0 whitespace-no-wrap font-semibold text-left " +
                    (color === "light"
                      ? "bg-gray-100 text-gray-600 border-gray-200"
                      : "bg-blue-800 text-blue-300 border-blue-700")
                  }
                >
                  Last Run Status
                </th>
                <th className={
                    "px-6 align-middle border border-solid py-3 text-xs uppercase border-l-0 border-r-0 whitespace-no-wrap font-semibold text-left " +
                    (color === "light"
                      ? "bg-gray-100 text-gray-600 border-gray-200"
                      : "bg-blue-800 text-blue-300 border-blue-700")
                }>
                </th>
              </tr>
            </thead>
            <tbody>
              {notebookRows}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}

CardTable.defaultProps = {
  color: "light",
};

CardTable.propTypes = {
  color: PropTypes.oneOf(["light", "dark"]),
};
