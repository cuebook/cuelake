import React, { useState, useEffect } from "react";
import style from "./style.module.scss";
import { Form, Input, Switch, Button, message } from 'antd';
import settingsService from "services/settings.js";

export default function AlertSettings(){

  const [accountSettings, setAccountSettings] = useState([]);
  const [initialFormValues, setInitialFormValues] = useState({});
  const [form] = Form.useForm();

  useEffect(() => {
    if (!accountSettings.length) {
        fetchAccountSettings();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchAccountSettings = async () => {
    const response = await settingsService.getAccountSettings()
    setAccountSettings(response.data)
    parseInitialFormValues(response.data)
  }

  const updateAccountSettings = async (requestPayload) => {
    const response = await settingsService.updateAccountSettings(requestPayload)
    if(response.success){
        message.success("Settings updated successfully")
        fetchAccountSettings()
    }
    else{
        message.error(response.message)
    }
  }

  const updateAccountSettingsFormSubmit = (values) => {
    let requestPayload = []
    accountSettings.forEach(as => {
        as.value = values[as["key"]].toString()
        requestPayload.push(as)
    })
    updateAccountSettings(requestPayload)
  }

  const parseInitialFormValues = (settings) => {
    let initialFormValues = {}
    settings.forEach(s => {
        let value = s.type !== "bool" ? s.value : s.value === "true"
        initialFormValues[s.key] = value
    })
    setInitialFormValues(initialFormValues)
  }

  const getInputElementFromType = (setting) => {
    if(setting.type==="text")
        return <Form.Item name={setting.key} label={setting.label} key={setting.key}>
            <Input />
        </Form.Item>
    else if(setting.type === "bool")
        return <Form.Item name={setting.key} label={setting.label} key={setting.key} valuePropName="checked">
            <Switch />
        </Form.Item>
    else
        return null
  }

  let formElements = []
  if(accountSettings.length){
      accountSettings.forEach(as => {
          let inputElement = getInputElementFromType(as)
          formElements.push(
            inputElement
          )
      })
  }

  const layout = {
    labelCol: { span: 4 },
    wrapperCol: { span: 12 },
  };
  const tailLayout = {
    wrapperCol: { offset: 4, span: 12 },
  };

  return <div className={style.settingsDiv}>
        {Object.keys(initialFormValues).length !== 0
        ?
        <Form 
            {...layout} 
            className="mb-2"
            form={form} 
            initialValues={{...initialFormValues}}
            name="accountSettings"
            scrollToFirstError
            hideRequiredMark
            onFinish={updateAccountSettingsFormSubmit}
        >
        {formElements}
            <Form.Item {...tailLayout}>
                <Button
                    icon=""
                    type="primary"
                    className="mr-2"
                    htmlType="submit"
                >
                Save
                </Button>
            </Form.Item>
        </Form>
        :
        null
    }
  </div>
};
