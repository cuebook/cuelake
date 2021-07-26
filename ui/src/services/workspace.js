import apiService from "./api";

class WorkspaceService {

    async getWorkspaces(){
        const response = await apiService.get("workspace/workspaces")
        return response
    }
}
let workspaceService = new WorkspaceService();
export default workspaceService