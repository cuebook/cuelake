import apiService from "./api";
import { store } from 'react-notifications-component';
import { message } from "antd";

class WorkflowsService {
    async getWorkflows(offset, limit, sortColumn, sortOrder){
        const response = await apiService.get("workflows/workflows/" + offset + "?limit="+ limit +"&sortColumn=" + sortColumn + "&sortOrder=" + sortOrder)
        if(response.success == true)
            return response.data
        else
            return null
    }


    async getWorkflowRuns(workflowId, offset){
        const response = await apiService.get("workflows/workflowRuns/" + workflowId +"/"+ offset)
        if(response.success == true)
            return response.data
        else
            return null
    }

    async getWorkflowRunLogs(workflowRunId){
        const response = await apiService.get("workflows/workflowRunLogs/" + workflowRunId)
        if(response.success == true)
            return response.data
        else
            return null
    }

    async setWorkflows(data){
        const response = await apiService.post("workflows/workflows", data)
        if(response.success == true)
            return response.success
        else
            message.error(response.message);
            return null
    }

    async runWorkflow(workflowId){
        const response = await apiService.get("workflows/runWorkflow/" + workflowId)
        if(response.success == true)
            return response.data
        else
            message.error(response.message);
            return null
    }

    async stopWorkflow(workflowId){
        const response = await apiService.get("workflows/stopWorkflow/" + workflowId)
        if(response.success == true)
            return response.data
        else
            message.error(response.message);
            return null
    }

    async deleteWorkflow(workflowId){
        const response = await apiService.delete("workflows/workflow/" + workflowId)
        if(response.success == true)
            return response.data
        else
            message.error(response.message);
            return null
    }

    async updateTriggerWorkflow(workflowId, data){
        const response = await apiService.post("workflows/updateTriggerWorkflow/" + workflowId, data)
        if(response.success == true)
            return response.data
        else
            message.error(response.message);
            return null
    }

    async updateWorkflowSchedule(workflowId, data){
        const response = await apiService.post("workflows/updateSchedule/" + workflowId, data)
        if(response.success == true)
            return response.data
        else
            message.error(response.message);
            return null
    }

}
let workflowsService = new WorkflowsService();
export default workflowsService
