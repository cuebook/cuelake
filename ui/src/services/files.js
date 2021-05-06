import apiService from "./api";
import { store } from 'react-notifications-component';
import { message } from "antd";
import { notification } from "antd";


class FilesService {
    async getFiles(offset){
        const response = await apiService
        .get("files/files/" + offset)
        .catch(error => {});
        if(response && response.success == true)
            return response.data
        else
            return null
    }

    async uploadFile(file, fileName) {
      const response = await apiService
      .upload("files/file", file, fileName)
      .catch(error => {});
      return response
    }

    async deleteFile(key) {
      const response = await apiService.delete("files/file/"+key)
      return response
    }
}
let filesService = new FilesService();
export default filesService
