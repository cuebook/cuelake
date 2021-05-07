import React from "react";
import style from "./style.module.scss";
import { useParams } from 'react-router-dom';
import apiService from "services/api";
import { useHistory } from "react-router-dom";

export default function NotebookView() {
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
      {
        isEmbedPage 
        ?
        <div className={style.iframeHeader}></div>
        :
        null
      }
      <iframe className={isEmbedPage ? style.embedIframe : style.iframe} src={iframeUrl}></iframe>
    </>
  );
}
