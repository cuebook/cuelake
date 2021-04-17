import apiService from "./api";

class ConnectionService {

    async getConnections(){
        const response = await apiService.get("connections")
        return response
    }

    async getConnection(connectionId){
        const response = await apiService.get("connection/" + connectionId)
        return response
    }

    async getConnectionTypes(){
        const response = await apiService.get("connectiontypes")
        return response
    }

    async addConnection(payload){
        const response = await apiService.post("connections", payload)
        return response
    }

    async updateConnection(connectionId, payload){
        const response = await apiService.put("connection/" + connectionId, payload)
        return response
    }
    
    async deleteConnection(connectionId){
        const response = await apiService.delete("connection/" + connectionId)
        return response
    }
}
let connectionService = new ConnectionService();
export default connectionService