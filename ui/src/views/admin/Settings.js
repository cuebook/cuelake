import React from "react";

// components
import SettingsView from "components/Settings/Settings.js";

export default function Settings() {
  return (
    <>
      <div className="flex flex-wrap">
        <div className="w-full lg:w-12/12 px-4 mt-4">
          <SettingsView />
        </div>
      </div>
    </>
  );
}
