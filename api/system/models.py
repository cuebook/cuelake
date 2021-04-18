from django.db import models

class AccountSetting(models.Model):
    """
    Model class to store account settings
    """
    key = models.CharField(max_length=200, blank=True, null=True)
    label = models.CharField(max_length=200, blank=True, null=True)
    value = models.TextField(blank=True)
    type = models.CharField(max_length=200, default="text") # bool / text / textarea

    def __str__(self) -> str:
        return self.key