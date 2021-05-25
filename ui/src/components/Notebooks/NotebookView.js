import React, {useState} from "react";
import style from "./style.module.scss";
import { useParams } from 'react-router-dom';
import apiService from "services/api";
import { useHistory } from "react-router-dom";
import SchemaTree from "components/Schema/SchemaTree";


export default function NotebookView() {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)
  const params = useParams();
  const history = useHistory();
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
      <div style={{position: "absolute", width: 420, marginLeft: "720px" }} >
        <SchemaTree/>
      </div>
      <iframe className={isEmbedPage ? style.embedIframe : style.iframe} src={iframeUrl}></iframe>
    </>
  );
}
