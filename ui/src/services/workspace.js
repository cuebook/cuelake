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
}
let workspaceService = new WorkspaceService();
export default workspaceService