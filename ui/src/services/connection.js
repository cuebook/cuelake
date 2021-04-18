import apiService from "./api";

class ConnectionService {

    async getConnections(){
        const response = await apiService.get("genie/connections")
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

    async addConnection(payload){
        const response = await apiService.post("genie/connections", payload)
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