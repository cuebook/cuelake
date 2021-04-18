import { getCookie } from "./general.js";

class ApiService {
  host = "";
  base_url = this.host + "api/";
  zeppelin_base_url = "/zeppelin";
  
  async get(endpoint) {
    let token = this.getCsrfToken();
    let response = await fetch(this.base_url + endpoint, {
      credentials: "include",
      method: "GET",
      mode: "cors",
      headers: { "content-type": "application/json", "X-CSRFToken": token }
    });
    let resBody = await response.json();
    return resBody;
  }

  async post(endpoint, data) {
    let token = this.getCsrfToken();
    let response = await fetch(this.base_url + endpoint, {
      credentials: "include",
      method: "POST",
      mode: "cors",
      body: JSON.stringify(data),
      headers: { "content-type": "application/json", "X-CSRFToken": token }
    });
    let resBody = await response.json();
    return resBody;
  }

  async put(endpoint, data) {
    let token = this.getCsrfToken();
    let response = await fetch(this.base_url + endpoint, {
      credentials: "include",
      method: "PUT",
      mode: "cors",
      body: JSON.stringify(data),
      headers: { "content-type": "application/json", "X-CSRFToken": token }
    });
    let resBody = await response.json();
    return resBody;
  }

  async delete(endpoint, data) {
    let token = this.getCsrfToken();
    let response = await fetch(this.base_url + endpoint, {
      credentials: "include",
      method: "DELETE",
      mode: "cors",
      body: data,
      headers: { "content-type": "application/json", "X-CSRFToken": token }
    });
    let resBody = await response.json();
    return resBody;
  }

  getCsrfToken = () => {
    let name = "csrftoken";
    let token = getCookie(name);
    return token ? token : "";
  };
}

let apiService = new ApiService()
export default apiService;