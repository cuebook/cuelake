from django.db import models

class AccountSetting(models.Model):
    """
    Model class to store account settings
    """
    key = models.CharField(max_length=50)
    value = models.TextField()

    def __str__(self) -> str:
        return self.key