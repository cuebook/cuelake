import React, { useState, useEffect, useRef } from "react";
import { Button, Form, Input, message, Select } from "antd";
import { LeftOutlined } from '@ant-design/icons';

import style from "./style.module.scss";
import notebookService from "services/notebooks.js";

const { Option } = Select;
export default function EditSchedule(props) {
  const [schedules, setSchedules] = useState([]);
  const [timezones, setTimezones] = useState('');
  const [selectedScheduleId, setSelectedScheduleId] = useState('');
  const [scheduleName, setScheduleName] = useState('');
  const [cronTabSchedule, setCronTabSchedule] = useState('');
  const [selectedTimezone, setSelectedTimezone] = useState('');
  const [selectedSchedule, setSelectedSchedule] = useState({});
  const [isAddScheduleModalVisible, setIsAddScheduleModalVisible] = useState(false);
  const [initialFormValues, setInitialFormValues] = useState({});
  const [form] = Form.useForm();

  useEffect(() => {

    if (!timezones) {
      getTimezones();
    }
    fetchSelectedSchedule()
    
  }, []);

  const getSchedules = async () => {
    const response = await notebookService.getSchedules();
    setSchedules(response);
  };

  const getTimezones = async () => {
    const response = await notebookService.getTimezones();
    setTimezones(response);
  }


  const editScheduleForm = async (values) => {
    let payload = {
        name: scheduleName,
        crontab: cronTabSchedule,
        timezone: selectedTimezone,
    };
    const response = await notebookService.updateSchedule(selectedScheduleId,cronTabSchedule, selectedTimezone, scheduleName)
    if(response.success){
        props.onEditScheduleSuccess()
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
  const fetchSelectedSchedule = async () => {
    const response = await notebookService.getSingleSchedule(props.editSchedule.id)
    setSelectedScheduleId(props.editSchedule.id)
    setSelectedSchedule(response)
    // This parsing logic is temporary 
    let parseSchedule = response[0].schedule.split(")")
    setSelectedTimezone(parseSchedule[1].trim())
    setCronTabSchedule(parseSchedule[0]+")")
    //
    setScheduleName(response[0].name)
    setInitialFormValues({name: response[0].name,...response})
  }

const handleCancelClick = async () =>
{
  props.onEditScheduleSuccess()
}
  
  let ScheduleParamElements = []
    
    let viewScheduleFormElement = (
      <div>
        {
        initialFormValues.name ? 
            <Form 
                layout="vertical" 
                className="mb-2" 
                form={form} 
                initialValues={{...initialFormValues}}
                // onFinish={addConnectionFormSubmit}
                name="EditSchedule"
                scrollToFirstError
                hideRequiredMark
            >
            <div className={style.addConnectionForm}>
                <div className={style.formItem} style={{ width: "100%" }}>
                    
              <Form.Item label="Crontab Schedule (m/h/dM/MY/d)">
              <Input placeholder="* * * * *" onChange={(event) => setCronTabSchedule(event.target.value)}/>
            </Form.Item>
            <Form.Item label="Timezone">
              <Select onChange={(value) => setSelectedTimezone(value)}>
                {timezoneElements}
              </Select>
            </Form.Item>
                <Form.Item hasFeedback name="name" label="Schedule Name">
                    <Input  className={style.inputArea} onChange={(event) => setScheduleName(event.target.value)}/>
                </Form.Item>
                </div>
                {ScheduleParamElements}
            </div>
            <div className={style.submitButton}>
            <Button
                icon=""
                type="primary"
                className="mr-2"
                htmlType="submit"
                onClick={editScheduleForm}
            >
                Save
            </Button>
            <Button
                icon=""
                type="primary"
                className="mr-2"
                htmlType="submit"
                onClick={handleCancelClick}
            >
                Cancel
            </Button>
          </div>
            </Form>
            :
            null
        }
      </div>
    );

    return (
      <div>
        <div className="row view-connection">
            <div>
              {viewScheduleFormElement}
            </div>
        </div>
      </div>
    );
  }
