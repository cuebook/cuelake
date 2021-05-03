import React from 'react';

import SchedulesView from 'components/Schedules/SchedulesView.js';

import Schedule from "components/Schedules/Schedule.js"


export default function Schedules() {
    return (
      <>
        <div className="flex flex-wrap">
          <div className="w-full lg:w-12/12 px-4 mt-4">
            <Schedule/>
          </div>
        </div>
      </>
    );
  }
  