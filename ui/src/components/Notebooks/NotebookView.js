import React from "react";
import style from "./style.module.scss";
import { useParams } from 'react-router-dom';
import apiService from "services/api";

export default function NotebookView() {
  const params = useParams();
  let notebookId = params.notebookId;
  let iframeUrl = apiService.zeppelin_base_url + "/#/notebook/" + notebookId;
  return (
    <>
      <iframe className={style.iframe} src={iframeUrl}></iframe>
    </>
  );
}
