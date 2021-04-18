import React from "react";
import style from "./style.module.scss";
import { Tabs } from 'antd';
import  ZeppelinInterpreterSettings from "./ZeppelinInterpreterSettings.js"
import  AlertSettings from "./AlertSettings.js"

const { TabPane } = Tabs;

export default function Settings(){
  return <div className={style.settingsWrapper}>
        <Tabs defaultActiveKey="1" >
        <TabPane tab="Alerts" key="1">
            <AlertSettings />
        </TabPane>
        <TabPane tab="Interpreter Settings" key="2">
            <ZeppelinInterpreterSettings />
        </TabPane>
    </Tabs>
  </div>
};
