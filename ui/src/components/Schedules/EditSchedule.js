import React, { useState, useEffect } from "react";
import { Button, Form, Input, message, Select } from "antd";

import style from "./style.module.scss";
import notebookService from "services/notebooks.js";

const { Option } = Select;
export default function EditSchedule(props) {
  const [timezones, setTimezones] = useState('');
  const [selectedScheduleId, setSelectedScheduleId] = useState('');
  const [scheduleName, setScheduleName] = useState('');
  const [cronTabSchedule, setCronTabSchedule] = useState('');
  const [selectedTimezone, setSelectedTimezone] = useState('');
  const [initialFormValues, setInitialFormValues] = useState({});
  const [form] = Form.useForm();

  useEffect(() => {

    if (!timezones) {
      getTimezones();
    }
    fetchSelectedSchedule()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const getTimezones = async () => {
    const response = await notebookService.getTimezones();
    setTimezones(response);
  }


  const editScheduleForm = async (values) => {
    const response = await notebookService.updateSchedule(selectedScheduleId, cronTabSchedule, selectedTimezone, scheduleName)
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
    let responseObj = response[0];
    let resName = responseObj["name"]
    let resTimezone = responseObj["timezone"]
    let resCrontab = responseObj["crontab"]

    setSelectedTimezone(resTimezone)
    setCronTabSchedule(resCrontab)
    setScheduleName(response[0].name)
    setInitialFormValues({name: resName,crontab: resCrontab,timezone: resTimezone,...response})

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
                name="EditSchedule"
                scrollToFirstError
                hideRequiredMark
            >
            <div className={style.addConnectionForm}>
                <div className={style.formItem} style={{ width: "100%" }}>
                    
              <Form.Item label="Crontab Schedule (m/h/dM/MY/d)" name="crontab">
              <Input placeholder="* * * * *" onChange={(event) => setCronTabSchedule(event.target.value)}/>
            </Form.Item>
            <Form.Item label="Timezone" name="timezone">
              <Select showSearch onChange={(value) => setSelectedTimezone(value)}>
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
