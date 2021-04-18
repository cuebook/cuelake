import apiService from "./api";

class SettingsService {

    async getAccountSettings(){
        const response = await apiService.get("system/accountsettings")
        return response
    }

    async updateAccountSettings(accountsettings){
        const response = await apiService.post("system/accountsettings/", accountsettings)
        return response
    }
}
let settingsService = new SettingsService();
export default settingsService