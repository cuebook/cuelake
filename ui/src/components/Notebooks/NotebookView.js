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
  if(history.location.pathname.indexOf("api/redirect") !== -1)
    iframeUrl = "/api/redirect/cuelake" + apiService.zeppelin_base_url + "/#/notebook/" + notebookId;
  else
    iframeUrl = apiService.zeppelin_base_url + "/#/notebook/" + notebookId;
  return (
    <>
      <iframe className={style.iframe} src={iframeUrl}></iframe>
    </>
  );
}
