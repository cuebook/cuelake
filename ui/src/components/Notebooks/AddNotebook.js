import React, { useState, useEffect } from "react";
import { Button, Form, Input, message, Select } from "antd";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-mysql";
import "ace-builds/src-noconflict/theme-chrome";

import style from "./style.module.scss";
import notebookService from "services/notebooks.js";
import connectionService from "services/connection.js";
import { Link } from "react-router-dom";
import { LeftOutlined } from '@ant-design/icons';
import DatasetSelector from "../DatasetSelector/DatasetSelector";

const { Option } = Select;

export default function AddNotebook(props) {
  const [notebookTemplates, setNotebookTemplates] = useState([]);
  const [connections, setConnections] = useState([]);
  const [selectedNotebookTemplate, setSelectedNotebookTemplate] = useState('');
  const [form] = Form.useForm();

  useEffect(() => {
    if (!notebookTemplates.length) {
        fetchNotebookTemplates();
    }
    if (!connections.length) {
        fetchConnections();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchNotebookTemplates = async () => {
     const response = await notebookService.getNotebookTemplates()
     setNotebookTemplates(response.data)
  }

  const fetchConnections = async () => {
    const response = await connectionService.getConnections();
    setConnections(response.data)
  }

  const handleNotebookTemplateSelect = (notebookTemplate) => {
    setSelectedNotebookTemplate(notebookTemplate)
  }

  const addNotebookFormSubmit = async (values) => {
    values["notebookTemplateId"] = selectedNotebookTemplate.id;
    let workspaceId = parseInt(localStorage.getItem("workspaceId"))
    const response = await notebookService.addNotebook(values, workspaceId)
    if(response.success){
        props.onAddNotebookSuccess()
    }
    else{
        message.error(response.message);
    }
  };

  const getConnectionOptions = (field) => {
    let optionElements = [];
    connections.forEach(connection => {
        if(!field.filter || (field.filter && field.filter.indexOf(connection.connectionType) !== -1)){
            optionElements.push(
                <Option value={connection.id}>{connection.name}</Option>
            )
        }
    })
    return optionElements
  }

  const renderInputType = (field) => {
    switch(field.type) {
      case 'text':
        return <Input
            type={"text"}
            className={style.inputArea}
        />;
      case 'connectionSelect':
        return <Select 
            className={style.inputArea}
            notFoundContent={<Link to="/connections"><div>Add Connection</div></Link>}>
            {getConnectionOptions(field)}
        </Select>
      case 'datasetSelector':
        return <DatasetSelector />
      case 'sql':
        return <AceEditor
            mode="mysql"
            theme="chrome"
            name="sqlEditor"
            highlightActiveLine={true}
            setOptions={{
                enableBasicAutocompletion: true,
                enableLiveAutocompletion: true,
                enableSnippets: true,
                showLineNumbers: true,
                tabSize: 2,
                }}
            style={{
                width: "100%",
                height: "15em"
            }}
        />;
      default:
        return <Input
            type={"text"}
            className={style.inputArea}
        />;
    }
  }
  
  let notebookFormElements = []
  if(selectedNotebookTemplate.id){
    selectedNotebookTemplate.formJson.fields.forEach(field => {
        notebookFormElements.push(
            <div
                // style={{ width: field.properties.width }}
                className={style.inputGroup}
                key={field.name}
            >
                <Form.Item 
                    key={field.name} 
                    label={field.label}
                    rules={field.rules}
                    name={field.name}
                >
                    {renderInputType(field)}
                </Form.Item>
            </div>
            )
          }
        )
    }


    let addNotebookFormElement = (
      <div>
        <div className={style.selectedNotebookTemplate}>
            <div className={style.templateBackButton} onClick={()=>setSelectedNotebookTemplate({})}>
                <LeftOutlined />
                Back
            </div>
            <p className={style.selectedNotebookTemplateName}>{selectedNotebookTemplate.name}</p>
        </div>
        <Form 
            layout="vertical" 
            className="mb-2" 
            form={form} 
            onFinish={addNotebookFormSubmit}
            name="addNotebook"
            scrollToFirstError
            hideRequiredMark
        >
          <div className="row">
            {notebookFormElements}
            <div className={style.inputGroup}>
              <Form.Item required name="name" label="Notebook Name" rules={[{"required": true, "message": "Notebook name is required"}]}>
                <Input className={style.inputArea} />
              </Form.Item>
            </div>
          </div>
          <Button
            icon=""
            type="primary"
            className="mr-2"
            htmlType="submit"
          >
            Create Notebook
          </Button>
        </Form>
      </div>
    );

    // Code for rendering select connection type form
    let selectNotebookTemplatElement = (
      <div className={style.items}>
        {notebookTemplates.map((notebookTemplate, index) => (
            <div className={style.notebookTemplate} key={index}>
                <Button
                    style={{ height: "100%", width: "100%" }}
                    onClick={e => handleNotebookTemplateSelect(notebookTemplate)}
                    >
                    {notebookTemplate.name}
                </Button>
            </div>
        ))}
      </div>
    );

    return (
      <div>
        <div className="row">
          {selectedNotebookTemplate.id ? (
            <div className="col-md-8 card offset-md-2 shadow-sm bg-white p-5 mb-5 rounded">
              {addNotebookFormElement}
            </div>
          ) : (
            selectNotebookTemplatElement
          )}
        </div>
      </div>
    );
  }
