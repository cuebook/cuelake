import React, { useState, useEffect } from "react";
import { Steps, Popover, Form, Input, Button, Select, message } from 'antd';
import { DatabaseOutlined, AppstoreOutlined, CloudServerOutlined, SmileOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import style from "./style.module.scss";
import workspaceService from "services/workspace";
import { useHistory } from "react-router-dom";

const { Step } = Steps;
const { TextArea } = Input;
const { Option } = Select;

export default function AddWorkspace() {
    const [form] = Form.useForm();
    const [currentStep, setCurrentStep] = useState(0);
    const [storage, setStorage] = useState("S3");
    const [sparkImages, setSparkImages] = useState([]);
    const [interpreterImages, setInterpreterImages] = useState([]);
    const [workspace, setWorkspace] = useState({});
    const [workspaceConfig, setWorkspaceConfig] = useState({});
    const history = useHistory();
    
    const storageTypes = [
        "S3",
        "GCS",
        "ADLS"
    ]

    const setWorksapce = (formdata) => {
        setWorkspace(formdata)
        setCurrentStep(1)
    }

    const updateStorageConfig = (formdata) => {
        let workspaceConfigData = {storage: storage, ...formdata, ...workspaceConfig}
        setWorkspaceConfig(workspaceConfigData)
        setCurrentStep(2)
    }

    const updateServerConfig = (formdata) => {
        setWorkspaceConfig({...workspaceConfig, ...formdata})
        setCurrentStep(3)
    }

    const handleStorageTypeSelect = (storage) => {
        setStorage(storage)
    }

    const createWorkspace = () => {
        const response = workspaceService.createAndStartWorkspaceServer(workspace, workspaceConfig)
        if(response.success){
            window.location.href='/dashboard'
        }
        else{
            message.error(response.message);
        }
    }

    const getSparkImages = async () => {
        const response = await workspaceService.getImageTags("spark")
        setSparkImages(response.data)
    }

    const getInterpreterImages = async () => {
        const response = await workspaceService.getImageTags("zeppelin-interpreter")
        setInterpreterImages(response.data)
    }

    useEffect(() => {
        if (!sparkImages.length) {
          getSparkImages();
        }
        if (!interpreterImages.length) {
            getInterpreterImages();
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
      }, []);

    const navigateToDashboard = () => {
        history.push("/api/redirect/cuelake/dashboard");
    } 

    return (
        <div className={style.addWorksapceForm}>
            <div className={style.addWorkspaceSteps}>
                <Steps current={currentStep}>
                    <Step title="Workspace" icon={<AppstoreOutlined />} />
                    <Step title="Storage" icon={<DatabaseOutlined />} />
                    <Step title="Server" icon={<CloudServerOutlined />}/>
                    <Step title="Review" icon={<SmileOutlined />}/>
                </Steps>
            </div>
            <div className={style.workspaceForm}>
            { currentStep === 0 ?
                <Form 
                    layout="vertical" 
                    className="mb-2" 
                    form={form} 
                    onFinish={setWorksapce}
                    name="addConnection"
                    scrollToFirstError
                    hideRequiredMark
                >
                    <div>
                        <div className={style.formItem} style={{ width: "100%" }}>
                            <Form.Item hasFeedback name="name" label="Workspace Name" rules={[{message: "Name can't be empty", required: true}]}>
                                <Input className={style.inputArea} />
                            </Form.Item>
                        </div>
                        <div className={style.formItem} style={{ width: "100%" }}>
                            <Form.Item hasFeedback name="description" label="Description" rules={[{message: "Description can't be empty", required: true}]}>
                                <TextArea className={style.inputArea} rows={5} />
                            </Form.Item>
                        </div>
                    </div>
                    <div className={style.buttonDiv}>
                        <Button
                            icon=""
                            type="primary"
                            htmlType="submit"
                        >
                            Next
                        </Button>
                    </div>
                </Form> 
                :
                null
            }
            { currentStep === 1 ?
                <Form 
                    layout="vertical" 
                    className="mb-2" 
                    form={form} 
                    onFinish={updateStorageConfig}
                    name="addConnection"
                    scrollToFirstError
                    hideRequiredMark
                >
                    <div className={style.storageTypes}>
                        {storageTypes.map((storageType, index) => (
                            <div className={storage === storageType ? style.selectedStorage : style.storage} key={index} onClick={e => handleStorageTypeSelect(storageType)}>
                                <div className={style.storageLogo} style={{backgroundImage: `url(${require("assets/img/" + storageType + ".svg")})`}}>
                                </div>
                                <p>{storageType}</p>
                            </div>
                        ))}
                    </div>
                    {storage === "S3" ?
                        <div>
                            <div className={style.formItem} style={{ width: "100%" }}>
                                <Form.Item hasFeedback name="warehouseLocation" 
                                    label={
                                        <>
                                        <span className="mr-2">Data Location</span>
                                        <Popover 
                                            content={
                                                <span>Location where your hive table data will be stored</span>
                                            } 
                                            trigger="hover"
                                        >
                                            <QuestionCircleOutlined />
                                        </Popover>
                                        </>
                                    } 
                                    rules={[{message: "Location can't be empty", required: true}]}>
                                    <Input className={style.inputArea} placeholder="s3://BUCKET_NAME/DIRECTORY" />
                                </Form.Item>
                            </div>
                            <div className={style.formItem} style={{ width: "100%" }}>
                                <Form.Item hasFeedback name="s3AccessKey" label="S3 Access Key" rules={[{message: "Access Key can't be empty", required: true}]}>
                                    <Input className={style.inputArea} />
                                </Form.Item>
                            </div>
                            <div className={style.formItem} style={{ width: "100%" }}>
                                <Form.Item hasFeedback name="s3SecretKey" label="S3 Secret Key" rules={[{message: "Secret Key can't be empty", required: true}]}>
                                    <Input className={style.inputArea} type="password"/>
                                </Form.Item>
                            </div>
                        </div>
                        :
                        null
                    }
                    {storage === "GCS" ?
                        <div>
                            <div className={style.formItem} style={{ width: "100%" }}>
                                <Form.Item hasFeedback name="warehouseLocation" 
                                    label={
                                        <>
                                        <span className="mr-2">Data Location</span>
                                        <Popover 
                                            content={
                                                <span>Location where your hive table data will be stored</span>
                                            } 
                                            trigger="hover"
                                        >
                                            <QuestionCircleOutlined />
                                        </Popover>
                                        </>
                                    } 
                                    rules={[{message: "Location can't be empty", required: true}]}>
                                    <Input className={style.inputArea} placeholder="gs://BUCKET_NAME/DIRECTORY" />
                                </Form.Item>
                            </div>
                            <div className={style.formItem} style={{ width: "100%" }} rules={[{message: "Account Key can't be empty", required: true}]}>
                                <Form.Item hasFeedback name="googleKey" label="Account Key JSON">
                                    <TextArea className={style.inputArea} placeholder="// Paste your account key json contents here" />
                                </Form.Item>
                            </div>
                        </div>
                        :
                        null
                    }
                    {storage === "ADLS" ?
                        <div>
                            <div className={style.formItem} style={{ width: "100%" }}>
                                <Form.Item hasFeedback name="warehouseLocation" 
                                    label={
                                        <>
                                        <span className="mr-2">Data Location</span>
                                        <Popover 
                                            content={
                                                <span>Location where your hive table data will be stored</span>
                                            } 
                                            trigger="hover"
                                        >
                                            <QuestionCircleOutlined />
                                        </Popover>
                                        </>
                                    } 
                                    rules={[{message: "Location can't be empty", required: true}]}>
                                    <Input className={style.inputArea} placeholder="wasbs://STORAGE_ACCOUNT@CONTAINER.blob.core.windows.net/DIRECTORY" />
                                </Form.Item>
                            </div>
                            <div className={style.formItem} style={{ width: "100%" }} rules={[{message: "Storage Account Name can't be empty", required: true}]}>
                                <Form.Item hasFeedback name="azureAccount" label="Storage Account Name">
                                    <Input className={style.inputArea} />
                                </Form.Item>
                            </div>
                            <div className={style.formItem} style={{ width: "100%" }} rules={[{message: "Storage Account Key can't be empty", required: true}]}>
                                <Form.Item hasFeedback name="azureKey" label="Storage Account Key">
                                    <Input type="password" className={style.inputArea} />
                                </Form.Item>
                            </div>
                        </div>
                        :
                        null
                    }
                    <div className={style.buttonDiv}>
                        <Button
                            icon=""
                            type="default"
                            className="mr-2"
                            onClick={()=>setCurrentStep(0)}
                        >
                            Previous
                        </Button>
                        <Button
                            icon=""
                            type="primary"
                            htmlType="submit"
                        >
                            Next
                        </Button>
                    </div>
                </Form> 
                :
                null
            }
            { currentStep === 2 ?
                <Form 
                    layout="vertical" 
                    className="mb-2"
                    form={form} 
                    onFinish={updateServerConfig}
                    name="addConnection"
                    scrollToFirstError
                    hideRequiredMark
                    initialValues={{inactivityTimeout: 1800}}
                >
                    <div className={style.formItem} style={{ width: "100%" }}>
                        <Form.Item 
                            hasFeedback 
                            name="zeppelinInterpreterImage" 
                            rules={[{message: "Zeppelin Interpreter Image can't be empty", required: true}]}
                            label={
                                <>
                                <span className="mr-2">Zeppelin Interpreter Image</span>
                                <Popover 
                                    content={
                                        <span>Zeppelin Interpreter Docker Image to be used with this workspace</span>
                                    } 
                                    trigger="hover"
                                >
                                    <QuestionCircleOutlined />
                                </Popover>
                                </>
                            }
                        >
                            <Select>
                                {interpreterImages.map((image, index) => (
                                    <Option value={image.name} key={image.id}>{image.name}</Option>
                                ))}
                            </Select>
                        </Form.Item>
                    </div>
                    <div className={style.formItem} style={{ width: "100%" }}>
                        <Form.Item 
                            hasFeedback 
                            name="sparkImage" 
                            rules={[{message: "Spark Image can't be empty", required: true}]}
                            label={
                                <>
                                <span className="mr-2">Spark Image</span>
                                <Popover 
                                    content={
                                        <span>Spark Docker Image to be used with this workspace</span>
                                    } 
                                    trigger="hover"
                                >
                                    <QuestionCircleOutlined />
                                </Popover>
                                </>
                            }
                        >
                            <Select>
                                {sparkImages.map((image, index) => (
                                    <Option value={image.name} key={image.id}>{image.name}</Option>
                                ))}
                            </Select>
                        </Form.Item>
                    </div>
                    <div className={style.formItem} style={{ width: "100%" }}>
                        <Form.Item 
                            hasFeedback 
                            name="acidProvider"
                            rules={[{message: "ACID & Data Versioning Provider can't be empty", required: true}]}
                            label={
                                <>
                                <span className="mr-2">ACID & Data Versioning Provider</span>
                                <Popover 
                                    content={
                                        <span>You can choose <a href={"https://delta.io/"}>Delta lake</a> or <a href={"https://iceberg.apache.org/"}>Apache Iceberg</a>, the jars and env variables for the choosen storage will be set automatically. <a href={"https://cuelake.cuebook.ai"}>Learn more</a></span>
                                    } 
                                    trigger="hover"
                                >
                                    <QuestionCircleOutlined />
                                </Popover>
                                </>
                            }>
                            <Select>
                                <Option value="delta">Delta Lake</Option>
                                <Option value="iceberg">Apache Iceberg</Option>
                                <Option value="none">None</Option>
                            </Select>
                        </Form.Item>
                    </div>
                    <div className={style.formItem} style={{ width: "100%" }}>
                        <Form.Item 
                            hasFeedback 
                            name="inactivityTimeout" 
                            rules={[{message: "Auto Terminate Interpreter Inactivity Time (seconds)", required: true}]}
                            label={
                                <>
                                <span className="mr-2">Auto Terminate Interpreter Inactivity Time (seconds)</span>
                                <Popover 
                                    content={
                                        <span>Interpreters attached to a notebook will get terminated automatically to save infra cost if they are inactive for this amount of time</span>
                                    } 
                                    trigger="hover"
                                >
                                    <QuestionCircleOutlined />
                                </Popover>
                                </>
                            }
                        >
                            <Input type="number"></Input>
                        </Form.Item>
                    </div>
                    <div className={style.buttonDiv}>
                        <Button
                            icon=""
                            type="default"
                            className="mr-2"
                            onClick={()=>setCurrentStep(1)}
                        >
                            Previous
                        </Button>
                        <Button
                            icon=""
                            
                            type="primary"
                            htmlType="submit"
                        >
                            Next
                        </Button>
                    </div>
                </Form> 
                :
                null
            }
            { currentStep === 3 ?
                <Form 
                    layout="vertical" 
                    className={style.preview}
                    form={form} 
                    onFinish={createWorkspace}
                    name="addConnection"
                    scrollToFirstError
                    hideRequiredMark
                >
                    <label>Name</label>
                    <Input disabled value={workspace.name}></Input>
                    <label>Description</label>
                    <TextArea disabled value={workspace.description}></TextArea>
                    <label>Storage</label>
                    <Input disabled value={workspaceConfig.storage}></Input>
                    <label>Data Location</label>
                    <Input disabled value={workspaceConfig.warehouseLocation}></Input>
                    <label>Spark Image</label>
                    <Input disabled value={workspaceConfig.sparkImage}></Input>
                    <label>Zeppelin Interpreter Image</label>
                    <Input disabled value={workspaceConfig.zeppelinInterpreterImage}></Input>
                    <label>ACID & Data Versioning Provider</label>
                    <Input disabled value={{'delta':'Delta Lake', 'iceberg': 'Apache Iceberg', 'none': 'None'}[workspaceConfig.acidProvider]}></Input>
                    <label>Auto Terminate Interpreter Inactivity Time (seconds)</label>
                    <Input disabled value={workspaceConfig.inactivityTimeout}></Input>

                    <div className={`${style.buttonDiv} mt-4`}>
                        <Button
                            icon=""
                            type="default"
                            className="mr-2"
                            onClick={()=>setCurrentStep(2)}
                        >
                            Previous
                        </Button>
                        <Button
                            icon=""
                            type="primary"
                            htmlType="submit"
                        >
                            Cretae Workspace and Start Server
                        </Button>
                    </div>
                </Form>
                :
                null
            }
            </div>
        </div>
    );
}
