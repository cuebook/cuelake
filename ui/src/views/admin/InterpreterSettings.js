import React from "react";

// components
import SettingsView from "components/Settings/ZeppelinInterpreterSettings.js";

export default function ZeppelinInterpreterSettings() {
  return (
    <>
      <div className="flex flex-wrap">
        <div className="w-full lg:w-12/12 px-4">
          <SettingsView />
        </div>
      </div>
    </>
  );
}
