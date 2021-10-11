import apiService from "./api";

class NotebookService {
    async getNotebookObject(notebookObjId, workspaceId){
        const response = await apiService.get("genie/notebookObject/" + notebookObjId + "/" + workspaceId)
        if(response.success === true)
            return response.data
        else
            return null
    }

    async getNotebooks(offset, limit, searchText, sorter, filter, workspaceId){
        const response = await apiService.get("genie/notebooks/" + offset + "/" + workspaceId + "?limit="+ limit + "&searchText="+ searchText+ "&sorter="+ JSON.stringify(sorter) + "&filter=" + JSON.stringify(filter))
        if(response.success === true)
            return response.data
        else
            return null
    }

    async getArchivedNotebooks(){
        const response = await apiService.get("genie/notebooks/archive")
        if(response.success === true)
            return response.data
        else
            return null
    }

    async getDriverAndExecutorStatus(){
        const response = await apiService.get("genie/driverAndExecutorStatus/" )
        if(response.success === true)
            return response.data
        else
            return null
    }

    async getNotebooksLight(workspaceId){
        const response = await apiService.get("genie/notebooksLight/" + workspaceId)
        if(response.success === true)
            return response.data
        else
            return null
    }

    async getNotebookLogs(notebookJobId, offset){
        const response = await apiService.get("genie/notebookjob/" + notebookJobId + "?offset=" + offset)
        if(response.success === true)
            return response.data
        else
            return null
    }

    async getSchedules(){
        const response = await apiService.get("genie/schedules/")
        if(response.success === true)
            return response.data
        else    
            return null
    }

    async deleteSchedule(scheduleId){
        const response = await apiService.delete("genie/schedules/" + scheduleId)
        if(response.success === true)
            return response
        else    
            return null
    }
    
    async getSingleSchedule(scheduleId){
        const response = await apiService.get("genie/schedules/" + scheduleId)
        if(response.success === true)
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
        if(response.success === true)
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

    async stopNotebook(notebookId, workspaceId){
        const response = await apiService.delete("genie/notebook/actions/" + notebookId + "/" + workspaceId)
        return response
    }

    async runNotebook(notebookId, workspaceId){
        const response = await apiService.post("genie/notebook/actions/" + notebookId + "/" + workspaceId)
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

    async addNotebook(payload, WorkspaceId){
        const response = await apiService.post("genie/notebook" + "/" + WorkspaceId, payload)
        return response
    }

    async editNotebook(payload, WorkspaceId){
        const response = await apiService.put("genie/notebookObject/" + payload.notebookObjId + "/" + WorkspaceId, payload)
        return response
    }

    async cloneNotebook(notebookId, newNotebookName, workspaceId){
        const response = await apiService.post("genie/notebook/" + notebookId + "/" + workspaceId, {name: newNotebookName})
        return response
    }

    async archiveNotebook(notebookId, notebookName, WorkspaceId){
        const response = await apiService.get("genie/notebook/" + notebookId + "/archive/" + notebookName + "/" + WorkspaceId)
        return response
    }

    async unarchiveNotebook(notebookId, notebookName, WorkspaceId){
        const response = await apiService.get("genie/notebook/" + notebookId + "/unarchive/" + notebookName + "/" + WorkspaceId)
        return response
    }

    async deleteNotebook(notebookId, WorkspaceId){
        const response = await apiService.delete("genie/notebook/" + notebookId + "/" + WorkspaceId)
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

    async getMetastoreTables(){
        const response = await apiService.get("genie/metastoreTables")
        return response
    }

    async getMetastoreColumns(tableId){
        const response = await apiService.get("genie/metastoreColumns/" + tableId)
        return response
    }
}
let notebookService = new NotebookService();
export default notebookService
