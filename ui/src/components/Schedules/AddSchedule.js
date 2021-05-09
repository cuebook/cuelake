import React, { useState, useEffect, useRef } from "react";
import { Button, Form, Input, Switch, message, Select } from "antd";
import { LeftOutlined } from '@ant-design/icons';

import style from "./style.module.scss";
import notebookService from "services/notebooks.js";
import { setTokenSourceMapRange } from "typescript";

const { Option } = Select;
export default function AddSchedule(props) {
  const [form] = Form.useForm();

  const [schedules, setSchedules] = useState([]);
  const [timezones, setTimezones] = useState('');
  const [scheduleName, setScheduleName] = useState('');
  const [cronTabSchedule, setCronTabSchedule] = useState('');
  const [selectedTimezone, setSelectedTimezone] = useState('');
  const [isAddScheduleModalVisible, setIsAddScheduleModalVisible] = useState(false);


  useEffect(() => {
    
    if (!timezones) {
      getTimezones();
    }
  }, []);


  const getSchedules = async () => {
    const response = await notebookService.getSchedules();
    setSchedules(response);
  };

  const getTimezones = async () => {
    const response = await notebookService.getTimezones();
    setTimezones(response);
  }


  const saveSchedule = async (event) => {
    if(cronTabSchedule, selectedTimezone, scheduleName){
      const response = await notebookService.addSchedule(cronTabSchedule, selectedTimezone, scheduleName);
      if(response.success){
        setCronTabSchedule("")
        setSelectedTimezone("")
        setScheduleName("")
        setIsAddScheduleModalVisible(false)
        getSchedules()
      }
      else{
        message.error(response.message);
      }
    }
    else{
      message.error('Please fill values');
    }
  }
  const addConnectionFormSubmit = async (values) => {
    let payload = {
        name: scheduleName,
        crontab: cronTabSchedule,
        timezone: selectedTimezone,
    };
    const response = await notebookService.addSchedule(cronTabSchedule, selectedTimezone, scheduleName)
    if(response.success){
        props.onAddScheduleSuccess()
    }
    else{
        message.error(response.message);
    }
  };

  
  let timezoneElements = []
  if(timezones){
    timezones.forEach(tz => {
      timezoneElements.push(<Option value={tz} key={tz}>{tz}</Option>)
    })
  }
  let scheduleParamElements = []

    let addScheduleFormElement = (
      <div>
        <Form 
            layout="vertical" 
            className="mb-2" 
            form={form} 
            onFinish={addConnectionFormSubmit}
            name="addSchedule"
            scrollToFirstError
            hideRequiredMark
        >
          <div className={style.addConnectionForm}>
            <div className={style.formItem} style={{ width: "100%" }}>
              <Form.Item label="Crontab Schedule (m/h/dM/MY/d)">
              <Input placeholder="* * * * *" defaultValue = "* * * * *" onChange={(event) => setCronTabSchedule(event.target.value)}/>
            </Form.Item>
            <Form.Item label="Timezone">
              <Select showSearch onChange={(value) => setSelectedTimezone(value)}>
                {timezoneElements}
              </Select>
            </Form.Item>
            <Form.Item hasFeedback name="name" label="Schedule Name">
                <Input className={style.inputArea} onChange={(event) => setScheduleName(event.target.value)}/>
              </Form.Item>
            </div>
            {scheduleParamElements}
          </div>
          <div className={style.submitButton}>
            <Button
                icon=""
                type="primary"
                className="mr-2"
                htmlType="submit"
            >
                Add Schedule
            </Button>
          </div>
        </Form>
      </div>
    );


    return (
      <div>
        <div className="row">
            <div>
              {addScheduleFormElement}
            </div>
          
        </div>
      </div>
    );
  }
