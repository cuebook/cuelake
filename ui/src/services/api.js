class ApiService {
  constructor(basePath){
    if(process.env.NODE_ENV === "development"){
      // Development Settings
      this.host = "http://localhost:8000";
      this.base_url = this.host + basePath + "/api/";
      this.zeppelin_base_url = "http://localhost:8080";
      this.spark_base_url = "http://localhost:4040";
    }
    else{
      // Production Settings
      this.host = "";
      this.base_url = this.host + basePath + "/api/";
      this.zeppelin_base_url = "/zeppelin";
      this.spark_base_url = "/sparkui/jobs";
    }
  }
  
  async get(endpoint) {
    if (!document.hidden){
      let response = await fetch(this.base_url + endpoint, {
        method: "GET",
        headers: { "content-type": "application/json"}
      });
      let resBody = await response.json();
      return resBody;
    } else {
      return {};
    }
  }

  async post(endpoint, data) {
    let response = await fetch(this.base_url + endpoint, {
      method: "POST",
      body: JSON.stringify(data),
      headers: { "content-type": "application/json"}
    });
    let resBody = await response.json();
    return resBody;
  }

  async put(endpoint, data) {
    let response = await fetch(this.base_url + endpoint, {
      method: "PUT",
      body: JSON.stringify(data),
      headers: { "content-type": "application/json"}
    });
    let resBody = await response.json();
    return resBody;
  }

  async delete(endpoint, data) {
    let response = await fetch(this.base_url + endpoint, {
      method: "DELETE",
      body: data,
      headers: { "content-type": "application/json"}
    });
    let resBody = await response.json();
    return resBody;
  }


  async upload(endpoint, data, fileName) {
    const formData = new FormData();
    formData.append(fileName, data);
    let response = await fetch(this.base_url + endpoint, {
      credentials: "include",
      method: "POST",
      mode: "cors",
      body: formData,
      headers: { "X-Requested-With": "XMLHttpRequest" }
    });
    let resBody = await response.json();
    return resBody;
  }

}

let basePath = "";
if (window.location.pathname.indexOf("api/redirect/cuelake") !== -1){
  basePath = "/api/redirect/cuelake";
}
let apiService = new ApiService(basePath)
export default apiService;