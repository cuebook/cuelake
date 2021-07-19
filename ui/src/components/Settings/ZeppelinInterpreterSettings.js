import React from "react";
import style from "./style.module.scss";
import apiService from "services/api";
import { useHistory } from "react-router-dom";

export default function ZeppelinInterpreterSettings() {
  const history = useHistory();
  let iframeUrl = "";
  let isEmbedPage = (history.location.pathname.indexOf("api/redirect") !== -1);
  if(isEmbedPage)
    iframeUrl = "/api/redirect/cuelake" + apiService.zeppelin_base_url + "/#/interpreter";
  else
    iframeUrl = apiService.zeppelin_base_url + "/#/interpreter";
  return (
    <>
      <iframe title="zeppelinInterpreterSettings" className={isEmbedPage ? style.embedIframe : style.iframe} src={iframeUrl}></iframe>
    </>
  );
}
