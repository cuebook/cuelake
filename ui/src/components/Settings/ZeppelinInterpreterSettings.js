import React from "react";
import style from "./style.module.scss";
import apiService from "services/api";
import { useHistory } from "react-router-dom";

export default function ZeppelinInterpreterSettings() {
  const history = useHistory();
  let iframeUrl = "";
  if(history.location.pathname.indexOf("api/redirect") !== -1)
    iframeUrl = "/api/redirect/cuelake" + apiService.zeppelin_base_url + "/#/interpreter";
  else
    iframeUrl = apiService.zeppelin_base_url + "/#/interpreter";
  return (
    <>
      <iframe className={style.iframe} src={iframeUrl}></iframe>
    </>
  );
}
