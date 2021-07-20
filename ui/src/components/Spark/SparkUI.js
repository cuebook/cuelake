import React from "react";
import style from "./style.module.scss";
import apiService from "services/api";
import { useHistory } from "react-router-dom";

export default function SparkUI() {
  const history = useHistory();
  let iframeUrl = "";
  let isEmbedPage = (history.location.pathname.indexOf("api/redirect") !== -1);
  if(isEmbedPage)
    iframeUrl = "/api/redirect/cuelake" + apiService.spark_base_url;
  else
    iframeUrl = apiService.spark_base_url;
  return (
    <>
      <iframe title="sparkUI" className={isEmbedPage ? style.embedIframe : style.iframe} src={iframeUrl}></iframe>
    </>
  );
}
