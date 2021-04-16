import React, { useState, useEffect, useRef } from "react";
import { Button, Form, Input, message, Select } from "antd";
import { useHistory } from "react-router-dom";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-sql";
import "ace-builds/src-noconflict/theme-github";

import style from "./style.module.scss";
import notebookService from "services/notebooks.js";
import connectionService from "services/connection.js";
import { Link } from "react-router-dom";

const { Option } = Select;

export default function AddNotebook(props) {
  const [notebookTemplates, setNotebookTemplates] = useState([]);
  const [connections, setConnections] = useState([]);
  const [selectedNotebookTemplate, setSelectedNotebookTemplate] = useState('');
  const [form] = Form.useForm();
  const history = useHistory();

  useEffect(() => {
    if (!notebookTemplates.length) {
        fetchNotebookTemplates();
    }
    if (!connections.length) {
        fetchConnections();
    }
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
    const response = await notebookService.addNotebook(values)
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
        if(!field.filter || field.filter && field.filter.indexOf(connection.connectionType) !== -1){
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
      case 'sql':
        return <AceEditor
            mode="sql"
            theme="github"
            // onChange={onChange}
            name="UNIQUE_ID_OF_DIV"
            editorProps={{ $blockScrolling: true }}
            enableBasicAutocompletion={true}
            enableLiveAutocompletion={true}
            setOptions={{
                
                enableSnippets: false,
                showLineNumbers: true,
                tabSize: 4,
                useWorker: false
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


    let addConnectionFormElement = (
      <div>
        <p>{selectedNotebookTemplate.name}</p>
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
            <div className={style.inputGroup}>
              <Form.Item hasFeedback name="name" label="Notebook Name">
                <Input className={style.inputArea} />
              </Form.Item>
            </div>
            {notebookFormElements}
          </div>
          <Button
            icon=""
            type="primary"
            className="mr-2"
            htmlType="submit"
          >
            SUBMIT
          </Button>
        </Form>
      </div>
    );

    // Code for rendering select connection type form
    let selectNotebookTemplatElement = (
      <div className={style.items}>
        {notebookTemplates.map((notebookTemplate, index) => (
            <div className={style.item} key={index}>
              <div className={style.itemContent}>
                <div className={style.itemControl}>
                  <Button
                    style={{ height: "100%", width: "100%" }}
                    onClick={e => handleNotebookTemplateSelect(notebookTemplate)}
                  >
                    {notebookTemplate.name}
                  </Button>
                </div>
                {/* 
                TODO - Add Images
                  <img
                  style={{ width: "50%", height: "50%" }}
                  src={require("assets/media/" + item.name + ".png")}
                  alt={connectionType.name}
                /> */}
              </div>
              <div className="text-gray-6"></div>
            </div>
        ))}
      </div>
    );

    return (
      <div>
        <div className="row">
          {selectedNotebookTemplate.id ? (
            <div className="col-md-8 card offset-md-2 shadow-sm bg-white p-5 mb-5 rounded">
              {addConnectionFormElement}
            </div>
          ) : (
            selectNotebookTemplatElement
          )}
        </div>
      </div>
    );
  }
