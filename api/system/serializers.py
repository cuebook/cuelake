import json
from rest_framework import serializers
from system.models import AccountSetting

class AccountSettingSerializer(serializers.ModelSerializer):
    """
    Serializer for the model Account Setting
    """
    value = serializers.SerializerMethodField()
    
    def get_value(self, obj):
        """
        Gets account setting value
        """
        values = obj.accountsettingvalue_set.all()
        if len(values):
            return values[0].value
        else:
            return ""

    class Meta:
        model = AccountSetting
        fields = ["key", "label", "type", "value"]
