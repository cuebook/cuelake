from rest_framework.views import APIView
from rest_framework.response import Response
from system.services import AccountSettingServices

class AccountSettingView(APIView):
    """
    Class to get and set account setting values
    """
    def get(self, request):
        res = AccountSettingServices.getAllAccountSettings()
        return Response(res.json())
    
    def post(self, request):
        key = request.data["key"]
        value = request.data["value"]
        res = AccountSettingServices.setAccountSetting(key=key, value=value)
        return Response(res.json())