import apiService from "./api";

class WorkspaceService {

    async getWorkspaces(){
        const response = await apiService.get("workspace/workspaces")
        return response
    }

    async getImageTags(repository){
        const response = await apiService.get("workspace/dockerimages/" + repository)
        return response
    }

    async createAndStartWorkspaceServer(workspace, workspaceConfig){
        const response = await apiService.post("workspace/createAndStartWorkspaceServer", {workspace: workspace, workspaceConfig: workspaceConfig})
        return response
    }

    async stopWorkspaceServer(id){
        const response = await apiService.delete("workspace/workspaceServer/" + id)
        return response
    }

    async startWorkspaceServer(id){
        const response = await apiService.post("workspace/workspaceServer/" + id)
        return response
    }

    async switchWorkspaceServer(id){
        const response = await apiService.post("workspace/switchWorkspaceServer/" + id)
        return response
    }

    async deleteWorkspaceServer(id){
        const response = await apiService.delete("workspace/" + id , {id: id})
        return response
    }
}
let workspaceService = new WorkspaceService();
export default workspaceService