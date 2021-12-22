import apiService from "./api";

class ConnectionService {

    async getConnections(workspaceId){
        const response = await apiService.get("genie/connections/" + workspaceId)
        return response
    }

    async getConnection(connectionId){
        const response = await apiService.get("genie/connection/" + connectionId)
        return response
    }

    async getConnectionTypes(){
        const response = await apiService.get("genie/connectiontypes")
        return response
    }

    async addConnection(payload, workspaceId){
        const response = await apiService.post("genie/connections/" + workspaceId, payload)
        return response
    }

    async updateConnection(connectionId, payload){
        const response = await apiService.put("genie/connection/" + connectionId, payload)
        return response
    }
    
    async deleteConnection(connectionId){
        const response = await apiService.delete("genie/connection/" + connectionId)
        return response
    }
}
let connectionService = new ConnectionService();
export default connectionService