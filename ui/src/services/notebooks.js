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

    async getNotebookLogs(notebookJobId, offset){
        const response = await apiService.get("notebookjob/" + notebookJobId + "?offset=" + offset)
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
        return response
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

    async stopNotebook(notebookId){
        const response = await apiService.delete("notebook/" + notebookId)
        return response
    }

    async runNotebook(notebookId){
        const response = await apiService.post("notebook/" + notebookId)
        return response
    }

    async toggleNotebookSchedule(enabled, notebookId){
        const response = await apiService.put("notebookjob/", {notebookId: notebookId, enabled: enabled})
        return response
    }
}
let notebookService = new NotebookService();
export default notebookService
