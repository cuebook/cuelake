import ApiService from "./api";
import { store } from 'react-notifications-component';
let apiService = new ApiService()

class NotebookService {
    async getNotebooks(){
        const response = await apiService.get("/api/notebooks/0")
        if(response.success == true)
            return response.data
        else
            return null
    }

    async getSchedules(){
        const response = await apiService.get("/api/schedules/")
        if(response.success == true)
            return response.data
        else    
            return null
    }

    async addNotebookSchedule(notebookId, scheduleId){
        const response = await apiService.post("/api/notebookjob/", {notebookId: notebookId, crontabScheduleId: scheduleId})
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
}
let notebookService = new NotebookService();
export default notebookService
