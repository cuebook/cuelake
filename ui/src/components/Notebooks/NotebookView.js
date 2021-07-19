import React, {useState} from "react";
import style from "./style.module.scss";
import { useParams } from 'react-router-dom';
import apiService from "services/api";
import { useHistory } from "react-router-dom";
import SchemaTree from "components/Schema/SchemaTree";
import { DatabaseOutlined, LeftOutlined, RightOutlined } from '@ant-design/icons';
import { Tooltip } from "antd";


export default function NotebookView() {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const params = useParams();
  const history = useHistory();

  const toggleSchemaBrowser = () => {
    setIsDrawerOpen(!isDrawerOpen);
  }

  let notebookId = params.notebookId;
  let iframeUrl = "";
  let isEmbedPage = (history.location.pathname.indexOf("api/redirect") !== -1);
  if(isEmbedPage){
    iframeUrl = "/api/redirect/cuelake" + apiService.zeppelin_base_url + "/#/notebook/" + notebookId;
  }
  else{
    iframeUrl = apiService.zeppelin_base_url + "/#/notebook/" + notebookId;
  }
  return (
    <>
      <div className={`${style.schemaBrowser} ${ isDrawerOpen ? style.open : "" }`} >
        <Tooltip title={(isDrawerOpen ? "Close" : "Open") +  " Schema Browser"}>
          <div className={style.schemaBrowserDrawerButton} onClick={() => toggleSchemaBrowser()}>
            {
              isDrawerOpen ? <RightOutlined style={{fontSize: "10px"}} /> : <LeftOutlined style={{fontSize: "10px"}} />
            }
            <br />
            <br />
            
              <DatabaseOutlined style={{fontSize: "18px"}} />
            
          </div>
        </Tooltip>
        <div className={style.schemaTreeWrapper}>
          <SchemaTree/>
        </div>
      </div>
      <iframe title="ZeppelinNotebook" className={isEmbedPage ? style.embedIframe : style.iframe} src={iframeUrl}></iframe>
    </>
  );
}
