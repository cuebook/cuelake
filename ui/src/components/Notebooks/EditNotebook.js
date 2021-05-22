import React, { useState, useEffect, useRef } from "react";
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
import SchemaTree from "components/Schema/SchemaTree";

const { Option } = Select;

export default function EditNotebook(props) {
  const [notebookTemplates, setNotebookTemplates] = useState([]);
  const [connections, setConnections] = useState([]);
  const [selectedNotebookTemplate, setSelectedNotebookTemplate] = useState('');
  const [selectedNotebook, setSelectedNotebook] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    if (!selectedNotebook) {
        fetchNotebookObject(props.notebookObjId);
    }
    if (!connections.length) {
        fetchConnections();
    }
  }, []);

  const fetchNotebookObject = async (notebookObjId) => {
    const response = await notebookService.getNotebookObject(notebookObjId)
    setSelectedNotebook(response)
 }

  const fetchConnections = async () => {
    const response = await connectionService.getConnections();
    setConnections(response.data)
  }

  const editNotebookFormSubmit = async (values) => {
    values["notebookObjId"] = props.notebookObjId
    const response = await notebookService.editNotebook(values)
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

  const renderInputType = (field, initValForDatasetSelector) => {
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
        return <DatasetSelector defaultLocation={initValForDatasetSelector}  />
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
  let defaultNotebookName = "" 
  if(selectedNotebook){
    defaultNotebookName = selectedNotebook.defaultPayload.name
    selectedNotebook.notebookTemplate.formJson.fields.forEach(field => {
        let fieldInitValue = field.type == "datasetSelector" ? undefined : selectedNotebook.defaultPayload[field.name]
        let initValForDatasetSelector = field.type == "datasetSelector" ? JSON.parse(selectedNotebook.defaultPayload[field.name]).spec.ioConfig.inputSource.prefixes[0] : null
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
                    initialValue={fieldInitValue}
                >
                    {renderInputType(field, initValForDatasetSelector)}
                </Form.Item>
            </div>
            )
          }
        )
    }


    let editNotebookFormElement = (
      <div>
        <div className={style.selectedNotebookTemplate}>
            <p className={style.selectedNotebookTemplateName}>{selectedNotebookTemplate.name}</p>
        </div>
        <Form 
            layout="vertical" 
            className="mb-2" 
            form={form} 
            onFinish={editNotebookFormSubmit}
            name="addNotebook"
            scrollToFirstError
            hideRequiredMark
        >
          <div className="row">
            {notebookFormElements}
            <div className={style.inputGroup}>
              <Form.Item initialValue={defaultNotebookName} required name="name" label="Notebook Name" rules={[{"required": true, "message": "Notebook name is required"}]}>
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
            Update Notebook
          </Button>
        </Form>
      </div>
    );

    return (
      <div>
        <SchemaTree/>
        <div className="row">
            <div className="col-md-8 card offset-md-2 shadow-sm bg-white p-5 mb-5 rounded">
              {selectedNotebook ? editNotebookFormElement : null}
            </div>
        </div>
      </div>
    );
  }
