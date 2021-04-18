import apiService from "./api";
import { store } from 'react-notifications-component';

class NotebookService {
    async getNotebooks(offset){
        const response = await apiService.get("genie/notebooks/" + offset)
        if(response.success == true)
            return response.data
        else
            return null
    }

    async getNotebookLogs(notebookJobId, offset){
        const response = await apiService.get("genie/notebookjob/" + notebookJobId + "?offset=" + offset)
        if(response.success == true)
            return response.data
        else
            return null
    }

    async getSchedules(){
        const response = await apiService.get("genie/schedules/")
        if(response.success == true)
            return response.data
        else    
            return null
    }

    async addNotebookSchedule(notebookId, scheduleId){
        const response = await apiService.post("genie/notebookjob/", {notebookId: notebookId, crontabScheduleId: scheduleId})
        return response
    }

    async getTimezones(){
        const response = await apiService.get("genie/timezones/")
        if(response.success == true)
            return response.data
        else 
            return null
    }

    async addSchedule(cronTabSchedule, selectedTimezone){
        const response = await apiService.post("genie/schedules/", {"crontab": cronTabSchedule, "timezone": selectedTimezone})
        return response
    }

    async stopNotebook(notebookId){
        const response = await apiService.delete("genie/notebook/actions/" + notebookId)
        return response
    }

    async runNotebook(notebookId){
        const response = await apiService.post("genie/notebook/actions/" + notebookId)
        return response
    }

    async toggleNotebookSchedule(enabled, notebookId){
        const response = await apiService.put("genie/notebookjob/", {notebookId: notebookId, enabled: enabled})
        return response
    }

    async getNotebookTemplates(){
        const response = await apiService.get("genie/notebookTemplates/")
        return response
    }

    async addNotebook(payload){
        const response = await apiService.post("genie/notebook", payload)
        return response
    }

    async cloneNotebook(notebookId, newNotebookName){
        const response = await apiService.post("genie/notebook/" + notebookId, {name: newNotebookName})
        return response
    }

    async deleteNotebook(notebookId){
        const response = await apiService.delete("genie/notebook/" + notebookId)
        return response
    }
}
let notebookService = new NotebookService();
export default notebookService
