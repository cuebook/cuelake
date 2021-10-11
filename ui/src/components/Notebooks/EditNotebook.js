import React, { useState, useEffect } from "react";
import { Button, Form, Input, message, Select, Popconfirm } from "antd";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-mysql";
import "ace-builds/src-noconflict/theme-chrome";

import style from "./style.module.scss";
import notebookService from "services/notebooks.js";
import connectionService from "services/connection.js";
import { Link } from "react-router-dom";
import DatasetSelector from "../DatasetSelector/DatasetSelector";

const { Option } = Select;

export default function EditNotebook(props) {
  const [connections, setConnections] = useState([]);
  const [selectedNotebook, setSelectedNotebook] = useState(null);
  const [form] = Form.useForm();

  useEffect(() => {
    if (!selectedNotebook) {
        fetchNotebookObject(props.notebookObjId);
    }
    if (!connections.length) {
        fetchConnections();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fetchNotebookObject = async (notebookObjId) => {
    let workspaceId = parseInt(localStorage.getItem("workspaceId"))
    const response = await notebookService.getNotebookObject(notebookObjId, workspaceId)
    setSelectedNotebook(response)
 }

  const fetchConnections = async () => {
    const response = await connectionService.getConnections();
    setConnections(response.data)
  }

  const editNotebookFormSubmit = async (values) => {
    values["notebookObjId"] = props.notebookObjId
    let workspaceId = parseInt(localStorage.getItem("workspaceId"))
    const response = await notebookService.editNotebook(values, workspaceId)
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
        let fieldInitValue = field.type === "datasetSelector" ? undefined : selectedNotebook.defaultPayload[field.name]
        let initValForDatasetSelector = field.type === "datasetSelector" ? JSON.parse(selectedNotebook.defaultPayload[field.name]).spec.ioConfig.inputSource.prefixes[0] : null
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
          
          <Popconfirm
            title={"Updating this Form will overwrite the Notebook. If you made any changes to the Notebook earlier, they will be lost."}
            onConfirm={form.submit}
            okText="Overwrite"
            cancelText="Cancel"
          >
            <Button
              icon=""
              type="primary"
              className="mr-2"
            >
              Update Notebook
            </Button>
          </Popconfirm>
        </Form>
      </div>
    );

    return (
      <div>
        <div className="row">
            <div className="col-md-8 card offset-md-2 shadow-sm bg-white p-5 mb-5 rounded">
              {selectedNotebook ? editNotebookFormElement : null}
            </div>
        </div>
      </div>
    );
  }
