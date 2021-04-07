import apiService from "./api";
import { store } from 'react-notifications-component';

class NotebookService {
    async getNotebooks(offset){
        const response = await apiService.get("notebooks/" + offset)
        if(response.success == true)
            return response.data
        else
            return null
    }

    async getSchedules(){
        const response = await apiService.get("schedules/")
        if(response.success == true)
            return response.data
        else    
            return null
    }

    async addNotebookSchedule(notebookId, scheduleId){
        const response = await apiService.post("notebookjob/", {notebookId: notebookId, crontabScheduleId: scheduleId})
        if(response.success == true){
            store.addNotification({
                title: "Success!",
                message: "Schedule added successfully",
                type: "success",
                container: "top-right",
            })
            return response.data
        }
        else{
            store.addNotification({
                title: "Error!",
                message: "response.message",
                type: "error",
                container: "top-right",
            })
            return response.data
        }
    }

    async getTimezones(){
        const response = await apiService.get("timezones/")
        if(response.success == true)
            return response.data
        else 
            return null
    }

    async addSchedule(cronTabSchedule, selectedTimezone){
        const response = await apiService.post("schedules/", {"crontab": cronTabSchedule, "timezone": selectedTimezone})
        return response
    }
}
let notebookService = new NotebookService();
export default notebookService
