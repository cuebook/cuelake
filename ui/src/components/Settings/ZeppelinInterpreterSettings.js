import React from "react";
import style from "./style.module.scss";
import apiService from "services/api";

export default function ZeppelinInterpreterSettings() {
  let iframeUrl = apiService.zeppelin_base_url + "/#/interpreter";
  return (
    <>
      <iframe className={style.iframe} src={iframeUrl}></iframe>
    </>
  );
}
