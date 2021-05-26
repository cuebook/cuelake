import apiService from "./api";
import { store } from 'react-notifications-component';

class NotebookService {
    async getNotebookObject(notebookObjId){
        const response = await apiService.get("genie/notebookObject/" + notebookObjId)
        if(response.success == true)
            return response.data
        else
            return null
    }

    async getNotebooks(offset, limit, searchText, sortColumn, sortOrder){
        const response = await apiService.get("genie/notebooks/" + offset + "?limit="+ limit + "&searchText="+ searchText+ "&sortColumn="+ sortColumn + "&sortOrder=" + sortOrder)
        if(response.success == true)
            return response.data
        else
            return null
    }

    async getArchivedNotebooks(){
        const response = await apiService.get("genie/notebooks/archive")
        if(response.success == true)
            return response.data
        else
            return null
    }

    async getDriverAndExecutorStatus(){
        const response = await apiService.get("genie/driverAndExecutorStatus/" )
        if(response.success == true)
            return response.data
        else
            return null
    }

    async getNotebooksLight(){
        const response = await apiService.get("genie/notebooksLight")
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

    async deleteSchedule(scheduleId){
        const response = await apiService.delete("genie/schedules/" + scheduleId)
        if(response.success == true)
            return response
        else    
            return null
    }
    

    async getSingleSchedule(scheduleId){
        const response = await apiService.get("genie/schedules/" + scheduleId)
        if(response.success == true)
            return response.data
        else    
            return null
    }
    


    async addNotebookSchedule(notebookId, scheduleId){
        const response = await apiService.post("genie/notebookjob/", {notebookId: notebookId,scheduleId: scheduleId})
        return response
    }

    async getTimezones(){
        const response = await apiService.get("genie/timezones/")
        if(response.success == true)
            return response.data
        else 
            return null
    }

    async addSchedule(cronTabSchedule, selectedTimezone, scheduleName){
        const response = await apiService.post("genie/schedules/", {"crontab": cronTabSchedule, "timezone": selectedTimezone, "name": scheduleName})
        return response
    }
    async updateSchedule(selectedScheduleId,cronTabSchedule, selectedTimezone, scheduleName){
        const response = await apiService.put("genie/schedules/", {"id":selectedScheduleId,"crontab": cronTabSchedule, "timezone": selectedTimezone, "name": scheduleName})
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

    async editNotebook(payload){
        const response = await apiService.put("genie/notebookObject/" + payload.notebookObjId, payload)
        return response
    }

    async cloneNotebook(notebookId, newNotebookName){
        const response = await apiService.post("genie/notebook/" + notebookId, {name: newNotebookName})
        return response
    }

    async archiveNotebook(notebookId, notebookName){
        const response = await apiService.get("genie/notebook/" + notebookId + "/archive/" + notebookName)
        return response
    }

    async unarchiveNotebook(notebookId, notebookName){
        const response = await apiService.get("genie/notebook/" + notebookId + "/unarchive/" + notebookName)
        return response
    }

    async deleteNotebook(notebookId){
        const response = await apiService.delete("genie/notebook/" + notebookId)
        return response
    }

    async unassignSchedule(notebookId){
        const response = await apiService.delete("genie/notebookjob/" + notebookId)
        return response
    }

    async getDatasetDetails(payload){
        const response = await apiService.post("genie/datasetDetails", payload)
        return response
    }

    async getSchemas(){
        const response = await apiService.get("genie/schemas")
        return response
    }
}
let notebookService = new NotebookService();
export default notebookService
