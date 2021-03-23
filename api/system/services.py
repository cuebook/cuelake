import json
import requests
from system.models import AccountSetting
from utils.apiResponse import ApiResponse

from .constants import ACCOUNT_SETTING_SLACK_URL_KEY

class NotificationServices:
    """
    Class containing services related to notifications
    """
    @staticmethod
    def notifyOnSlack(message: str):
        """
        Service to send message to preconfigured slack channel
        :param message: Message to be sent to slack
        """
        slackWebHookUrl = AccountSettingServices.getAccountSetting(key=ACCOUNT_SETTING_SLACK_URL_KEY).data
        if slackWebHookUrl:
            requests.post(slackWebHookUrl, data=json.dumps({"text": message}))

class AccountSettingServices:
    """
    Class containing services for getting and setting various AccountSetting values
    """
    @staticmethod
    def getAccountSetting(key: str):
        """
        Service to get the value of AccountSetting with specified key
        :param key: Key of the Account Setting
        """
        res = ApiResponse()
        try:
            value = AccountSetting.objects.get(key=key).value
            res.update(True, "Fetched account setting value successfully", value)
        except:
            res.update(False, "Error in fetching account setting value")
        return res

    @staticmethod
    def getAllAccountSettings():
        """
        Service to get keys and values of all AccountSettings
        """
        res = ApiResponse()
        data = list(AccountSetting.objects.all().values("key", "value"))
        res.update(True, "Fetched account settings successfully", data)
        return res
    
    @staticmethod
    def setAccountSetting(key: str, value: str):
        """
        Service to set specified value of AccountSetting with specified key
        :param key: Key of the Account Setting
        :param value: Value to be set in the Account Setting
        """
        res = ApiResponse()
        settingObj, _ = AccountSetting.objects.get_or_create(key=key)
        settingObj.value = value
        settingObj.save()
        res.update(True, "Updated account setting successfully")
        return res




