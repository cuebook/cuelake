import React from 'react';

import SchedulesView from 'components/Schedules/SchedulesView.js';

import Schedule from "components/Schedules/Schedule.js"


export default function Schedules() {
    return (
      <>
        <div className="flex flex-wrap mh-full">
          <div className="w-full mb-12 px-4">
            <Schedule/>
          </div>
        </div>
      </>
    );
  }
  