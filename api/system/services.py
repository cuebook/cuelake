import json
import requests
from system.models import AccountSetting, AccountSettingValue
from system.serializers import AccountSettingSerializer
from utils.apiResponse import ApiResponse
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

from .constants import ACCOUNT_SETTING_SLACK_URL_KEY, NOTIFY_ON_SUCCESS_KEY, NOTIFY_ON_FAILURE_KEY

class NotificationServices:
    """
    Class containing services related to notifications
    """
    @staticmethod
    def notify(notebookName: str, isSuccess: bool, message: str):
        """
        Service to send message to preconfigured slack channel
        :param message: Message to be sent to slack
        """
        try:
            slackWebHookUrl = AccountSetting.objects.get(key=ACCOUNT_SETTING_SLACK_URL_KEY).value
            isNotifyOnSuccess = AccountSetting.objects.get(key=NOTIFY_ON_SUCCESS_KEY).value == "true"
            isNotifyOnFailure = AccountSetting.objects.get(key=NOTIFY_ON_FAILURE_KEY).value == "true"
            if slackWebHookUrl:
                if (isNotifyOnFailure and not isSuccess) or (isNotifyOnSuccess and isSuccess):
                    NotificationServices.sendSlackNotification(slackWebHookUrl, notebookName, isSuccess, message)
        except:
            pass

    def sendSlackNotification(slackWebHookUrl: str, notebookName: str, isSuccess: bool, message: str):
        messageContent = {
            "text": "Job run for " + notebookName + " was " + ("successful" if isSuccess else "unsuccessful"),
            "blocks": [
    	    {
    		    "type": "section",
    		    "text": {
    			    "type": "mrkdwn",
    			    "text": "Notebook: *" + notebookName + "*"
    		    }
    	    },
            {
    		    "type": "section",
    		    "text": {
    			    "type": "mrkdwn",
    			    "text": "Status: *" + ("SUCCESS" if isSuccess else "ERROR") + "*"
    		    }
    	    },
            {
    		    "type": "section",
    		    "text": {
    			    "type": "mrkdwn",
    			    "text": "Message: " + message
    		    }
    	    }
            ]   
        }
        requests.post(slackWebHookUrl, data=json.dumps(messageContent))


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
        accountSettings = AccountSetting.objects.all()
        data = AccountSettingSerializer(accountSettings, many=True).data
        res.update(True, "Fetched account settings successfully", data)
        return res
    
    @staticmethod
    def updateAccountSettings(settings: list):
        """
        Service to set specified value of AccountSetting with specified key
        :param key: Key of the Account Setting
        :param value: Value to be set in the Account Setting
        """
        res = ApiResponse()
        for setting in settings:
            accountSetting = AccountSetting.objects.get(key=setting["key"])
            if len(accountSetting.accountsettingvalue_set.all()):
                accountSettingValue = accountSetting.accountsettingvalue_set.all()[0]
                accountSettingValue.value = setting["value"]
                accountSettingValue.save()
            else:
                AccountSettingValue.objects.create(accountSetting=accountSetting, value=setting["value"])
        res.update(True, "Updated account setting successfully")
        return res




