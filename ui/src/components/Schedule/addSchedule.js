import React, { useState, useEffect } from "react";
import {
    Modal,
    Input,
    Select,
    Form,
    message,
  } from "antd";
import notebookService from "services/notebooks";

const { Option } = Select;

export default function AddSchedule(props) {
    const [timezones, setTimezones] = useState('');
    const [cronTabSchedule, setCronTabSchedule] = useState('* * * * *');
    const [selectedTimezone, setSelectedTimezone] = useState('');
    const [scheduleName, setScheduleName] = useState('');

    useEffect(() => {
      if (!timezones) {
        getTimezones();
      }
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const saveSchedule = async (event) => {
      if(cronTabSchedule && selectedTimezone && scheduleName){
        const response = await notebookService.addSchedule(cronTabSchedule, selectedTimezone, scheduleName);
        if(response.success){
          setCronTabSchedule("* * * * *")
          setSelectedTimezone("")
          props.onCompletion()
        }
        else{
          message.error(response.message);
        }
      }
      else{
        message.error('Please fill values');
      }
    }

    const getTimezones = async () => {
      const response = await notebookService.getTimezones();
      setTimezones(response);
    }

    const timezoneElements = timezones && timezones.map(timezone =>
        <Option value={timezone} key={timezone}>{timezone}</Option>
      )

    const handleCancel = () => {
        props.onCompletion()
    }

    return (
        <Modal 
          title="Add Schedule" 
          onOk={saveSchedule}
          visible={true}
          onCancel={handleCancel}
          okText="Save"
        >
            <Form layout={"vertical"}>
              <Form.Item label="Crontab Schedule (m/h/dM/MY/d)">
                <Input placeholder="* * * * *" defaultValue = "* * * * *" onChange={(event) => setCronTabSchedule(event.target.value)}/>
              </Form.Item>
              <Form.Item label="Timezone">
                <Select 
                    showSearch
                    onChange={(value) => setSelectedTimezone(value)}
                    filterOption={(input, option) => option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0 }
                >
                  {timezoneElements}
                </Select>
              </Form.Item>
              <Form.Item label="Schedule Name">
                <Input placeholder="Schedule name"  onChange={(event) => setScheduleName(event.target.value)}/>
              </Form.Item>
            </Form>
        </Modal>
    )
}